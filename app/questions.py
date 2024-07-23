"""
Contains the logic for deriving questions for the user
"""
import random
from flask_login import current_user
from sqlalchemy import func
from app import db
from app.models import Verb, Vocab, UserSubscription


def format_question(row_dict: dict, kind: str) -> None:
    """
    Generates question based on whether word being tested is in English or Portuguese 
    """
    langs = ['Portuguese', 'English']
    random.shuffle(langs)
    trans_to, trans_from = langs
    context = row_dict.get('context', '')
    if trans_from == 'English' and context:
        question_context = f"({context})"
    else:
        question_context = ''
    question_dict = {
        "question": f"What is the {trans_to} of {row_dict[trans_from.lower()]}{question_context}?",
        "answer": row_dict[trans_to.lower()].split(' (')[0],
        "id": row_dict['id']}
    if trans_to == 'English' and context:
        question_dict['context_question'] = "In what context?"
        question_dict['context_answer'] = context
    question_dict['kind'] = kind
    question_dict['word_id'] = row_dict.get('id')
    return question_dict


def get_word_ending(question_dict: dict) -> str:
    """
    Checks what endings are available for the word and chooses 1 to append
    """
    m, f = question_dict['masculine'], question_dict['feminine']
    if m and f:
        return random.choice(['masculine', 'feminine'])
    if m:
        return 'masculine'
    if f:
        return 'feminine'
    return ''


def compose_word(question_dict: dict, kind: str) -> dict:
    """
    Chooses what the of the word gender will be asked
    """
    if kind == 'Verbs':
        return question_dict
    ending = get_word_ending(question_dict)
    if ending:
        question_dict['english'] = f"{question_dict['english']} ({ending})"
        question_dict['portuguese'] = f"{question_dict['portuguese']}{question_dict[ending]}"
    return question_dict


def get_question(number: int, kind: str):
    """
    Returns the requested number of questions from the database depending on the user's request
    """
    if number == 0:
        return []
    elif kind == 'Vocab':
        obj = Vocab
    elif kind == 'Verbs':
        obj = Verb
    query = db.session.query(obj).join(UserSubscription, (obj.id == UserSubscription.word) & (
        UserSubscription.user_id == current_user.id)).order_by(func.random()).limit(number)
    questions = [format_question(compose_word(
        q.__dict__, kind), kind) for q in query]
    return questions


def get_questions_set(number: int, kind: str) -> str:
    """
    Returns a random shuffle of the requested number of questions by type
    """
    if kind == 'Vocab':
        questions = get_question(number, kind)
    elif kind == 'Verbs':
        questions = get_question(number, kind)
    else:
        random_choices = [random.choice(['vocab', 'verb'])
                          for _ in range(number)]
        questions = get_question(random_choices.count('vocab'), 'Vocab')
        questions.extend(get_question(random_choices.count('verb'), 'Verbs'))
        random.shuffle(questions)
    return questions
