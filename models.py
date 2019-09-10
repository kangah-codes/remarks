__author__ = "Joshua Akangah"

import sqlite3
import string
import random
import datetime


def gen_event_id(size=6, chars=string.ascii_uppercase+string.digits):
    """
    Function to generate an event id
    :param size: size of the alphanumeric
    :param chars: Characters to include
    :return: 6 digit alphanumeric
    """
    return ''.join(random.choice(chars) for _ in range(size))


def gen_post_id(size=6, chars=string.ascii_lowercase+string.digits+string.ascii_uppercase):
    """
    Function to generate a random alphanumeric 6 digit code
    :param size: The size of the id to generate
    :param chars: Characters to include in the key
    :return: 6 digit alphanumeric
    """
    return ''.join(random.choice(chars) for _ in range(size))


class Database:
    """
    Database class for all events and posts in the web app
    This database object would control all objects such as adding items to the database, deleting, updating etc.
    """
    def __init__(self, name='remarks.db'):
        """
        Init method
        :param name: name of the database
        """
        self.db_name = name
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        except sqlite3.OperationalError:
            # raise sqlite3.OperationalError('Could not connect to the database file')
            pass
        finally:
            self.connection.close()

    def create_table(self, event_table_name, post_table_name):
        """
        create tables for the events
        :param event_table_name: table name for event
        :param post_table_name: table name for posts
        :return: bool, sqlite3.operationalerror
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"""
                CREATE TABLE {event_table_name}
                    (ID CHAR(6) PRIMARY KEY UNIQUE,
                    NAME TEXT NOT NULL UNIQUE,
                    DATEOF DATE NOT NULL,
                    DESCRIPTION TEXT NOT NULL,
                    POSTS TEXT NOT NULL,
                    LOCATION TEXT NOT NULL,
                    PRICE REAL NOT NULL,
                    RATING REAL)
            """)
            self.cursor.execute(f"""
                CREATE TABLE {post_table_name}
                    (ID CHAR(6) PRIMARY KEY UNIQUE,
                    WRITER TEXT NOT NULL,
                    BODY TEXT NOT NULL,
                    DATEOF DATE NOT NULL,
                    PARENT_EVENT CHAR(6) NOT NULL,
                    STARS REAL NOT NULL)
            """)
            self.connection.commit()
            return True
        except sqlite3.OperationalError:
            return False
        finally:
            self.connection.close()

    def create_event(self, table_name, event_name, event_date, event_desc, location, price, rating=5.0, event_posts=''):
        """
        Create an event
        :param table_name: Table name for events
        :param event_name: name of event
        :param event_date: date
        :param event_desc: description
        :param event_posts: posts
        :return: bool, sqlite3.operationalerror
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            # generating event id
            gen_id = gen_event_id()

            # checking if event exists
            self.cursor.execute(
                f"""
                SELECT ID FROM {table_name} WHERE ID='{gen_id}'
                """
            )
            length = len(self.cursor.fetchall())
            while length != 0:
                # generate a new id if that id already exists
                gen_id = gen_event_id()

                self.cursor.execute(
                    f"""
                    SELECT ID FROM {table_name} WHERE ID='{gen_id}'
                    """
                )

                length = len(self.cursor.fetchall())

            self.cursor.execute(
                f"""
                INSERT INTO {table_name}
                (ID, NAME, DATEOF, DESCRIPTION, POSTS, LOCATION, PRICE, RATING)
                VALUES
                ('{gen_id}', "{event_name}", '{event_date}', "{event_desc}", '{event_posts}', '{location}', '{price}', '{rating}')
                """
            )
            self.connection.commit()
            return True
        except sqlite3.OperationalError:
            return False
        except sqlite3.IntegrityError:
            return False
            #print(e)
        finally:
            self.connection.close()

    def create_post(self, table_name, writer, body, event, date, event_table_name, stars):
        """
        Create a post
        :param table_name: table name for posts
        :param writer: writer of the posts
        :param body: body of the post
        :param event: parent event of the post
        :param date: date post was written
        :param event_table_name: table name for event
        :param stars: star rating of the event
        :return: bool, sqlite3.operationalerror
        """
        # add stars to posts
        try:
            """
            Creating a post
            1. First check the event
                a. If event is true
                    i. Return all posts in that event as a string
                    ii. Add the id of current post
                    iii. Update the posts section
                b. Else
                    i. Throw OperationalError
            2. Add the current post to its own database
            """
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            gen_id = gen_post_id()

            # validate the event first
            try:
                # validate event
                self.cursor.execute(
                    f"""
                        SELECT POSTS FROM {event_table_name} WHERE ID='{event}'
                    """
                )
                # if event exists
                if len(self.cursor.fetchall()) != 0:
                    # validate the post id

                    self.cursor.execute(
                        f"""
                        SELECT ID FROM {table_name} WHERE ID='{gen_id}'
                        """
                    )
                    length = len(self.cursor.fetchall())
                    while length != 0:
                        # generate a new id if that id already exists
                        # continue in a loop until a unique id is generated 
                        gen_id = gen_post_id()

                        self.cursor.execute(
                            f"""
                            SELECT ID FROM {table_name} WHERE ID='{gen_id}'
                            """
                        )

                        length = len(self.cursor.fetchall())

                    # post id has benn validated

                    self.cursor.execute(
                        f"""
                        SELECT POSTS FROM {event_table_name} WHERE ID='{event}'
                        """
                    )
                    # add current post to the event posts
                    returned_post = self.cursor.fetchone()[0]+gen_id+'/'
                    self.cursor.execute(
                        f"""
                        UPDATE EVENT SET POSTS='{returned_post}' WHERE ID='{event}'
                        """
                    )
                    self.connection.commit()
                    self.cursor.execute(
                        f"""
                            INSERT INTO {table_name}
                            (ID, WRITER, BODY, DATEOF, PARENT_EVENT, STARS)
                            VALUES
                            ('{gen_id}', '{writer}', "{body}", '{date}', '{event}', '{stars}')
                        """
                    )

                    # calculating the rating for the event
                    self.cursor.execute(
                        f"""
                        SELECT RATING FROM {event_table_name} WHERE ID='{event}'
                        """
                    )
                    event_rating = self.cursor.fetchone()[0]
                    rating = []

                    self.connection.commit()

                    for _ in self.return_child_posts('event', event, 'post'):
                        rating.append(_[5])
                        #print(_)

                    #3print(event_rating)

                    #print(self.return_child_posts(event_table_name, event, table_name))

                    # for _ in child_posts:
                    #     print(_)
                    
                    #return True
                    self.connection = sqlite3.connect(self.db_name)
                    self.cursor = self.connection.cursor()
                    
                    self.cursor.execute(
                        f"""
                        UPDATE EVENT SET RATING='{sum(rating)/len(rating)}' WHERE ID='{event}'
                        """
                    )

                    self.connection.commit()
                    

                else:
                    # raise sqlite3.OperationalError('Event does not exist')
                    return False

            except sqlite3.OperationalError:
                return False

        except sqlite3.OperationalError:
            return False

        finally:
            self.connection.close()

    def return_events(self, event_table_name, select_all=True, event_id=None):
        """
        Return all the events in the database
        :param event_table_name: table name for the event
        :param select_all:
            :type: bool
            :description: whether to return all events in the database or to return just one
        :param event_id: if all=True, specify the id of the event you want returned
        :return: tuple
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()

            if select_all:
                self.cursor.execute(
                    f"""
                        SELECT * FROM {event_table_name} ORDER BY DATEOF DESC
                    """
                )

                return self.cursor.fetchall()

            # if selecting just one event
            self.cursor.execute(
                f"""
                    SELECT * FROM {event_table_name} WHERE ID='{event_id}'
                """
            )
            return self.cursor.fetchone()

        except sqlite3.OperationalError:
            return False

        finally:
            self.connection.close()

    def delete_event(self, event_id, event_table_name, post_table_name):
        """
        delete an event from the database
        :param event_id: id of event to delete
        :param event_table_name: table name of event
        :param post_table_name: table name of post
        :return: bool, sqlite3.operationalerror
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()

            self.cursor.execute(
                f"""
                SELECT POSTS FROM {event_table_name} WHERE ID='{event_id}'
                """
            )

            try:

                event_posts = self.cursor.fetchone()[0].split('/')
                """
                removing the last string because it is an 
                empty string and does not contain any 
                post id
                """
                event_posts.pop(-1)

                # delete all posts
                for post in event_posts:
                    self.cursor.execute(
                        f"""
                        DELETE FROM {post_table_name} WHERE ID='{post}'
                        """
                    )

                # self.connection.commit()

                # delete event itself
                self.cursor.execute(
                    f"""
                    DELETE FROM {event_table_name} WHERE ID='{event_id}'
                    """
                )

                # commit changes
                self.connection.commit()
                return True

            except TypeError:
                return Falseid

        except sqlite3.OperationalError:
            return False

        finally:
            self.connection.close()

    def return_child_posts(self, event_table_name, event_id, post_table_name):
        """
        return all posts which belong to an event
        :param event_table_name: event table
        :param event_id: event id to fetch child posts from
        :param post_table_name: post table
        :return: list, typeError, sqlite3.operationalerror
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()

            self.cursor.execute(
                f"""
                SELECT POSTS FROM {event_table_name} WHERE ID='{event_id}'
                """
            )

            try:
                selected_posts = self.cursor.fetchone()[0].split('/')
                selected_posts.pop(-1)
                all_posts = []

                for _ in selected_posts:
                    self.cursor.execute(
                        f"""
                        SELECT * FROM {post_table_name} WHERE ID='{_}'
                        """
                    )
                    all_posts.append(self.cursor.fetchone())
                    #print(self.cursor.fetchone())

                return all_posts          

            except TypeError:
                # event does not exist
                return False

        except sqlite3.OperationalError:
            return False

        finally:
            self.connection.close()

    def return_child_post_ids(self,event_table_name, event_id, post_table_name):
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()

            self.cursor.execute(
                f"""
                SELECT POSTS FROM {event_table_name} WHERE ID='{event_id}'
                """
            )

            try:
                selected_posts = self.cursor.fetchone()[0].split('/')
                selected_posts.pop(-1)

                return selected_posts        

            except TypeError:
                # event does not exist
                return False

        except sqlite3.OperationalError:
            return False

        finally:
            self.connection.close()

    def search_event(self, event_table_name, query):
        """
        Find an event
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()

            self.cursor.execute(
                f"""
                SELECT * FROM {event_table_name} WHERE NAME LIKE '%{query}%' OR ID LIKE '%{query}%' ORDER BY NAME ASC
                """
            )

            return self.cursor.fetchall()

        except sqlite3.OperationalError:
            return False

        finally:
            self.connection.close()
d = Database()
#print(d.create_table('event', 'post'))
#print(d.create_event('event', 'MARLEY', datetime.datetime.today(), "HHH IUHU IHushduifhduifhsdiufh sduihfui sdhfiusdhfuis hadiufhasdui gfusdagfu eagdsufewguknsdyugfyuagdshfgdsjfgaewagsgesyu", "Accra", 0, rating=1.4, event_posts=''))
#print(d.create_post('post', 'Joshua', 'Enjoyed it', 'BWSUVW', datetime.datetime.today(), 'event', 3.6))

# print(d.search_event('event', 'cqm'))
#print(d.return_child_posts('event', 'F1UTOS', 'post'))

#print(d.create_post('post', 'Josh', 'Hated this event!!', 'S96MGO', datetime.datetime.today(), 'event', 1.9))
#print(d.return_child_posts('event', 'F1UTOS', 'post'))
