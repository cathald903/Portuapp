"""
Connects to the db for import into the other modules
"""
import csv
from flask import session
from flask_login import current_user
import os
from app import db, bcrypt
from app.models import Answers


def get_csv_file(name) -> list:
    with open(name, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        return [row for row in reader]


def import_from_csv(file: str, obj: object):
    data = get_csv_file(file)
    # try except so we skip over primary key duplicate error when the container hasn't been cleared
    for row in data:
        try:
            db.session.add(obj(row, True))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)


def save_answer_to_database(user_id, question_id, datetime_id, question, correct_answer, user_answer, correct_context, user_context, user_conjugation):
    answer_obj = Answers([user_id, question_id, datetime_id, question,
                         correct_answer, user_answer, correct_context, user_context, user_conjugation])
    db.session.add(answer_obj)
    db.session.commit()
    return answer_obj


def save_answer_to_csv(answer_id, user_id, question_id, date, question, given_answer, correct, context_answer, context_correct, user_conjugation):
    try:
        append_to_csv(os.getenv('ANSWER_FILE'), (answer_id, user_id, question_id, date,
                                                 question, given_answer, correct, context_answer, context_correct, user_conjugation))
    except:
        print(f"unable to write row to {os.getenv('ANSWER_FILE')}")


def save_answer(user_answer, user_context, user_conjugation):
    question_dict = session['question_dict']
    question = question_dict['question_set'][question_dict['number']]
    datetime_id = question_dict['datetime_id']
    correct_answer = question['answer'].lower()
    correct_context = question.get('context_answer', 'n/a')
    answer_obj = save_answer_to_database(current_user.id,
                                         question['id'], datetime_id, question['question'],
                                         correct_answer, user_answer,
                                         correct_context, user_context, user_conjugation)
    save_answer_to_csv(answer_obj.id, current_user.id, question['id'], datetime_id,
                       question['question'], user_answer, answer_obj.correct,
                       correct_context, answer_obj.context_correct, user_conjugation)


def append_to_csv(filename, data):
    with open(filename, 'a', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(data)


def init_db():
    from app.models import Vocab, Verb, Answers, User, UserSubscription
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        db.create_all()
        import_from_csv(os.getenv('VOCAB_FILE'), Vocab)
        import_from_csv(os.getenv('VERB_FILE'), Verb)
        ##### just because of testing and constant wiping of user data #####
        if len(User.query.filter_by(username='Cathal').all()) == 0:
            hashed_password = bcrypt.generate_password_hash('12341234')
            new_user = User(username='Cathal', password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
        import_from_csv(os.getenv('ANSWER_FILE'), Answers)
        import_from_csv(os.getenv('USERSUB_FILE'), UserSubscription)
