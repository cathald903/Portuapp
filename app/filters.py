"""
Contains the code for the simple filters on the table dispalyed on the Answer History page
"""
from flask import session
from app.config import current_datetime
from app.models import Answers


def build_query(results_form, query):
    """
    Decides which filter commands need to be appended to the given query depending on the
    form's values and returns the query with these changes.
    """
    start_date = results_form.date_start_filter.data
    end_date = results_form.date_end_filter.data
    if start_date:
        query = query.filter(
            Answers.date >= start_date)
    if end_date and end_date != start_date:
        query = query.filter(
            Answers.date <= end_date)

    if not results_form.word_filter.data == 'All':
        query = query.filter(
            Answers.word_id == results_form.word_filter.data)
    if not results_form.correct_filter.data == 'None':
        query = query.filter(
            Answers.correct == {"True": True, "False": False}[results_form.correct_filter.data])
    return query


def get_filter_dict():
    """
    Quick function to return the filter dictionary or create a default one if it doesn't exist
    """
    if session.get('filter_dict'):
        return session.get('filter_dict')

    return {'start_date': current_datetime('datetime'),
            'end_date': current_datetime('datetime'),
            'word_filter': 'All',
            'correct_filter': 'None'}
