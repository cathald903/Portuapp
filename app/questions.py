from app.models import Vocab, Verb
from sqlalchemy import func
import random


def format_question(row_dict: dict) -> None:
    """
    Generates question based on whether word being tested is in English or Portuguese 
    """
    langs = ['Portuguese', 'English']
    random.shuffle(langs)
    translate_to, translate_from = langs
    context = row_dict.get('context', '')
    if translate_from == 'English' and context:
        question_context = f"({context})"
    else:
        question_context = ''
    question_dict = {
        "question": f"What is the {translate_to} of {row_dict[translate_from.lower()]}{question_context}?",
        "answer": row_dict[translate_to.lower()].split(' (')[0],
        "id": row_dict['id']}
    if translate_to == 'English' and context:
        question_dict['context_question'] = "In what context?"
        question_dict['context_answer'] = context
    return question_dict


def get_word_ending(question_dict: dict) -> str:
    m, f = question_dict['masculine'], question_dict['feminine']
    if m and f:
        return random.choice(['masculine', 'feminine'])
    if m:
        return 'masculine'
    if f:
        return 'feminine'
    return ''


def compose_word(question_dict: dict) -> dict:
    """
    Chooses what gender type of the word we will ask for this word
    """
    ending = get_word_ending(question_dict)
    if ending:
        question_dict['english'] = f"{question_dict['english']} ({ending})"
        question_dict['portuguese'] = f"{question_dict['portuguese']}{question_dict[ending]}"
    return question_dict


def get_vocab_question(number: int):
    if number == 0:
        return []
    questions = [compose_word(q.__dict__) for q in Vocab.query.order_by(
        func.random()).limit(number)]
    return [format_question(q) for q in questions]


def get_verb_question(number: int):
    if number == 0:
        return []
    return [format_question(q.__dict__) for q in Verb.query.order_by(
        func.random()).limit(number)]


def get_questions_set(number: int, kind: str) -> str:
    if kind == 'Vocab':
        questions = get_vocab_question(number)
    elif kind == 'Verbs':
        questions = get_verb_question(number)
    else:
        random_choices = [random.choice(['vocab', 'verb'])
                          for _ in range(number)]
        questions = get_vocab_question(random_choices.count('vocab'))
        questions.extend(get_verb_question(random_choices.count('verb')))
        random.shuffle(questions)
    return questions


def get_questions(number: int, kind: str = 'mixed') -> str:
    return get_questions_set(number, kind)
