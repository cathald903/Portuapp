"""
Contains the functions for saving the data to the DB and
Csv load/save functions for local development purposes
"""
import csv
import os
from flask import session
from flask_login import current_user
from sqlalchemy import exc
from app import db
from app.models import Answers, UserSubscription, User, Verb, Vocab


def get_csv_file(name) -> list:
    """
    Simple csv loader that returns the given file as a list
    """
    with open(name, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        return [row for row in reader]


def commit_to_database(data: object):
    """
    Commits to database, rollbacks if there is an IntegrityError
    """
    try:
        db.session.add(data)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()


def import_from_csv(file: str, obj: object):
    """
    Function used for local development to import data into the db
    """
    data = get_csv_file(file)
    for row in data:
        commit_to_database(obj(row))


def format_answer(datetime_id, question, user_answer, user_context, user_conjugation):
    """
    Formats the fields into the order/values expected by the Answers Model
    """
    user_object = User.query.filter_by(id=current_user.id).first()
    id_ = "_".join([user_object.username, datetime_id, question['id']])
    correct = str(question['answer'].lower() == user_answer.lower())
    context = question.get('context_answer', 'n/a')
    context_correct = str(context.lower() == user_context.lower())
    conjugation_correct = user_conjugation
    return [id_, current_user.id, question['id'], datetime_id, question['question'],
            user_answer, correct, context, context_correct, conjugation_correct]


def save_answer(user_answer, user_context, user_conjugation):
    """
    Retrieves session data to get the necessary fields for saving it
    to csv and to the database
    """
    question_dict = session['question_dict']
    question = question_dict['question_set'][question_dict['number']]
    datetime_id = question_dict['datetime_id']

    data = format_answer(datetime_id, question, user_answer,
                         user_context, user_conjugation)
    answer_obj = Answers(data)
    commit_to_database(answer_obj)
    append_to_csv(os.getenv('ANSWER_FILE'),
                  data)


def append_to_csv(filename, data):
    """
    Writes the given data to a newline in the given file
    """
    with open(filename, 'a', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(data)


def init_db():
    """
    Creates the databases's tables if they don't already exist and when running in the test
    environment will populate them with data from the given csvs.
    """
    db.create_all()
    if os.getenv('ENVIRONMENT') == 'Test':
        import_from_csv(os.getenv('VOCAB_FILE'), Vocab)
        import_from_csv(os.getenv('VERB_FILE'), Verb)
        import_from_csv(os.getenv('ANSWER_FILE'), Answers)
        import_from_csv(os.getenv('USERSUB_FILE'), UserSubscription)
