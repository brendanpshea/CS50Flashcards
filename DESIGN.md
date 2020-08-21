## CS50 Flashcards: Design Document
Brendan Shea (brendanpshea@gmail.com)

CS50 is a web application built using Python (Flask) on the backend; JavaScript, CSS, and HTML on the fronted; and an SQLite database with tables for users for users and cards. Bootstrap was used to style the project. It was built on the basis of the distribution code for CS50 Finance, and what I learned in that project, though it goes considerably beyond what I did there. The idea was inspired by my regular use of Anki flashcards (https://apps.ankiweb.net/), and my desire to have something similar that I use with my students (e.g., where I could create flashcards for them, and see their progress with them).  
While the app I’ve designed isn’t quite ready for deployment in a classroom setting, I was pleasantly surprised on how it turned out, and ended up learning quite a bit along the way. In what follows, I’ve provided an outline of the structure of the app, together with a short explanation of why I made the design decisions I did.

# flashcard.db

This is the SQLite database. It contains a table for “users” and one for “cards.” These tables can be joined on the card.user_id and users.id fields. The user field holds the basic info entered by the user when they registered, including username, a password hash, email address, and a field indicating whether they are a teacher or student. The card table holds not only the question and answer, but also other info about the user’s performance on that card, such as how many times they answered it correctly or incorrectly, the card’s next due date, and the last time the card was reviewed. Because of this design decision, users cannot *share* cards directly (though the app does allow teachers to create *copies* of cards for student accounts). I considered separating the question/answer from the user-specific data (and creating a third table), which would allow different users to “share” the same card. In the end, though, I decided that it made more sense to have each user have their “own” flashcard deck, over which they could exercise control.

## Functions in application.py  
This is where the flask application resides. Several of the functions/routes are very similar to those used for the Finance project, so I won’t comment on those here. Error and success messages are generally delivered using Flask’s built-in “flash” functionality, rather than the “apology” function. New or altered routes include:

### index()
A short function that renders the homepage. It queries the database to determine how many flashcards are currently due. 

### create()
This function renders the route that allows users to create flashcards. It first checks whether there is already a card with an identical question; if so, the creation fails. If this check passes, the card is created through an “insertion” to cards.

### review()
This handles the user reviewing flashcards. For “get” requests, it queries the database and serves the flashcard that is “most overdue” (i.e., whose due date is the furthest in the past). For “post” requests (which happen when the user clicks on a button during the review), the function updates the “cards” database correspondingly. If the user gets the card incorrect, the card’s new due date is set to be 1 minute in the future (the idea being that the user should see the card soon, but not immediately). If the user gets the card correct, the time period until the next review of this card is due is calculated as TWICE the time that has passed between this review (“now”) and the previous review. Once this has been done, “review” is called again, and the next card that is due will be displayed. When no more cards are due, a variable passed to the template will trigger a message telling the user this. 

### stats()
This function calculates selected stats for the user: their total number of reviews, the percent correct, etc. It also breaks down these statistics by cards. These are passed to a template to be displayed. In future development of the app, this could be expanded on. 

### teacher_stats
This function allows teacher accounts to see the activity of individual student accounts. Calculating these involve calls to both the user table (to get a list of users) and the cards database (to access the card-level statistics). Again, in future development, there’s more that could be done here (e.g., allowing teachers to see cards, break users into sections, etc.).

### teacher_cards
This was the last function I added. It allows teachers to share cards with student accounts. This involves retrieving a list of “checked” questions from the corresponding route (on a “POST” method), using these ids to retrieve question from the teacher account, and updating each student account (or, at least, each student account that doesn’t already have an identical question) with a NEW card with that question/answer (but with new due dates, last review dates, and so on). 

## Templates
Again, some of this will be familiar from the Finance app, so I won’t go into detail on everything. However, I added some functionality via Javascript, Bootstrap, etc. Some highlights are as follows:

### create.html
Allows user to create cards. Uses JS to validate user input on the front-end to improve user experience (it is checked on the backend as well).

### index.html
Uses Bootstrap’s jumbotron class for introducing the app, and a badge class to alert users of cards due for review.

### layout.html
Closely based on CS50 finance but adds some functionality to the navbar (via drop down menus).

### register.html
In comparison to CS50, there are several additional elements here. Again, JS is used to do some preliminary validation of user input.



