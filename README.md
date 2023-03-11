# DatabaseReviewManager  
*Note:* This repository contains the 'sakila' DVD rental database (more info at https://dev.mysql.com/doc/sakila/en/sakila-structure.html), which files are stores in the 'database' folder.  

## Introduction  
This python program is a command line program. Its intent is to manage the rating of movies in the DVD rental store, having an MYSQL server handling SQL query requests.
It adds two tables to the initial database:  
- **"reviewer"** - which contains fields describing the review poster: Their full name and their ID. With the ID being the primary key.  
- **"rating"** = which containg fields describing the review: Its poster's ID, the movie's ID and the rating itself, a 2-digit number between 0 to 9.9. With the tuple (film ID, reviewer ID) being the primary key and referencing the corresponding columns in the film and reviewer tables.

## Structure
The program is split to two files.
*DatabaseInteract.py* - containing the *DatabaseInteract* class, a class designed to handle all of the transactions with the database
*main.py* - containing the main function. It connects to the MYSQL server and uses the *DatabaseInteract* class to handle all of the transactions with the database.

## Using the program
The program is run in the command line with the `python main.py` command.

## Key Learnings
By developing this project, i have gained experience in the following areas:  
- Programming with a python connector to a MYSQL database.  
- Using safe C\U\D transactions with the database, in order to avoid reading dirty data.  
- Using parameterized queries to avoid SQL injections by the user.  

## Example run:
```
DatabaseReviewManager>python main.py
Please enter your ID: 5
Enter your first name: Daniel
Enter your last name: Boianju
Hello, Daniel Boianju
Please enter film name: lust loo
film doesn't exist in film table, or you have already reviewed this film. please enter a valid name: Lust lock
Please enter rating for this film: 15
the rating must be at least 0.0 and smaller than 10.0. enter a new rating please: 8.7
+-----------+----------------+--------+
|   title   |   full_name    | rating |
+-----------+----------------+--------+
| LUST LOCK | Daniel Boianju |  8.7   |
+-----------+----------------+--------+

DatabaseReviewManager>python main.py
Please enter your ID: 5
Hello, Daniel Boianju
Please enter film name: Academy Dinosaur
There are multiple records of this title, please enter the id of your choice:

+---------+------------------+
| film_id |      title       |
+---------+------------------+
|    1    | ACADEMY DINOSAUR |
|  10000  | ACADEMY DINOSAUR |
+---------+------------------+
please choose a valid film id: 10000
Please enter rating for this film: 9.8
+------------------+----------------+--------+
|      title       |   full_name    | rating |
+------------------+----------------+--------+
|    LUST LOCK     | Daniel Boianju |  8.7   |
| ACADEMY DINOSAUR | Daniel Boianju |  9.8   |
+------------------+----------------+--------+

DatabaseReviewManager>python main.py
Please enter your ID: 1
Enter your first name: John
Enter your last name: Doe
Hello, John Doe
Please enter film name: african egg
Please enter rating for this film: 2
+------------------+-------------------+--------+
|      title       |     full_name     | rating |
+------------------+-------------------+--------+
|   AFRICAN EGG    |      John Doe     |  2.0   |
|    LUST LOCK     |   Daniel Boianju  |  8.7   |
| ACADEMY DINOSAUR |   Daniel Boianju  |  9.8   |
+------------------+-------------------+--------+
```
