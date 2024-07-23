"""
Contains the definitions for the database Models and some utility functions
that they will use
"""
from flask_login import UserMixin
from app import db


def get_present_tense_endings(ending):
    """
    Function to provide a quick dictionary reference for the given verb
    """
    endings = {'er': ('o', 'es', 'e', 'emos', 'eis', 'em'),
               'ar': ('o', 'as', 'a', 'amos', 'ais', 'am'),
               'ir': ('o', 'es', 'e', 'imos', 'is', 'em')}
    return endings[ending]


def add_conjugation(portu, tense) -> str:
    """
    Attaches the correct conjugation to the end of the given verb depending
    on it's ending.
    Currently only present tense is defined
    """
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
    """
    User table definition that contains the basic info of the user.
    Has a one to many relationship with the Answers table.
    """
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
    """
    User Subscription table definition that contains which words the user has subscribed
    to and so which ones they can be quized on.
    Has a many to one relationship with the Users table.
    """
    __tablename__ = 'user_subscriptions'
    word: str = db.Column(db.String(41), primary_key=True)
    kind: str = db.Column(db.String(6), nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False)

    def __repr__(self):
        return f"""<word {self.word!r},
                    kind {self.kind!r},
                    user {self.user_id!r}>"""


class Vocab(db.Model):
    """
    Vocab table
    """
    __tablename__ = 'vocab'
    id: str = db.Column(db.String(41), primary_key=True)
    english: str = db.Column(db.String(20), nullable=False)
    portuguese: str = db.Column(db.String(20), nullable=False)
    masculine: str = db.Column(db.String(20), nullable=True)
    feminine: str = db.Column(db.String(20), nullable=False)
    article: str = db.Column(db.String(20), nullable=False)
    batch: int = db.Column(db.Integer, nullable=False)

    def __init__(self, inputs: list):
        self.append_data(*inputs)

    def append_data(self, eng: str, portu: str, m: str, f: str, article: str, batch: str):
        """
        fill the objects vairables with the given values
        """
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


class Verb(db.Model):
    """
    Verb table definition
    """
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

    def __init__(self, inputs: list):
        self.append_data(*inputs)

    def append_data(self, eng: str, portu: str, kind: str, batch: str,
                    context: str, past: str, present: str, future: str):
        """
        Formats and sets the given info into the Vocab Models variables
        """
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


class Answers(db.Model):
    """
    Answer Model definition
    """
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
    conjugation_correct: bool = db.Column(db.Boolean)

    def __init__(self, inputs: list):
        self.append_data(*inputs)

    def append_data(self, id_: str, user_id: int, word_id: int, date: str, question: str,
                    given_answer: str, correct: str, context: str, context_correct: bool,
                    user_conjugation: bool):
        """
        appending to the Answers table.
        """
        self.id = id_
        self.word_id = word_id
        self.date = date
        self.question = question
        self.given_answer = given_answer
        self.correct = correct == 'True'
        self.context = context
        self.context_correct = context_correct == 'True'
        self.user_id = user_id
        self.conjugation_correct = user_conjugation == 'True'

    def __repr__(self):
        return f"""<id {self.id!r},
                    user_id {self.user_id}
                    word {self.word_id!r},
                    date {self.date!r},
                    question {self.question!r},
                    given_answer {self.given_answer!r},
                    correct  {self.correct!r},
                    context_correct  {self.context_correct!r},
                    conjugation_correct {self.conjugation_correct!r}
                    >"""
