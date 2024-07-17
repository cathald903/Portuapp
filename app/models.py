from dataclasses import dataclass
from flask_login import UserMixin
from app import db


def get_present_tense_endings(ending):
    endings = {'er': ('o', 'es', 'e', 'emos', 'eis', 'em'),
               'ar': ('o', 'as', 'a', 'amos', 'ais', 'am'),
               'ir': ('o', 'es', 'e', 'imos', 'is', 'em')}
    return endings[ending]


def add_conjugation(portu, tense) -> str:
    v = portu
    ending = v[-2:]  # Verb type eg er,ar,ir
    root = v[:-2]
    if tense == 'past':
        return " "  # .join(
        # [root + ending for ending in PAST_TENSE[ending]])
    elif tense == 'present':
        return " ".join(
            [root + ending for ending in get_present_tense_endings(ending)])
    else:
        return " "  # .join(
        # [root + ending for ending in FUTURE_TENSE[ending]])


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(20), nullable=False, unique=True)
    password: str = db.Column(db.String(80), nullable=False)
    answers = db.relationship('Answers', backref='user', lazy=True)
    subscriptions = db.relationship(
        'UserSubscription', backref='user', lazy=True)

    def __repr__(self):
        return f"""<id {self.id!r},
                    username {self.username!r},
                    answers {self.answers!r},
                    subscriptions {self.subscriptions!r}>"""


class UserSubscription(db.Model):
    __tablename__ = 'user_subscriptions'
    word: str = db.Column(db.String(41), primary_key=True)
    kind: str = db.Column(db.String(6), nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False)

    def __repr__(self):
        return f"""<word {self.word!r},
                    kind {self.kind!r},
                    user {self.user_id!r}>"""


@dataclass
class Vocab(db.Model):
    __tablename__ = 'vocab'
    id: str = db.Column(db.String(41), primary_key=True)
    english: str = db.Column(db.String(20), nullable=False)
    portuguese: str = db.Column(db.String(20), nullable=False)
    masculine: str = db.Column(db.String(20), nullable=True)
    feminine: str = db.Column(db.String(20), nullable=False)
    article: str = db.Column(db.String(20), nullable=False)
    batch: int = db.Column(db.Integer, nullable=False)

    def __init__(self, inputs: list, from_csv: bool = False):
        if from_csv:
            self.append_from_csv(*inputs)
        else:
            self.append_from_app(*inputs)

    def append_from_csv(self, eng: str, portu: str, m: str, f: str, article: str, batch: str):
        self.id = "_".join([x.replace(" ", "_") for x in [eng, portu]]).lower()
        self.english = eng
        self.portuguese = portu
        self.masculine = m
        self.feminine = f
        self.article = article
        self.batch = batch

    def append_from_app(self, eng: str, portu: str, m: str, f: str, article: str, batch: str):
        self.id = "_".join([x.replace(" ", "_") for x in [eng, portu]]).lower()
        self.english = eng
        self.portuguese = portu
        self.masculine = m
        self.feminine = f
        self.article = article
        self.batch = batch

    def __repr__(self):
        return f"""<id {self.id!r},
                    english {self.english!r},
                    portuguese {self.portuguese!r},
                    masculine {self.masculine!r},
                    feminine {self.feminine!r},
                    article {self.article!r},
                    batch {self.batch!r}
                    >"""


@dataclass
class Verb(db.Model):
    __tablename__ = 'verb'
    id: str = db.Column(db.String(41), primary_key=True)
    english: str = db.Column(db.String(20), nullable=False)
    portuguese: str = db.Column(db.String(20), nullable=False)
    kind: str = db.Column(db.String(20), nullable=False)
    batch: int = db.Column(db.Integer, nullable=False)
    context: str = db.Column(db.String(20), nullable=False)
    past: str = db.Column(db.String(200), nullable=False)
    present: str = db.Column(db.String(200), nullable=False)
    future: str = db.Column(db.String(200), nullable=False)

    def __init__(self, inputs: list, from_csv: bool = False):
        if from_csv:
            self.append_from_csv(*inputs)
        else:
            self.append_from_app(*inputs)

    def append_from_csv(self, eng: str, portu: str, kind: str, batch: str,
                        context: str, past: str, present: str, future: str):
        self.id = "_".join([x.replace(" ", "_") for x in [eng, portu]]).lower()
        self.english = eng
        self.portuguese = portu
        self.kind = kind
        self.batch = batch
        self.context = context
        self.past = past
        if kind == 'Regular':
            self.present = add_conjugation(portu, 'present')
        else:
            self.present = present
        self.future = future

    def append_from_app(self, eng: str, portu: str, kind: str, batch: str,
                        context: str, past: str, present: str, future: str):
        self.id = "_".join([x.replace(" ", "_") for x in [eng, portu]]).lower()
        self.english = eng
        self.portuguese = portu
        self.kind = kind
        self.batch = batch
        self.context = context
        self.past = past
        if kind == 'Regular':
            self.present = add_conjugation(portu, 'present')
        else:
            self.present = present
        self.future = future

    def __repr__(self):
        return f"""<id {self.id!r},
                    english {self.english!r},
                    portuguese {self.portuguese!r},
                    kind {self.kind!r}
                    batch {self.batch!r},
                    context {self.context!r},
                    past {self.past!r},
                    present {self.present!r},
                    future {self.future!r}
                    >"""


@dataclass
class Answers(db.Model):
    __tablename__ = 'answer'
    id: str = db.Column(db.String(81), primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False)
    word_id: str = db.Column(db.String(41), nullable=False)
    date: str = db.Column(db.DateTime, nullable=False)
    question = db.Column(db.String(60), nullable=False)
    given_answer: str = db.Column(db.String(50), nullable=False)
    correct: bool = db.Column(db.Boolean)
    context: str = db.Column(db.String(20), nullable=False)
    context_correct: bool = db.Column(db.Boolean)

    def __init__(self, inputs: list, from_csv: bool = False):
        if from_csv:
            self.append_from_csv(*inputs)
        else:
            self.append_from_app(*inputs)

    def append_from_csv(self, id_: str, user_id: int, word_id: int, date: str, question: str,
                        given_answer: str, correct: str, context: str, context_correct: bool):
        self.id = id_
        self.word_id = word_id
        self.date = date
        self.question = question
        self.given_answer = given_answer
        self.correct = correct == "True"
        self.context = context
        self.context_correct = context_correct == "True"
        self.user = User.query.filter_by(id=user_id).first()

    def append_from_app(self, user_id: int, word_id: int, date: str, question: str,
                        correct_answer: str, given_answer: str, correct_context: str, given_context: str):
        user_object = User.query.filter_by(id=user_id).first()
        self.id = "_".join([user_object.username, date, word_id])
        self.word_id = word_id
        self.date = date
        self.question = question
        self.given_answer = given_answer
        self.correct = correct_answer.lower() == given_answer.lower()
        self.context = correct_context
        self.context_correct = correct_context.lower() == given_context.lower()
        self.user = user_object

    def __repr__(self):
        return f"""<id {self.id!r},
                    user_id {self.user_id}
                    word {self.word_id!r},
                    date {self.date!r},
                    question {self.question!r},
                    given_answer {self.given_answer!r},
                    correct  {self.correct!r},
                    given_context {self.given_context!r},
                    context_correct  {self.context_correct!r},
                    user {self.user!r}
                    >"""
