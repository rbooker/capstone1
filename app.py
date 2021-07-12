from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from tools import get_quiz_data
from models import db, connect_db, User, Quiz, QuizQuestion, Question
from forms import CreateQuizForm, AddQuestionToQuiz, EditQuestion, AddQuestion, NewUserForm, LogInForm
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///trivia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

debug = DebugToolbarExtension(app)

######################################################
#Login/Logout routes
######################################################
@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup."""

    form = NewUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LogInForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("You have been successfully logged out. Goodbye!", "success")
    return redirect("/login")

@app.route('/deleteprofile')
def delete_profile_page():
    """Show delete profile page - contains warnings"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    return render_template("delete_profile.html")
    
@app.route('/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


######################################################
#Quiz routes
######################################################

@app.route("/quizzes/create", methods=["GET", "POST"])
def create_quiz():
    """Create a new quiz"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user

    form = CreateQuizForm()

    if form.validate_on_submit():
        #Get form data
        user_id = user.id
        name = form.name.data
        description = form.description.data
        rounds = form.rounds.data
        qs_per_round = form.qs_per_round.data
        difficulty_levels = [form.round_one_diff.data, 
                             form.round_two_diff.data,
                             form.round_three_diff.data,
                             form.round_four_diff.data,
                             form.round_five_diff.data]
        
        #Create new quiz and add to db
        quiz = Quiz(name=name,
                    description=description,
                    rounds=rounds,
                    user_id=user_id)
        db.session.add(quiz)
        db.session.commit()
        db.session.refresh(quiz)
        quiz_id = quiz.id

        #Get questions and add to db
        for round_no in range(1, quiz.rounds + 1):
            quiz_data = get_quiz_data(difficulty_levels[round_no - 1], qs_per_round, user_id)
            db.session.add_all(quiz_data)
            db.session.commit()
            
            #Create associations between quiz and questions
            for quiz_datum in quiz_data:
                db.session.refresh(quiz_datum)
                quiz_question = QuizQuestion(quiz_id=quiz_id,
                                             question_id=quiz_datum.id,
                                             round=round_no)
                db.session.add(quiz_question)
            db.session.commit()

        return redirect(f"/quizzes/show/{quiz_id}")

    else:
        return render_template("create_quiz.html", form=form)

@app.route("/quizzes/show")
def show_quizzes():
    """Show all quizzes"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    user_id = user.id

    quizzes = Quiz.query.filter(Quiz.user_id == user_id).order_by(Quiz.id).all()

    return render_template("show_all_quizzes.html",quizzes=quizzes)

@app.route("/quizzes/show/<int:quiz_id>")
def show_quiz(quiz_id):
    """Show the quiz with the given id"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    quiz = Quiz.query.get_or_404(quiz_id)
    quiz_questions = []
    for round_no in range(1, quiz.rounds + 1):
        round = []
        for quiz_question in quiz.questions:
            if quiz_question.round == round_no:
                round.append(quiz_question.question)
        quiz_questions.append(round)

    return render_template("show_quiz.html", quiz_questions=quiz_questions, quiz=quiz)

@app.route("/quizzes/edit/<int:quiz_id>")
def edit_quiz(quiz_id):
    """Edit the quiz with the given id"""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    quiz = Quiz.query.get_or_404(quiz_id)
    quiz_questions = []
    for round_no in range(1, quiz.rounds + 1):
        round = []
        for quiz_question in quiz.questions:
            if quiz_question.round == round_no:
                round.append(quiz_question.question)
        quiz_questions.append(round)

    return render_template("edit_quiz.html", quiz_questions=quiz_questions, quiz=quiz)

@app.route("/quizzes/replace_questions/<int:quiz_id>", methods=["POST"])
def replace_questions(quiz_id):
    """Replace selected questions in the quiz with the given id"""
    q_ids = request.form.getlist("checked_questions")
    quiz = Quiz.query.get_or_404(quiz_id)

    for q_id in q_ids:
        q_to_replace = Question.query.get_or_404(int(q_id))

        for quiz_question in q_to_replace.quizzes:
            qq = quiz_question.quiz
            if qq.id == quiz_id:
                quiz_question_to_replace = quiz_question
        
        #get replacement question - will have same difficulty and round as old question
        replacement_question_array = get_quiz_data([q_to_replace.difficulty], 1, q_to_replace.user_id)
        replacement_question = replacement_question_array[0]

        #add new question to db
        db.session.add(replacement_question)
        db.session.commit()
        db.session.refresh(replacement_question)

        #add new question to quiz
        new_quiz_question = QuizQuestion(quiz_id=quiz_id,
                                     question_id=replacement_question.id,
                                     round=quiz_question_to_replace.round)
        db.session.add(new_quiz_question)
        db.session.commit()

        #remove question from quiz - don't delete it, though
        db.session.delete(quiz_question_to_replace)
        db.session.commit()


    return redirect(f"/quizzes/edit/{quiz_id}")

@app.route("/quizzes/delete/<int:quiz_id>", methods=["POST"])
def delete_quiz(quiz_id):

    quiz_to_delete = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz_to_delete)
    db.session.commit()

    return redirect("/quizzes/show")

######################################################
#Quiz routes
######################################################

@app.route("/questions/create", methods=["GET", "POST"])
def create_question():
    """Add question"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    user_id = user.id
    
    form = AddQuestion()
    

    if form.validate_on_submit():

        new_question = Question(question=form.question.data,
                                answer=form.answer.data,
                                difficulty=form.difficulty.data,
                                user_id=user_id)

        db.session.add(new_question)
        db.session.commit()
        db.session.refresh(new_question)

        return redirect(f"/questions/show/{new_question.id}")

    return render_template("create_question.html", form=form)

@app.route("/questions/edit/<int:question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    """Edit question"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    question = Question.query.get_or_404(question_id)
    form = EditQuestion()

    if form.validate_on_submit():

        question.question = form.question.data
        question.answer = form.answer.data
        question.difficulty = form.difficulty.data
        db.session.commit()

        return redirect(f"/questions/show/{question_id}")

    return render_template("edit_question.html", question=question, form=form)

@app.route("/questions/show")
def show_questions():
    """Show all questions"""
   
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    user_id = user.id

    questions = Question.query.filter(Question.user_id == user_id).order_by(Question.id).all()

    return render_template("show_all_questions.html",questions=questions)

@app.route("/questions/show/<int:question_id>", methods=["GET", "POST"])
def show_question(question_id):
    """Show question - Also allow it to be added to a quiz"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    question = Question.query.get_or_404(question_id)
    form = AddQuestionToQuiz()

    #Get all the quizzes that the question is on
    quizzes_with_question = [quiz_question.quiz.id for quiz_question in question.quizzes]
    #Then use this to get all the quizzes it isn't on
    quiz_choice_data = db.session.query(Quiz.id, Quiz.name, Quiz.rounds).filter(Quiz.id.notin_(quizzes_with_question)).all()
    #These are the options for the quiz select in the form
    quiz_choices = [(quiz_datum.id, quiz_datum.name) for quiz_datum in quiz_choice_data]
    #These help dynamically generate the rounds in the quiz selected that the question can be added to
    quiz_rounds = [(quiz_datum.id, quiz_datum.rounds) for quiz_datum in quiz_choice_data]

    form.quiz.choices = quiz_choices

    if form.validate_on_submit():
        quiz_id = form.quiz.data
        round = form.round.data

        #Add the question to the selected quiz and round and show the amended quiz
        new_quiz_question = QuizQuestion(quiz_id=quiz_id, question_id=question_id, round=round)
        db.session.add(new_quiz_question)
        db.session.commit()
        new_quiz_question.question = question
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz.questions.append(new_quiz_question)

        return redirect(f"/quizzes/show/{quiz.id}")


    return render_template("show_question.html", question=question, form=form, quiz_rounds=quiz_rounds)

@app.route("/questions/delete/<int:question_id>", methods=["POST"])
def delete_question(question_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    question_to_delete = Question.query.get_or_404(question_id)
    db.session.delete(question_to_delete)
    db.session.commit()

    return redirect("/questions/show")

######################################################
#Homepage route
######################################################

@app.route('/')
def homepage():
    """Show homepage"""

    if g.user:

        return render_template('home.html', username=g.user.username)

    else:
        return render_template('home-anon.html')

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req



    


