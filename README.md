### Capstone Project 1
#### Quizzr - the Quiz-generating website
Available at https://quizzr-rb.herokuapp.com/

Quizzr was created by me, Ryan Booker, as one of the capstone projects I had to complete for the Springboard software engineering program in which I was enrolled in 2021. I'm a bit of a trivia fanatic (and also one of the country's best competitive crossworders - in the span of a year I won my skill division at [the largest](https://www.acptonline.com/prizes) and [second-largest](https://en.wikipedia.org/wiki/Lollapuzzoola#Past_Champions) tournaments in the U.S.) and, besides participating in several weekly pub trivia nights here in Portland, Oregon, I enjoy writing quizzes for family gatherings and other social occasions. However, it can sometimes be difficult to think of 20-30 questions off the top of my head, especially on short notice. Hence this app, which draws upon [JService](http://jservice.io/), the Jeopardy! question database (and the single largest trivia API on the internet) to generate quizzes. Many of the questions I "think up" for quizzes I write I'm simply recalling from episodes of Jeopardy! anyhow, so this is simply cutting out the middleman (me).

After registering, users can generate quizzes for which they specify the number of rounds (1-5), the number of questions per round (5-20), and the difficulty level of the questions in each round (from 1-5 - converting from Jeopardy! dollar value to difficulty using the formula: ceiling(dollar_value/200)). As mentioned above, questions are drawn from [JService](http://jservice.io/), the Jeopardy! question database. After a quiz is generated, users can edit it by removing questions, replacing questions with ones of equal difficulty from JService, or by adding questions they write themselves to it. Quizzes and questions (both downloaded and user-generated) are stored and can be displayed, edited, or deleted at the user's discretion.

The site makes use of HTML (rendered with Jinja), CSS (mostly provided by Bootstrap), Javascript, Flask, SQLAlchemy (using PostgreSQL), and WTForms, and was tested with the unittest library


