from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text,nullable=False)

    quizzes = db.relationship('Quiz', cascade="all, delete")
    questions = db.relationship('Question', cascade="all, delete")

    @classmethod
    def signup(cls, username, password):
        """Sign up user.

        Hashes password and adds user to system.
        Stolen from the 'Warbler' app
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.

        Stolen from the 'warbler' app
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Quiz(db.Model):
    """Quiz"""

    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    rounds = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)

    questions = db.relationship("QuizQuestion", back_populates="quiz", cascade="all, delete")

class QuizQuestion(db.Model):
    """Mapping of a quiz to a question."""

    __tablename__ = "quiz_questions"

    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    round = db.Column(db.Integer, nullable=False)
    question = db.relationship("Question", back_populates="quizzes")
    quiz = db.relationship("Quiz", back_populates="questions")

class Question(db.Model):
    """Question"""

    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)

    quizzes = db.relationship("QuizQuestion", back_populates="question", cascade="all, delete")

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)