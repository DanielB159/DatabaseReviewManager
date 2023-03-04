import os
import mysql.connector
from prettytable import from_db_cursor
from dotenv import load_dotenv

load_dotenv("root.env")


# this function will check weather a table exists
def check_if_table_exists(cnx, table_name):
    cursor = cnx.cursor()
    # selecting all the tables i=with this name
    cursor.execute("""
        SELECT COUNT(TABLE_NAME)
        FROM information_schema.tables
        WHERE TABLE_NAME = %s;
        """, [table_name])
    if cursor.fetchone()[0] == 1:
        return True
    return False


# this function makes sure that the id that is given is valid.
def getValidId():
    ID = input("Please enter your ID: ")
    idFlag = False  # idflag will indicate weather the ID is valid or not.
    while not idFlag:
        try:
            cursor.execute("SELECT COUNT(reviewer.reviewer_id) FROM reviewer WHERE reviewer.reviewer_id = %s", [ID])
            num = cursor.fetchone()[0]
            if (num != 0):
                idFlag = True
            else:
                cursor.execute("INSERT INTO reviewer VALUES(%s, null, null)", [ID])
                cursor.execute("DELETE FROM reviewer WHERE reviewer_id = %s", [ID])
                idFlag = True
                cnx.commit()
        except:
            ID = input("Please enter a valid id: ")
            cnx.rollback()
    return ID


# this function checks weather the needed tables exist in the DB
def checkIfTablesExist(cnx):
    if not check_if_table_exists(cnx, "reviewer"):
        cursor.execute("""CREATE TABLE reviewer (
            reviewer_id INT NOT NULL,
            first_name VARCHAR(45),
            last_name VARCHAR(45),
            PRIMARY KEY(reviewer_id));   
        """)

    if not check_if_table_exists(cnx, "rating"):
        cursor.execute("""CREATE TABLE rating (
            film_id SMALLINT UNSIGNED AUTO_INCREMENT,
            reviewer_id INT NOT NULL,
            rating DECIMAL(2,1) NOT NULL, 
            PRIMARY KEY(film_id, reviewer_id),
            CHECK(rating < 10 and rating >= 0),
            FOREIGN KEY(film_id) 
				REFERENCES film(film_id)
				ON UPDATE CASCADE
                ON DELETE CASCADE,
			FOREIGN KEY(reviewer_id) 
				REFERENCES reviewer(reviewer_id)
				ON UPDATE CASCADE
                ON DELETE CASCADE);
        """)


# this function will return the reviewer details
def getReviewerDetails(ID):
    # setting up a query to check weather the id is in the database
    query_reviewer_id = """SELECT reviewer.reviewer_id
                    FROM reviewer
                    WHERE reviewer_id = %s;
    """
    cursor.execute(query_reviewer_id, [ID])
    result = cursor.fetchone()
    # if the id is not in the database
    if result is None:
        nameFlag = False
        while not nameFlag:
            # ask for details and insert them to database.
            reviewer_first_name = input("Enter your first name: ")
            reviewer_last_name = input("Enter your last name: ")
            try:
                query_insert_reviewer = "INSERT INTO reviewer VALUES(%s, %s, %s)"
                reviewer_id = ID
                cursor.execute(query_insert_reviewer, (ID, reviewer_first_name, reviewer_last_name))
                cnx.commit()
                nameFlag = True
            except:
                cnx.rollback()
                print("please enter valid first and last name.")
        # if the id is already in the database, get the first and last name.
    else:
        cursor.execute("""SELECT reviewer.reviewer_id, reviewer.first_name, reviewer.last_name
                    FROM reviewer
                    WHERE reviewer_id = %s; 
        """, [ID])
        reviewer_id, reviewer_first_name, reviewer_last_name = cursor.fetchone()
    return (reviewer_id, reviewer_first_name, reviewer_last_name)


