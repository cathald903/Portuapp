"""
Contains simple functions used by the routes in routes.py
"""
from datetime import datetime
from flask import redirect, session, url_for, flash
from flask_login import current_user
from app import db
from app.config import DATETIME_FORMAT
from app.models import UserSubscription, Verb, Vocab


def check_quiz_finished(question_number, number_of_questions):
    """
    Checks if the number of questions is = current question number and
    returns whether the quiz has finished or not
    """
    if question_number >= number_of_questions-1:
        session.pop('question_dict')
        return True

    else:
        session['question_dict']['number'] += 1
        session.modified = True
        return False


def redirect_to_answer_page(question_dict):
    """
    redirects the user to the answer page with filters for their most recent
    quiz session
    """
    filter_time = datetime.strptime(
        question_dict['datetime_id'], DATETIME_FORMAT)
    session['filter_dict'] = {'start_date': filter_time,
                              'end_date': filter_time,
                              'word_filter': 'All',
                              'correct_filter': 'None'}
    return redirect(url_for('main.get_answers'))


def validate_conjugation(form, word_id):
    """
    Checks whether the user's inputted conjugation answers match the expected values
    in our database
    """
    if form.tense.data == 'Past':
        tense = Verb.past
    elif form.tense.data == 'Present':
        tense = Verb.present
    else:
        tense = Verb.future
    correct_conjugation = Verb.query.filter_by(
        id=word_id).with_entities(tense).first()[0].split(" ")
    res = [entry[0] == entry[1] for entry in list(
        zip(correct_conjugation, list(form.data.values())[:6]))]
    return str(all(res))


def slashify(toslash: str):
    """
    replaces / with slashify in order to avoid flask thinking that slashes
    in the word are paths. eg Fazer = To make/do
    """
    return toslash.lower().replace(
        "/", " slashify ")


def get_pagination_urls(func: str, obj: object, kind: str = None):
    """
    Returns the previous and next urls for the paginated object
    """
    if kind:
        next_url = url_for(
            func, page=obj.next_num, kind=kind) if obj.has_next else None
        prev_url = url_for(
            func, page=obj.prev_num, kind=kind) if obj.has_prev else None
    else:
        next_url = url_for(
            func, page=obj.next_num) if obj.has_next else None
        prev_url = url_for(
            func, page=obj.prev_num) if obj.has_prev else None
    return [next_url, prev_url]


def get_user_subscriptions(obj, user_id):
    """
    Gets the given users subscriptions
    """
    subs = db.session.query(obj.id, obj.english, obj.portuguese, UserSubscription.word).outerjoin(
        UserSubscription,
        (obj.id == UserSubscription.word)
        & (UserSubscription.user_id == user_id))

    return subs


def subscribe(word: str, kind: str, user_id: int):
    """
    Subscribes a user to a word
    """
    sub = UserSubscription(word=word, kind=kind,
                           user_id=user_id)
    db.session.add(sub)
    db.session.commit()


def subscribe_to_all(kind):
    """
    Subscribes user to every Verb or Vocab they are not currently subscribed
    to.
    """
    obj = Verb if kind == 'verb' else Vocab
    for q in get_user_subscriptions(obj, current_user.id).filter(
            UserSubscription.word.is_(None)).all():
        subscribe(q[0], kind, current_user.id)
    flash('Subscribed to Everything!')
