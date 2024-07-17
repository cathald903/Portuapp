"""
Definitions of all the app routes
"""
import random
from datetime import datetime
from flask import Blueprint, redirect, render_template, url_for, request, session, current_app
from flask_login import login_user, login_required, logout_user, current_user
from flask_paginate import Pagination
from app import db, bcrypt, login_manager
from app.database import save_answer
from app.config import current_datetime, datetime_format
from app.filters import build_query, get_filter_dict
from app.forms import QuestionSetupForm, QuestionForm, LoginForm, RegisterForm, ResultsForm
from app.models import Vocab, Verb, Answers, User, UserSubscription
from app.questions import get_questions


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


def check_quiz_finished(question_number, number_of_questions):
    if question_number >= number_of_questions-1:
        session.pop('question_dict')
        return True

    else:
        session['question_dict']['number'] += 1
        session.modified = True
        return False


@ main.route('/question_page', methods=['GET', 'POST'])
@login_required
def question_page():
    """

    """
    question_dict = session['question_dict']
    question_set = question_dict['question_set']
    question = question_set[question_dict['number']]
    form = QuestionForm()
    if form.validate_on_submit():
        save_answer(request.form.get('answer').lower(),
                    request.form.get('context_answer', 'n/a'))
        if check_quiz_finished(question_dict['number'], len(question_set)):
            filter_time = datetime.strptime(
                question_dict['datetime_id'], datetime_format)
            session['filter_dict'] = {'start_date': filter_time,
                                      'end_date': filter_time,
                                      'word_filter': 'All',
                                      'correct_filter': 'None'}
            return redirect(url_for('main.get_answers'))

    form.question.label = question['question']
    form.context_question.label = question.get('context_question')
    form.quiz_on_conjugation.data = question_dict.get(
        'quiz_on_conjugation', 'No')
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
        session['question_dict'] = {
            'datetime_id': current_datetime('string'),
            'number': 0,
            'question_set': get_questions(int(request.form.get(
                'num_of_questions')), request.form.get('quiz_area')),
            'quiz_on_context': request.form.get('context', ''),
            'quiz_on_conjugation': request.form.get('verb_conjugation', 'No')}
        return redirect(url_for('main.question_page'))
    return render_template('question_setup.html', title='Quiz', form=setup_form)


@ main.route('/profile')
@ login_required
def profile():
    return render_template('profile.html', user=current_user)


@ main.route('/debug')
def debug():
    break_here


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
