import os
import mysql.connector
from prettytable import from_db_cursor
from dotenv import load_dotenv
import validData as vd



load_dotenv("root.env")


# the main function will do all of the required steps for inserting and manaring film reviews.
if __name__ == '__main__':
    # first, connecting to a database
    cnx = mysql.connector.connect(
        user='root',
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host='127.0.0.1',
        database='sakila'
    )

    #create a cursor object to work with the database
    cursor = cnx.cursor()
    # checking weather the tables that will be used already exist
    vd.VerifyTables(cnx)
    # getting a valid id from the user
    ID = vd.getValidId()

    #setting the cursor to enable prepared statements.
    cursor = cnx.cursor(prepared=True)

    # getting the reviewer details
    reviewer_id, reviewer_first_name, reviewer_last_name = vd.getReviewerDetails(ID)

    # greeting the reviewer
    print("Hello, " + reviewer_first_name + " " + reviewer_last_name)

    # getting a valid movie input from the user
    film_choice = vd.checkValidMovieName(ID)

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
    # if there are multiple records with this movie title, call a function to make the user choose one
    if count > 1:
        new_film_id = vd.getValidFilmIdFromMany(film_choice, query_select_film_table)
    # if there is only one record with this movie title
    else:
        # get the id of the film
        cursor.execute(query_select_film_table, [film_choice])
        new_film_id = cursor.fetchone()[0]

    # asking the user to input a new rating for the movie.
    vd.insertValidRating(new_film_id, ID)

    # print the current table of reviews
    cursor.execute("""SELECT film.title, CONCAT(reviewer.first_name, \" \", reviewer.last_name)
                            AS full_name, rating.rating
                        FROM film, rating, reviewer
                        WHERE film.film_id = rating.film_id
                        AND reviewer.reviewer_id = rating.reviewer_id
                        LIMIT 100""")
    table = from_db_cursor(cursor)
    print(table)