# this function will check weather the name of the movie is valid.
def checkValidMovieName(ID):
    film_name = input("Please enter film name: ")
    # defining a query to check weather this title exists
    query_select_title = """SELECT film.title, film.film_id
                    FROM film
                    WHERE title = %s
    """
    cursor.execute(query_select_title, [film_name])
    film_choice_tuple = cursor.fetchone()
    reviewFlag = False  # notifying if there is a review currently in the database
    # now, settign up check if this user has already submitted a review for this movie.
    query_select_film = """SELECT COUNT(rating.film_id), rating.reviewer_id
                        FROM rating
                        WHERE rating.film_id = %s and rating.reviewer_id = %s
                        GROUP BY rating.reviewer_id
        """
    # if there is a movie with this title, checking weather the user has already submitted a review
    if film_choice_tuple is not None:
        film_choice, new_film_id = film_choice_tuple[0], film_choice_tuple[1]
        # running check weather review exists
        cursor.execute(query_select_film, [new_film_id, ID])
        print(cursor.fetchone())
        if cursor.fetchone() == None:
            numOfReviews = 0
        else:
            numOfReviews = cursor.fetchone()[0]
        # if there are no reviews, set the reviewFlag to be True
        if numOfReviews == 0:
            reviewFlag = True
    # this while loop will enter if the film name is invalid or the user has already submitted a review for this film.
    while film_choice_tuple is None or not reviewFlag:
        # getting another input
        film_name = input("film doesn't exist in film table, or you have already reviewed this film.""" +
                          """ please enter a valid name: """)
        cursor.execute(query_select_title, [film_name])
        film_choice_tuple = cursor.fetchone()
        # if the title is valid, check again if there is a review already.
        if film_choice_tuple is not None:
            film_choice, new_film_id = film_choice_tuple[0], film_choice_tuple[1]
            cursor.execute(query_select_film, [new_film_id, ID])
            if cursor.fetchone() == None:
                numOfReviews = 0
            else:
                numOfReviews = cursor.fetchone()[0]
            # if there are no reviews, set the reviewFlag to be True
            if numOfReviews == 0:
                reviewFlag = True
    return film_choice


def getValidFilmId(film_choice, query_select_film_table):
    print("There are multiple records of this title, please enter the id of your choice: \n")
    # print all of the movies with this title
    cursor.execute(query_select_film_table, [film_choice])
    my_table = from_db_cursor(cursor)
    print(my_table)
    movieIdflag = False
    while not movieIdflag:
        # asking the user to choose a valid movie id
        new_film_id = int(input("please choose a valid film id: "))
        cursor.execute(query_select_film_table, [film_choice])
        result = cursor.fetchall()
        # checking if the movie id is valid
        for record in result:
            if record[0] == new_film_id:
                movieIdflag = True
    return new_film_id


def insertValidRating(new_film_id, ID):
    reviewer_rating = input("Please enter rating for this film: ")
    rating_flag = False
    # this while loop makes sure that the rating is valid
    while not rating_flag:
        try:
            # check if negative. If so, will except
            if float(reviewer_rating) < 0:
                raise Exception("negative number")
            # try to insert to rating table. if fails, will except
            cursor.execute("INSERT INTO rating VALUES(%s, %s, %s)", [new_film_id, ID, reviewer_rating])
            cnx.commit()
            rating_flag = True
        except:
            cnx.rollback()
            # asking the user for a valid input
            reviewer_rating = input("""the rating must be larger than 0.0 and smaller """
                                    + """than 10.0. enter a new rating please: """)


# the main function will do all of the required steps for inserting and manaring film reviews.
if __name__ == '__main__':
    # first, connecting to a database
    cnx = mysql.connector.connect(
        user='root',
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host='127.0.0.1',
        database='sakila'
    )

    cursor = cnx.cursor()
    # checking weather the tables that will be used already exist
    checkIfTablesExist(cnx)
    # getting a valid id from the user
    ID = getValidId()
    cursor = cnx.cursor(prepared=True)

    # getting the reviewer details
    reviewer_id, reviewer_first_name, reviewer_last_name = getReviewerDetails(ID)

    # greeting the reviewer
    print("Hello, " + reviewer_first_name + " " + reviewer_last_name)

    # getting a valid movie input from the user
    film_choice = checkValidMovieName(ID)

    # checking the amount of movies with this title
    cursor.execute("""SELECT COUNT(film.title)
                    FROM film
                    WHERE film.title = %s
                    """, [film_choice])
    count = cursor.fetchone()[0]
    new_film_id = 0
    # setting up a query to to get the film details
    query_select_film_table = """SELECT film_id, film.title, film.release_year
                    FROM film
                    WHERE film.title = %s
                    """
    # if there are multiple records with this movie title
    if count > 1:
        new_film_id = getValidFilmId(film_choice, query_select_film_table)
    # if there is only one record with this movie title
    else:
        # get the id of the film
        cursor.execute(query_select_film_table, [film_choice])
        new_film_id = cursor.fetchone()[0]

    # asking the user to input a new rating for the movie.
    insertValidRating(new_film_id, ID)

    # print the current table of reviews
    cursor.execute("""SELECT film.title, CONCAT(reviewer.first_name, \" \", reviewer.last_name)
                            AS full_name, rating.rating
                        FROM film, rating, reviewer
                        WHERE film.film_id = rating.film_id
                        AND reviewer.reviewer_id = rating.reviewer_id
                        LIMIT 100""")
    table = from_db_cursor(cursor)
    print(table)
