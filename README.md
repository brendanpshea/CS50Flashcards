# CS50 Flashcards: User Guide

Brendan Shea (brendanpshea@gmail.com)
LINK to video: https://youtu.be/x9E1p9m_xxk

## Introduction
CS50 Flashcards is a webapp that allows users to create, review, and delete flashcards. Users can also review statistics related to their performance on the flashcards. Finally, “teacher” accounts have the additional abilities to (1) assign flashcards to student accounts and (2) review statistics related to student performance regarding these flashcards. The program implements a simple “spaced repetition” algorithm to increase the efficiency with which users learn flashcards. Basically, this means that the period between repetitions of a given card will vary on how well the user knows it (based on their previous performance with the card). 

## How do I run the program? 
This program was built using the distribution code for CS50 Finance, and can be run in the same way. The program is distributed as a Flask web app. Navigate to the directory with “application.py” and run “flask run” from the command line. You should now see an “http…” link you can click on to access the web application. In order to run successfully, the program requires “application.py”, “helpers.py”, and “flashcards.db” in the main directory, plus templates for each route in the “templates” sub-directory. 

## How do I register and login? 
Users must be logged in to access most of the app’s functionality. You can create an account by clicking on “register” and following the directions there. Once you have registered, you can use the account you have successfully created to log in. There are also three provided accounts (which you don’t need to use, but are free to explore). The usernames are “student1”, “student2”, and “teacher1”. The passwords for all are “CS50!”.

## How do I create a card? 
You can click “create a card” in the navbar. Enter your question and answer in the respective boxes and click the button to create the card. 

## How do I review cards? 
Once you have created cards, you can click “review cards” to begin reviewing your flashcards. Once you begin reviewing, you have three options: “I got it right!”, “I got it wrong!” and “delete this card.” Click on the appropriate button. 

## How I review my statistics? 
o review your statistics, you can click on “my stats.” This will show overall statistics related to your activity, as well as card-by-card statistics.

## How do I delete a card? 
At this point, the only way to delete a card is when it comes up for review (when you can choose to delete it). You will be asked to confirm your choice before the deletion is carried out. 

## How do I edit a card? 
At this point, it isn’t possible to edit a card. You’ll need to delete the card and create a new one. This is something for future work!

## How do I access the teacher functionality? 
When you create an account, you’ll need to choose the “teacher” option.
From the teacher account, how do I create cards for my students? First, you need to create the card for yourself. Once you’ve done so, you can click on the “Teacher Tools” (in the nav bar) and select the option to share cards with students. This should take you to a page where you can share cards with your students.

## What is the spaced repetition algorithm? 
It is inspired by (though far simpler than) the algorithms used by programs like Anki (https://apps.ankiweb.net/) and Supermemo (https://www.supermemo.com/en). In general, if a user successfully remembers a card, the next review for that card will be twice as long as the period that has passed since their last successful review. If the user fails to remember the card, by contrast, the next review will be scheduled (almost) immediately, and the cycle of learning the card will begin again. In this way, users spend most of their time reviewing cards they are actively trying to learn, and see “already mastered” cards 