import os
import mysql.connector
from dotenv import load_dotenv
import DatabaseInteract as di

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

    #create a databaseInteract object to interact with the MYSQL database
    dbi = di.DatabaseInteract(cnx)
    # checking weather the tables that will be used already exist
    dbi.VerifyTables()
    # getting a valid id from the user
    ID = dbi.getValidId()

    # getting the reviewer details
    reviewer_id, reviewer_first_name, reviewer_last_name = dbi.getReviewerDetails(ID)

    # greeting the reviewer
    print("Hello, " + reviewer_first_name + " " + reviewer_last_name)

    # getting a valid movie input from the user, the function makes sure that the movie exists
    film_choice, new_film_id = dbi.checkValidMovieName(ID)

    # asking the user to input a new rating for the movie.
    dbi.insertValidRating(new_film_id, ID)

    # print the current table of reviews
    table = dbi.getReviewTable()

    #printing the updated reviewer table
    print(table)
