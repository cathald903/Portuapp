"""
Definitions of all the app routes
"""
import random
from flask import Blueprint, flash, redirect, render_template, url_for, request, session
from flask_login import login_user, login_required, logout_user, current_user
from app import db, bcrypt, login_manager
from app.database import save_answer
from app.config import current_datetime
from app.filters import build_query, get_filter_dict
from app.forms import QuestionSetupForm, QuestionForm, LoginForm, RegisterForm, FilterForm
from app.forms import ConjugationForm
from app.models import Vocab, Verb, Answers, User, UserSubscription
from app.questions import get_questions_set
from app.route_functions import check_quiz_finished, get_pagination_urls, get_user_subscriptions
from app.route_functions import redirect_to_answer_page, slashify, subscribe, subscribe_to_all
from app.route_functions import validate_conjugation

main = Blueprint('main', __name__)
PER_PAGE = 20


@login_manager.user_loader
def load_user(user_id):
    """
    Loader func for logging in
    """
    return User.query.get(int(user_id))
##############################
###       Routes           ###
##############################


@ main.route('/')
@login_required
def homepage():
    """
    Welcome page that shows a random word for the database
    """
    if random.randint(0, 1):
        random_word = random.choice(Vocab.query.all()).__dict__
    else:
        random_word = random.choice(Verb.query.all()).__dict__
    return render_template('home.html', title='Home', word=random_word, user=current_user)


@main.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('main.homepage'))
            else:
                form.password.errors = "Invalid Password name"
                return render_template('login.html', form=form)
        else:
            form.username.errors = "Invalid User name"
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@main.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """
    Logs the user out
    """
    logout_user()
    return redirect(url_for('main.login'))


@ main.route('/register', methods=['GET', 'POST'])
def register():
    """
    Allows a new user to register their login info
    """
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
    """
    Displays the form for verb conjugation and validates the user answers on submit then checks to 
    see if the quiz is finished before redirecting to the answer page for the session or to the quiz
    page for the next question
    """
    word_id = word_id.replace(" slashify ", "/")
    user_answer = user_answer.replace(" slashify ", "/")
    context = context.replace(" slashify ", "/")
    question_dict = session['question_dict']
    question_set = question_dict['question_set']
    form = ConjugationForm()
    form.tense.data = question_dict.get('quiz_on_conjugation').lower()
    if form.validate_on_submit():
        save_answer(user_answer,
                    context,
                    validate_conjugation(form, question_set[question_dict['number']]['word_id']))
        if check_quiz_finished(question_dict['number'], len(question_set)):
            return redirect_to_answer_page(question_dict)
        else:
            return redirect(url_for('main.question_page'))
    return render_template('conjugation.html', form=form, word_id=word_id, tense=form.tense.data)


@ main.route('/question_page', methods=['GET', 'POST'])
@ login_required
def question_page():
    """
    Creates and displays the form for the user depending on what question areas they've selected
    then checks if the quiz is over and displays either the answer page or the next question
    """
    question_dict = session['question_dict']
    question_set = question_dict['question_set']
    question = question_set[question_dict['number']]
    form = QuestionForm()
    if form.validate_on_submit():
        if question_dict.get('quiz_on_conjugation', 'No') != 'No' and question['kind'] != 'Vocab':
            word_id = slashify(question['word_id'])
            user_answer = slashify(request.form.get('answer'))
            context = slashify(request.form.get('context_answer', 'n/a'))
            return redirect(url_for('main.conjugate', word_id=word_id,
                                    user_answer=user_answer, context=context))
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
    Asks the user for which areas they want to be tested on and creates the session dictionary
    for this quiz round
    """
    setup_form = QuestionSetupForm()
    if setup_form.validate_on_submit():
        question_set = get_questions_set(int(request.form.get(
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
    """
    Displays the landing profile page which shows a paginated view of what the user is 
    subscribed to 
    """
    page = request.args.get('page', 1, type=int)
    sub = db.session.query(UserSubscription).filter_by(
        user_id=current_user.id).paginate(page=page, per_page=PER_PAGE, error_out=False)

    next_url, prev_url = get_pagination_urls('main.profile', sub)
    return render_template('profile.html', subs=sub, next_url=next_url, prev_url=prev_url)


@ main.route('/profile/subscription/<kind>', methods=['GET', 'POST'])
@ login_required
def subscription(kind: str):
    """
    Shows a paginated view of the subscription page for either Verbs or Vocab and allows
    the user to click a checkbox to sub/unsub to the displayed word
    """
    page = request.args.get('page', 1, type=int)
    obj = Verb if kind == 'verb' else Vocab
    subs = get_user_subscriptions(obj, current_user.id).paginate(page=page, per_page=PER_PAGE,
                                                                 error_out=False)
    next_url, prev_url = get_pagination_urls('main.subscription', subs, kind)
    return render_template('subscription.html', sub=subs.items, next_url=next_url,
                           prev_url=prev_url, kind=kind)


@ main.route('/subscription_manager', methods=['GET', 'POST'])
@ login_required
def subscription_manager():
    """
    Performs the action requested, either sub or unsub and returns a response to the 
    user
    """
    word_id = request.form.get('word_id')
    to_subscribe = request.form.get('to_subscribe') == 'true'
    kind = request.form.get('kind')
    if word_id == 'all':
        subscribe_to_all(kind)
        return {'success': True}
    if to_subscribe:
        subscribe(word_id, kind, current_user.id)
        flash('Subscription updated!')
    else:
        sub = db.session.query(UserSubscription).filter_by(
            word=word_id, user_id=current_user.id).first()
        db.session.delete(sub)
        db.session.commit()
        flash('Subscription deleted!')
    return {'success': True}


@ main.route('/show_answers/', methods=['GET', 'POST'])
@ login_required
def get_answers():
    """
    Displays the history of the the User's answers and allows them to 
    filter (simply) over time, correctness or by certain words
    """
    filter_dict = get_filter_dict()
    results_form = FilterForm(
        date_start_filter=filter_dict['start_date'],
        date_end_filter=filter_dict['end_date'],
        word_filter=filter_dict['word_filter'],
        correct_filter=filter_dict['correct_filter']
    )
    page = request.args.get('page', 1, type=int)
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
                      per_page=PER_PAGE, error_out=False)
    next_url, prev_url = get_pagination_urls('main.get_answers', ans)
    return render_template('results.html', answers=ans.items, form=results_form, next_url=next_url, prev_url=prev_url)
