from app.config import current_datetime, datetime_format
from flask import session
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, StringField, PasswordField, DateTimeLocalField, RadioField, SelectMultipleField, BooleanField, FormField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)],
                             render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)],
                             render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class QuestionSetupForm(FlaskForm):
    num_of_questions = IntegerField('How many questions?', validators=[
                                    DataRequired()], render_kw={'autofocus': True})
    quiz_area = SelectMultipleField('What areas?', choices=[
        'Mixed', 'Verbs', 'Vocab'], validators=[DataRequired()])
    verb_conjugation = SelectMultipleField('Test conjugation?', choices=[
        'No', 'Past', 'Present', 'Future'], validators=[DataRequired()])
    context = RadioField('Test context?', choices=[
        ('Yes', True), ('No', False)], validators=[DataRequired()])
    submit = SubmitField('Get Quizzin')


class ConjugationForm(FlaskForm):
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
    def validate_context_field(self, context):
        if session['question_dict']['quiz_on_context'] == 'Yes' and len(context.data) == 0 and self.context_question.data:
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


class ResultsForm(FlaskForm):
    def time_range_validator(self, field):
        if not field.data or not self.date_start_filter.data:
            return True
        elif self.date_start_filter.data <= field.data:
            return True
        else:
            raise ValidationError(
                'End Date must be equal to or after Start Date.')

    date_start_filter = DateTimeLocalField(
        'Start Date',  default=current_datetime('datetime'), format=datetime_format)
    date_end_filter = DateTimeLocalField(
        'End Date', default=current_datetime('datetime'), validators=[time_range_validator], format=datetime_format)
    word_filter = SelectField(
        'word', choices=['All'], default='All')
    correct_filter = SelectField('correct', choices=[('None', 'All'), (
        'True', 'Correct'), ('False', 'Incorrect')], default='None')
    submit = SubmitField('Filter')
