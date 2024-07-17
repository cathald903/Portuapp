from app.config import current_datetime
from app.models import Answers
from flask import session


def build_query(results_form, query):
    if results_form.date_start_filter.data:
        query = query.filter(
            Answers.date >= results_form.date_start_filter.data)
    if results_form.date_end_filter.data and results_form.date_end_filter.data != results_form.date_start_filter.data:
        query = query.filter(
            Answers.date <= results_form.date_end_filter.data)

    if not results_form.word_filter.data == 'All':
        query = query.filter(
            Answers.word_id == results_form.word_filter.data)
    if not results_form.correct_filter.data == 'None':
        query = query.filter(
            Answers.correct == {"True": True, "False": False}[results_form.correct_filter.data])
    return query


def get_filter_dict():
    if session.get('filter_dict'):
        return session.get('filter_dict')

    return {'start_date': current_datetime('datetime'),
            'end_date': current_datetime('datetime'),
            'word_filter': 'All',
            'correct_filter': 'None'}
