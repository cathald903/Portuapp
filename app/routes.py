"""
Definitions of all the app routes
"""
import random
import urllib.parse
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, url_for, request, session, current_app
from flask_login import login_user, login_required, logout_user, current_user
from flask_paginate import Pagination
from app import db, bcrypt, login_manager
from app.database import save_answer
from app.config import current_datetime, datetime_format
from app.filters import build_query, get_filter_dict
from app.forms import QuestionSetupForm, QuestionForm, LoginForm, RegisterForm, ResultsForm, ConjugationForm
from app.models import Vocab, Verb, Answers, User, UserSubscription
from app.questions import get_questions
from app.route_functions import check_quiz_finished, validate_conjugation, redirect_to_answer_page

main = Blueprint('main', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
##############################
###       Routes           ###
##############################


@ main.route('/')
@login_required
def homepage():
    """

    """
    with current_app.app_context():
        if random.randint(0, 1):
            random_word = random.choice(Vocab.query.all()).__dict__
        else:
            random_word = random.choice(Verb.query.all()).__dict__
        return render_template('home.html', title='Home', word=random_word, user=current_user)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                try:
                    login_user(user)
                    return redirect(url_for('main.homepage'))
                except:
                    form.password.errors = ["Invalid Password name"]
                    return render_template('login.html', form=form)
        else:
            form.username.errors = ["Invalid User name"]
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@main.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@ main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)


@ main.route('/conjugate/<word_id>/<user_answer>/<context>', methods=['GET', 'POST'])
def conjugate(word_id: str, user_answer: str, context: str):
    word_id = word_id.replace(" slashify ", "/")
    user_answer = user_answer.replace(" slashify ", "/")
    context = context.replace(" slashify ", "/")
    question_dict = session['question_dict']
    question_set = question_dict['question_set']
    form = ConjugationForm()
    form.tense.data = question_dict.get('quiz_on_conjugation')
    if form.validate_on_submit():
        save_answer(user_answer,
                    context,
                    validate_conjugation(form, question_set[question_dict['number']]['word_id']))
        if check_quiz_finished(question_dict['number'], len(question_set)):
            return redirect_to_answer_page(question_dict)
        else:
            return redirect(url_for('main.question_page'))
    return render_template('conjugation.html', form=form, word_id=word_id, tense=question_dict.get('quiz_on_conjugation').lower())


@ main.route('/question_page', methods=['GET', 'POST'])
@ login_required
def question_page():
    """

    """
    question_dict = session['question_dict']
    question_set = question_dict['question_set']
    question = question_set[question_dict['number']]
    form = QuestionForm()
    if form.validate_on_submit():
        if question_dict.get('quiz_on_conjugation', 'No') != 'No' and question['kind'] != 'Vocab':
            encoded_word_id = question['word_id'].lower().replace(
                "/", " slashify ")
            encoded_user_answer = request.form.get(
                'answer').lower().replace("/", " slashify ")
            encoded_context = request.form.get(
                'context_answer', 'n/a').replace("/", " slashify ")
            return redirect(url_for('main.conjugate', word_id=encoded_word_id, user_answer=encoded_user_answer, context=encoded_context))
        else:
            save_answer(request.form.get('answer').lower(),
                        request.form.get('context_answer', 'n/a'),
                        'True')
        if check_quiz_finished(question_dict['number'], len(question_set)):
            return redirect_to_answer_page(question_dict)
        else:
            question = question_set[question_dict['number']]

    form.question.label = question['question']
    form.context_question.label = question.get('context_question')
    form.answer.data = None
    return render_template('question.html', title='Quiz Time', form=form,
                           quiz_on_context=len(question.get('context_answer', '')) > 0)


@ main.route('/quiz', methods=['GET', 'POST'])
@ login_required
def quiz():
    """

    """
    setup_form = QuestionSetupForm()
    if setup_form.validate_on_submit():
        question_set = get_questions(int(request.form.get(
            'num_of_questions')), request.form.get('quiz_area'))
        if len(question_set) == 0:
            flash('Subscribe to some words first!')
            return redirect(url_for('main.profile'))
        session['question_dict'] = {
            'datetime_id': current_datetime('string'),
            'number': 0,
            'question_set': question_set,
            'quiz_on_context': request.form.get('context', ''),
            'quiz_on_conjugation': request.form.get('verb_conjugation', 'No')}
        return redirect(url_for('main.question_page'))
    return render_template('question_setup.html', title='Quiz', form=setup_form)


