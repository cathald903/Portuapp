"""
File containing the definition of all the forms used in the project
"""
from flask import session
from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, IntegerField, PasswordField, RadioField, SelectField
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError
from app.config import current_datetime, DATETIME_FORMAT
from app.models import User


class LoginForm(FlaskForm):
    """
    Simple loginform that enforces minimum name and password lengths
    """
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)],
                             render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    """
    Simple signup form that enforces minimum name and password lengths
    """
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)],
                             render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        """
        Checks to make sure that username doesn't exist already in our database
        """
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class QuestionSetupForm(FlaskForm):
    """
    Form used to setup the number and types of questions the user wants
    """
    num_of_questions = IntegerField('How many questions?', validators=[
                                    DataRequired()], render_kw={'autofocus': True})
    quiz_area = SelectField('What areas?', choices=[
        'Mixed', 'Verbs', 'Vocab'], validators=[DataRequired()])
    verb_conjugation = SelectField('Test conjugation?', choices=[
        'No', 'Past', 'Present', 'Future'], validators=[DataRequired()])
    context = RadioField('Test context?', choices=[
        ('Yes', True), ('No', False)], validators=[DataRequired()])
    submit = SubmitField('Get Quizzin')


class ConjugationForm(FlaskForm):
    """
    form to show the different pronouns when quizzing the user
    """
    eu = StringField('Eu', validators=[DataRequired()],  render_kw={
        'autofocus': True})
    tu = StringField('Tu', validators=[DataRequired()],  render_kw={
        'autofocus': True})
    el = StringField('Ele/Ela/Você', validators=[DataRequired()],  render_kw={
        'autofocus': True})
    nos = StringField('Nós', validators=[DataRequired()],  render_kw={
        'autofocus': True})
    vos = StringField('Vós', validators=[DataRequired()],  render_kw={
        'autofocus': True})
    els = StringField('Eles/Elas/Vocês', validators=[DataRequired()],  render_kw={
        'autofocus': True})
    tense = StringField('')
    submit = SubmitField('Submit Answer')


class QuestionForm(FlaskForm):
    """
    This form contains the fields that will be displayed to the user
    when they are questioned
    """

    def validate_context_field(self, context):
        """
        Checks that the user requested to be quized on context and that the given word
        has additional context to actually quiz the user on
        """
        if session['question_dict']['quiz_on_context'] == 'Yes' and (
                len(context.data) == 0 and self.context_question.data):
            raise ValidationError('Required Field')
        else:
            return True

    question = StringField('')
    answer = StringField('', validators=[DataRequired()], render_kw={
                         'autofocus': True})
    context_question = StringField('')
    context_answer = StringField('', validators=[validate_context_field], default='', render_kw={
        'autofocus': True})
    submit = SubmitField('Submit Answer')


class FilterForm(FlaskForm):
    """
    Contains the fields to Filter the table on the Answer History page
    """

    def time_range_validator(self, field):
        """
        Checks to see if the given time fields are valid, eg end date not before start date
        """
        if not field.data or not self.date_start_filter.data:
            return True
        elif self.date_start_filter.data <= field.data:
            return True
        else:
            raise ValidationError(
                'End Date must be equal to or after Start Date.')

    date_start_filter = DateTimeLocalField(
        'Start Date',  default=current_datetime('datetime'), format=DATETIME_FORMAT)
    date_end_filter = DateTimeLocalField(
        'End Date', default=current_datetime('datetime'),
        validators=[time_range_validator], format=DATETIME_FORMAT)
    word_filter = SelectField(
        'word', choices=['All'], default='All')
    correct_filter = SelectField('correct', choices=[('None', 'All'), (
        'True', 'Correct'), ('False', 'Incorrect')], default='None')
    submit = SubmitField('Filter')
