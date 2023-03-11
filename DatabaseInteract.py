from prettytable import from_db_cursor

'''
The DatabaseInteract class is a class meant for interacting with the 'sakila' database using the MYSQL server.
it has a cnx object and a database cursor object as its fields and uses them in its methods.
'''
class DatabaseInteract:
    def __init__(self, cnx):
        #setting the fields of the DatabaseInteract Object
        self.cnx = cnx
        self.cursor = cnx.cursor()
    
    # this method will check weather a table exists
    def check_if_table_exists(self, table_name):
        # selecting all the tables i=with this name
        self.cursor.execute("""
            SELECT COUNT(TABLE_NAME)
            FROM information_schema.tables
            WHERE TABLE_NAME = %s;
            """, [table_name])
        if self.cursor.fetchone()[0] == 1:
            return True
        return False


    # this method will return the review table with the names of the reviewers included
    def getReviewTable(self):
        self.cursor.execute("""SELECT film.title, CONCAT(reviewer.first_name, \" \", reviewer.last_name)
                            AS full_name, rating.rating
                        FROM film, rating, reviewer
                        WHERE film.film_id = rating.film_id
                        AND reviewer.reviewer_id = rating.reviewer_id
                        LIMIT 100""")
        return from_db_cursor(self.cursor)

    # this method makes sure that the id that is given is valid.
    def getValidId(self):
        ID = input("Please enter your ID: ")
        idFlag = False  # idflag will indicate weather the ID is valid or not.
        while not idFlag:
            try:
                self.cursor.execute("SELECT COUNT(reviewer.reviewer_id) FROM reviewer WHERE reviewer.reviewer_id = %s", [ID])
                num = self.cursor.fetchone()[0]
                if (num != 0):
                    idFlag = True
                else:
                    self.cursor.execute("INSERT INTO reviewer VALUES(%s, null, null)", [ID])
                    self.cursor.execute("DELETE FROM reviewer WHERE reviewer_id = %s", [ID])
                    idFlag = True
                    self.cnx.commit()
            except:
                ID = input("Please enter a valid id: ")
                self.cnx.rollback()
        return ID


    # this method checks weather the reviewer and rating tables exist in the DB. If not, it creates them.
    def VerifyTables(self):
        if not self.check_if_table_exists("reviewer"):
            self.cursor.execute("""CREATE TABLE reviewer (
                reviewer_id INT NOT NULL,
                first_name VARCHAR(45),
                last_name VARCHAR(45),
                PRIMARY KEY(reviewer_id));   
            """)

        if not self.check_if_table_exists("rating"):
            self.cursor.execute("""CREATE TABLE rating (
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

    # this method will return the reviewer details
    def getReviewerDetails(self,ID):
        # setting up a query to check weather the id is in the database
        query_reviewer_id = """SELECT reviewer.reviewer_id
                        FROM reviewer
                        WHERE reviewer_id = %s;
        """
        self.cursor.execute(query_reviewer_id, [ID])
        result = self.cursor.fetchone()
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
                    self.cursor.execute(query_insert_reviewer, (ID, reviewer_first_name, reviewer_last_name))
                    self.cnx.commit()
                    nameFlag = True
                except:
                    self.cnx.rollback()
                    print("please enter valid first and last name.")
            # if the id is already in the database, get the first and last name.
        else:
            self.cursor.execute("""SELECT reviewer.reviewer_id, reviewer.first_name, reviewer.last_name
                        FROM reviewer
                        WHERE reviewer_id = %s; 
            """, [ID])
            reviewer_id, reviewer_first_name, reviewer_last_name = self.cursor.fetchone()
        return (reviewer_id, reviewer_first_name, reviewer_last_name)

    #this method is used when there are multiple films with the same title. it makes the user choose one.
    def getValidFilmIdFromMany(self, film_choice, query_select_film_table):
        print("There are multiple records of this title, please enter the id of your choice: \n")
        # print all of the movies with this title
        self.cursor.execute(query_select_film_table, [film_choice])
        my_table = from_db_cursor(self.cursor)
        print(my_table)
        movieIdflag = False
        while not movieIdflag:
            # asking the user to choose a valid movie id
            try:
                new_film_id = int(input("please choose a valid film id: "))
                self.cursor.execute(query_select_film_table, [film_choice])
                result = self.cursor.fetchall()
                # checking if the movie id is valid
                for record in result:
                    if record[0] == new_film_id:
                        movieIdflag = True
            except:
                pass
        return new_film_id

    '''
    this method gets a movie title (film_choice) and returns a movie id, movie title that the user intended.
    given that there can be multiple movies with the same title, if that is the case the method asks the user to choose
    one of them using the getValidFilmIdFromMany function.
    '''
    def assertSingleMovieChoice(self, film_choice):
        #first, empty out any remaining results, if there are any.
        dummy = self.cursor.fetchall()
        # checking the amount of movies with this title. the amount can be one or more
        self.cursor.execute("""SELECT COUNT(film.title)
                        FROM film
                        WHERE film.title = %s
                        """, [film_choice])
        count = self.cursor.fetchone()[0]
        # setting up a query to to get the film details
        query_select_film_table = """SELECT film_id, title
                        FROM film
                        WHERE film.title = %s
                        """
        # if there are multiple records with this movie title, call a function to make the user choose one
        if count > 1:
            new_film_id = self.getValidFilmIdFromMany(film_choice, query_select_film_table)
        # if there is only one record with this movie title
        else:
            # get the id of the film
            self.cursor.execute(query_select_film_table, [film_choice])
            new_film_id = self.cursor.fetchone()[0]
        return new_film_id

    # this method will ask user for movie name and check weather the name of the movie is valid.
    def checkValidMovieName(self, ID):
        film_name = input("Please enter film name: ")
        # defining a query to check weather this title exists
        query_select_title = """SELECT film.title, film.film_id
                        FROM film
                        WHERE title = %s
        """
        self.cursor.execute(query_select_title, [film_name])
        #setting film_choice_tuple to be oen row of the result
        film_choice_tuple = self.cursor.fetchone()
        reviewFlag = False  # notifying if there is a review currently in the database
        # now, settign up check if this user has already submitted a review for this movie.
        query_select_film = """SELECT COUNT(rating.film_id), rating.reviewer_id
                            FROM rating
                            WHERE rating.film_id = %s and rating.reviewer_id = %s
                            GROUP BY rating.reviewer_id
            """
        # if there is a movie with this title, checking weather the user has already submitted a review
        if film_choice_tuple is not None:
            #if there are more results, fetching all of them
            dummy = self.cursor.fetchall()
            new_film_id = self.assertSingleMovieChoice(film_name)
            # running check weather review exists
            self.cursor.execute(query_select_film, [new_film_id, ID])
            tupleResult = self.cursor.fetchone()
            if tupleResult == None:
                numOfReviews = 0
            else:
                numOfReviews = tupleResult[0]
            # if there are no reviews, set the reviewFlag to be True
            if numOfReviews == 0:
                reviewFlag = True
        # this while loop will enter if the film name is invalid or the user has already submitted a review for this film.
        while film_choice_tuple is None or not reviewFlag:
            # getting another input
            film_name = input("film doesn't exist in film table, or you have already reviewed this film.""" +
                            """ please enter a valid name: """)
            dummy = self.cursor.fetchall()
            self.cursor.execute(query_select_title, [film_name])
            film_choice_tuple = self.cursor.fetchone()
            # if the title is valid, check again if there is a review already.
            if film_choice_tuple is not None:
                new_film_id = self.assertSingleMovieChoice(film_name)
                self.cursor.execute(query_select_film, [new_film_id, ID])
                outputRow = self.cursor.fetchone() 
                if outputRow == None:
                    numOfReviews = 0
                else:
                    numOfReviews = outputRow[0]
                # if there are no reviews, set the reviewFlag to be True
                if numOfReviews == 0:
                    reviewFlag = True
        return film_name, new_film_id


    #this method asks the user for a rating for the movie with the inputted movie id and inserts it into the database
    def insertValidRating(self, new_film_id, ID):
        reviewer_rating = input("Please enter rating for this film: ")
        rating_flag = False
        # this while loop makes sure that the rating is valid
        while not rating_flag:
            try:
                # check if negative. If so, will except
                if float(reviewer_rating) < 0:
                    raise Exception("negative number")
                # try to insert to rating table. if fails, will except
                self.cursor.execute("INSERT INTO rating VALUES(%s, %s, %s)", [new_film_id, ID, reviewer_rating])
                self.cnx.commit()
                rating_flag = True
            except Exception as e:
                self.cnx.rollback()
                # asking the user for a valid input
                reviewer_rating = input("""the rating must be at least 0.0 and smaller """
                                        + """than 10.0. enter a new rating please: """)
    
    
   