@ main.route('/profile')
@ login_required
def profile():
    sub = db.session.query(UserSubscription).filter_by(
        user_id=current_user.id).all()
    return render_template('profile.html', subs=sub)


@ main.route('/profile/subscription/<kind>', methods=['GET', 'POST'])
@ login_required
def subscription(kind: str):
    page = request.args.get('page', 1, type=int)
    per_page = 20
    if kind == 'verb':
        obj = Verb
    else:
        obj = Vocab
    subs = db.session.query(obj.id, obj.english, obj.portuguese, UserSubscription.word).outerjoin(
        UserSubscription, (obj.id == UserSubscription.word)
        & (UserSubscription.user_id == current_user.id)).paginate(page=page, per_page=per_page, error_out=False)
    next_url = url_for(
        'main.subscription', page=subs.next_num, kind=kind) if subs.has_next else None
    prev_url = url_for(
        'main.subscription', page=subs.prev_num, kind=kind) if subs.has_prev else None
    return render_template('subscription.html', sub=subs.items, next_url=next_url, prev_url=prev_url, kind=kind)


@ main.route('/subscription_manager', methods=['GET', 'POST'])
@ login_required
def subscription_manager():
    word_id = request.form.get('word_id')
    subscribed = request.form.get('subscribed') == 'true'
    kind = request.form.get('kind')
    if word_id == 'all':
        if kind == 'verb':
            obj = Verb
        else:
            obj = Vocab
        for q in db.session.query(obj.id).outerjoin(UserSubscription, (obj.id == UserSubscription.word) & (UserSubscription.user_id == current_user.id)).filter(
                UserSubscription.word.is_(None)).all():
            sub = UserSubscription(word=q[0], kind=kind,
                                   user_id=current_user.id)
            db.session.add(sub)
            db.session.commit()
    try:
        if subscribed:
            sub = UserSubscription(word=word_id, kind=kind,
                                   user_id=current_user.id)
            db.session.add(sub)
            db.session.commit()
            flash('Subscription updated!')
        else:
            sub = db.session.query(UserSubscription).filter_by(
                word=word_id, user_id=current_user.id).first()
            db.session.delete(sub)
            db.session.commit()
            flash('Subscription deleted!')
        return {'success': True}
    except:
        return {'success': False}


@ main.route('/debug')
def debug():
    break_here


# @ main.route('/test')
# @ login_required
# def test():
#     form = TestForm()
#     return render_template('test.html', form=form)


@ main.route('/show_answers/', methods=['GET', 'POST'])
@ login_required
def get_answers():
    filter_dict = get_filter_dict()
    results_form = ResultsForm(
        date_start_filter=filter_dict['start_date'],
        date_end_filter=filter_dict['end_date'],
        word_filter=filter_dict['word_filter'],
        correct_filter=filter_dict['correct_filter']
    )
    page = request.args.get('page', 1, type=int)
    per_page = 20
    query = Answers.query.filter_by(user_id=current_user.id)
    results_form.word_filter.choices += [x[0] for x in query.with_entities(
        Answers.word_id).distinct().order_by(Answers.word_id).all()]
    valid = results_form.validate_on_submit()
    errors = len(results_form.errors) > 0
    if errors:
        return render_template('results.html', answers=[], form=results_form)
    if valid:
        session['filter_dict'] = {'start_date': results_form.date_start_filter.data,
                                  'end_date': results_form.date_end_filter.data,
                                  'word_filter': results_form.word_filter.data,
                                  'correct_filter': results_form.correct_filter.data}

    ans = db.paginate(build_query(results_form, query), page=page,
                      per_page=per_page, error_out=False)

    next_url = url_for(
        'main.get_answers', page=ans.next_num) if ans.has_next else None
    prev_url = url_for(
        'main.get_answers', page=ans.prev_num) if ans.has_prev else None
    return render_template('results.html', answers=ans.items, form=results_form, next_url=next_url, prev_url=prev_url)
