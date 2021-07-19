"""Quiz View Tests"""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_quiz_views.py

import os
from unittest import TestCase

from models import db, connect_db, User, Quiz, Question, QuizQuestion

os.environ['DATABASE_URL'] = "postgresql:///trivia-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class QuizViewTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    password="testuser")
        self.testuser_id = 6969
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    """def test_create_quiz(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/quizzes/create", data={"name": "testquiz",
                                                   "description": "a test quiz",
                                                   "rounds" : 5,
                                                   "qs_per_round": 5,
                                                   "round_one_diff": 1,
                                                   "round_two_diff": 2,
                                                   "round_three_diff": 3,
                                                   "round_four_diff": 4,
                                                   "round_five_diff": 5})
            
            self.assertEqual(resp.status_code, 302)

            quiz = Quiz.query.one()
            self.assertEqual(quiz.name, "testquiz")
            self.assertEqual(quiz.description, "a test quiz")
            self.assertEqual(quiz.rounds, 5)
            self.assertEqual(len(quiz.questions), 25)"""

    def setup_quizzes(self):
   
        quiz = Quiz(name="testquiz",
                    description="a test quiz",
                    rounds = 1,
                    user_id = self.testuser.id)
        db.session.add(quiz)
        db.session.commit()
        db.session.refresh(quiz)
                
        question = Question(question="What is the answer to life, the universe, and everything?",
                            answer= "Forty-two",
                            difficulty = 5,
                            user_id = self.testuser.id)
        db.session.add(question)
        db.session.commit()
        db.session.refresh(question)

        quiz_question = QuizQuestion(quiz_id=quiz.id,
                                    question_id=question.id,
                                    round=1)
        db.session.add(quiz_question)
        db.session.commit()

    def test_show_quizzes(self):

        self.setup_quizzes()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/quizzes/show")

            self.assertEqual(resp.status_code, 200)
                
            self.assertIn('testquiz', str(resp.data))
            self.assertIn('a test quiz', str(resp.data))

    def test_show_quiz(self):

        self.setup_quizzes()
        test_quiz = Quiz.query.filter(Quiz.name=="testquiz").one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f"/quizzes/show/{test_quiz.id}")

            self.assertEqual(resp.status_code, 200)
                
            self.assertIn('testquiz', str(resp.data))
            self.assertIn('What is the answer to life, the universe, and everything?', str(resp.data))
            self.assertIn('Forty-two', str(resp.data))
            self.assertIn('Difficulty:</strong> 5', str(resp.data))

    def test_edit_quiz_replace_question(self):

        self.setup_quizzes()
        test_quiz = Quiz.query.filter(Quiz.name=="testquiz").one()
        test_question = Question.query.filter(Question.answer=="Forty-two").one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/quizzes/edit/{test_quiz.id}", data={"checked_questions":f"{test_question.id}"})

            self.assertEqual(resp.status_code, 200)

            self.assertIn('testquiz', str(resp.data))

            #The question should be different, but of the same difficulty
            self.assertNotIn('What is the answer to life, the universe, and everything?', str(resp.data))
            self.assertNotIn('Forty-two', str(resp.data))
            self.assertIn('Difficulty:</strong> 5', str(resp.data))

    def test_edit_quiz_delete_question(self):

        self.setup_quizzes()
        test_quiz = Quiz.query.filter(Quiz.name=="testquiz").one()
        test_question = Question.query.filter(Question.answer=="Forty-two").one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/quizzes/remove_questions/{test_quiz.id}", data={"checked_questions":f"{test_question.id}"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('testquiz', str(resp.data))

            #The question should be gone
            self.assertNotIn('What is the answer to life, the universe, and everything?', str(resp.data))
            self.assertNotIn('Forty-two', str(resp.data))

            

