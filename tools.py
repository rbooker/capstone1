import requests
from math import ceil
from models import Question

def get_quiz_data(difficulty, total_questions, user_id):
    """Gets the initial quiz data from the Jservice API"""
    ###########################################
    #difficulty: a list storing the difficulty of the questions to retrieve
    #total_questions: the total number of questions to retrieve
    #user_id: needed for instantiation of Question objects
    ###########################################

    quiz_questions = []

    while len(quiz_questions) < total_questions:

        question_resp = requests.get(f"http://jservice.io/api/random?count={total_questions * 5}")
        question_data = question_resp.json()

        for question in question_data:

            if question["value"] is not None:
                q_diff = ceil(int(question["value"])/200)
                if q_diff in difficulty:
                    quiz_questions.append(Question(question=question["question"], answer=question["answer"], difficulty=q_diff, user_id=user_id))
                    if len(quiz_questions) == total_questions:
                        break

    return quiz_questions


