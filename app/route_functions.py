from datetime import datetime
from flask import redirect, session, url_for
from app.config import datetime_format
from app.models import Verb


def check_quiz_finished(question_number, number_of_questions):
    if question_number >= number_of_questions-1:
        session.pop('question_dict')
        return True

    else:
        session['question_dict']['number'] += 1
        session.modified = True
        return False


def redirect_to_answer_page(question_dict):
    filter_time = datetime.strptime(
        question_dict['datetime_id'], datetime_format)
    session['filter_dict'] = {'start_date': filter_time,
                              'end_date': filter_time,
                              'word_filter': 'All',
                              'correct_filter': 'None'}
    return redirect(url_for('main.get_answers'))


def validate_conjugation(form, word_id):

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
