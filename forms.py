from wtforms import SelectField, StringField, SelectMultipleField, RadioField, PasswordField, widgets
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, DataRequired, Length, Optional

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.

    Taken from the WTForms website
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class CreateQuizForm(FlaskForm):
    """Form for creating quizzes"""

    name = StringField("Quiz Name",  validators=[InputRequired(message="Quiz Name can't be blank"), Length(max=50, message="Quiz Name can't exceed 50 characters")])
    description = StringField("Description", validators=[Optional(), Length(max=250, message="Quiz Description can't exceed 250 characters")])
    rounds = SelectField("Number of Rounds", choices=[(1,1),(2,2),(3,3),(4,4),(5,5)], coerce=int)
    qs_per_round = SelectField("Questions per Round", choices=[(5,5),(10,10),(15,15),(20,20)], coerce=int)
    round_one_diff = MultiCheckboxField("Round One Difficulty", choices=[(1,1),(2,2),(3,3),(4,4),(5,5)], coerce=int, validators=[DataRequired(message="Select at least one question difficulty level")])
    round_two_diff = MultiCheckboxField("Round Two Difficulty", choices=[(1,1),(2,2),(3,3),(4,4),(5,5)], coerce=int, validators=[DataRequired(message="Select at least one question difficulty level")])
    round_three_diff = MultiCheckboxField("Round Three Difficulty", choices=[(1,1),(2,2),(3,3),(4,4),(5,5)], coerce=int, validators=[DataRequired(message="Select at least one question difficulty level")])
    round_four_diff = MultiCheckboxField("Round Four Difficulty", choices=[(1,1),(2,2),(3,3),(4,4),(5,5)], coerce=int, validators=[DataRequired(message="Select at least one question difficulty level")])
    round_five_diff = MultiCheckboxField("Round Five Difficulty", choices=[(1,1),(2,2),(3,3),(4,4),(5,5)], coerce=int, validators=[DataRequired(message="Select at least one question difficulty level")])

class AddQuestionToQuiz(FlaskForm):
    """Form for adding a question to a quiz"""

    quiz = SelectField("Add Question To Quiz:", coerce=int)
    round = SelectField('Add Question To Round:', coerce=int, validate_choice=False)

class EditQuestion(FlaskForm):
    """Form for editing a question"""

    question = StringField("Question",  validators=[InputRequired(message="Question can't be blank")])
    answer = StringField("Answer",  validators=[InputRequired(message="Answer can't be blank")])
    difficulty = RadioField("Difficulty", choices=[(1,1),(2,2),(3,3),(4,4),(5,5)], coerce=int, validators=[DataRequired(message="Select a difficulty")])

class AddQuestion(FlaskForm):
    """Form for editing a question"""

    question = StringField("Question",  validators=[InputRequired(message="Question can't be blank")])
    answer = StringField("Answer",  validators=[InputRequired(message="Answer can't be blank")])
    difficulty = RadioField("Difficulty", choices=[(1,1),(2,2),(3,3),(4,4),(5,5)], coerce=int, validators=[DataRequired(message="Select a difficulty")])

class NewUserForm(FlaskForm):
    """Form for adding a user"""
    
    username = StringField('Username', validators=[DataRequired(message="Enter a name")])
    password = PasswordField('Password', validators=[Length(min=6, message="Password must be at least six characters long")])

class LogInForm(FlaskForm):
    """Form for logging in a user"""
    
    username = StringField('Username', validators=[DataRequired(message="Enter a name")])
    password = PasswordField('Password', validators=[Length(min=6, message="Password must be at least six characters long")])

class ChangeUsernameForm(FlaskForm):
    """Form for changing username"""

    username = StringField('New Username', validators=[DataRequired(message="Enter a name")])
    password = PasswordField('Password', validators=[Length(min=6, message="Password must be at least six characters long")])

class ChangePasswordForm(FlaskForm):
    """Form for changing password"""

    new_password = PasswordField('New Password', validators=[Length(min=6, message="Password must be at least six characters long")])
    password = PasswordField('Current Password', validators=[Length(min=6, message="Password must be at least six characters long")])


