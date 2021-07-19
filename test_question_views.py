"""Quiz View Tests"""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_question_views.py

import os
from unittest import TestCase

from models import db, connect_db, User, Quiz, Question, QuizQuestion

os.environ['DATABASE_URL'] = "postgresql:///trivia-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class QuestionViewTestCase(TestCase):

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

    def test_create_question(self):
        """Test the create question route"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post("/questions/create", data={"question": "What is the answer to life, the universe, and everything?",
                                                   "answer": "Forty-two",
                                                   "difficulty" : 5},
                                                   follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            #Assert the question/answer pair is there and that the difficulty is correct
            self.assertIn('What is the answer to life, the universe, and everything?', str(resp.data))
            self.assertIn('Forty-two', str(resp.data))
            self.assertIn('<strong>Difficulty:</strong> 5', str(resp.data))

    def setup_quiz_and_question(self):
        """Set up a quiz and question for subsequent tests"""
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

    def test_edit_question(self):
        """Test edit question route"""
        self.setup_quiz_and_question()

        test_question = Question.query.filter(Question.answer=="Forty-two").one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/questions/edit/{test_question.id}", data={"question": "What is the question of life, the universe, and everything?", 
                                                                       "answer": "Six times nine", 
                                                                       "difficulty" : 4}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
    
            #Assert that the old question/answer/difficulty are not there
            self.assertNotIn('What is the answer to life, the universe, and everything?', str(resp.data))
            self.assertNotIn('Forty-two', str(resp.data))
            self.assertNotIn('<strong>Difficulty:</strong> 5', str(resp.data))
            #Assert the question/answer pair is there and that the difficulty is correct
            self.assertIn('What is the question of life, the universe, and everything?', str(resp.data))
            self.assertIn('Six times nine', str(resp.data))
            self.assertIn('<strong>Difficulty:</strong> 4', str(resp.data))

    def test_show_questions(self):
        """Test show all questions"""

        self.setup_quiz_and_question()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/questions/show")

            self.assertEqual(resp.status_code, 200)
                
            #Assert the question/answer pair is there and that the difficulty is correct
            self.assertIn('What is the answer to life, the universe, and everything?', str(resp.data))
            self.assertIn('Forty-two', str(resp.data))
            self.assertIn('<strong>Difficulty:</strong> 5', str(resp.data))

    def test_show_question(self):
        """Test show question - The GET route for questions/show/<int:question_id>"""

        self.setup_quiz_and_question()
        test_question = Question.query.filter(Question.answer=="Forty-two").one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f"/questions/show/{test_question.id}")

            self.assertEqual(resp.status_code, 200)
                
            #Assert the question/answer pair is there and that the difficulty is correct
            self.assertIn('What is the answer to life, the universe, and everything?', str(resp.data))
            self.assertIn('Forty-two', str(resp.data))
            self.assertIn('<strong>Difficulty:</strong> 5', str(resp.data))

    def test_add_question_to_quiz(self):
        """Test adding question to quiz - The POST route for questions/show/<int:question_id>"""

        self.setup_quiz_and_question()
        test_quiz = Quiz.query.filter(Quiz.name=="testquiz").one()
        test_quiz_id = test_quiz.id
        
        #Create new question to add to quiz
        new_test_question = Question(question="What is the question of life, the universe, and everything?",
                            answer= "Six times nine",
                            difficulty = 5,
                            user_id = self.testuser.id)
        db.session.add(new_test_question)
        db.session.commit()
        db.session.refresh(new_test_question)
        new_test_question_id = new_test_question.id

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post(f"/questions/show/{new_test_question_id}", data={"quiz": test_quiz_id,
                                                                           "round": 1},
                                                                           follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
                
            #Route redirects to page displaying quiz the question was added to - assert correct quiz
            self.assertIn('testquiz', str(resp.data)) 
            #Assert the question/answer pair is there and that the difficulty is correct
            self.assertIn('What is the question of life, the universe, and everything?', str(resp.data))
            self.assertIn('Six times nine', str(resp.data))
            self.assertIn('<strong>Difficulty:</strong> 5', str(resp.data))

    def test_delete_question(self):

        self.setup_quiz_and_question()
        test_question = Question.query.filter(Question.answer=="Forty-two").one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/questions/delete/{test_question.id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            #Redirects to "show all questions page" - test_question should be gone
            self.assertNotIn('What is the answer to life, the universe, and everything?', str(resp.data))
            self.assertNotIn('Forty-two', str(resp.data))
            self.assertNotIn('<strong>Difficulty:</strong> 5', str(resp.data))
            

            



            

