import pyrebase
from configparser import ConfigParser
from random import randrange


'''-------------------------------------------
NOTE: Never use personal credentials directly onto the code
Copy this snippet and paste it in your code
 
SNIPPET STARTS

from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('config.ini')
api = twitter.Api(consumer_key=cfg['twitterAuth']['consumer_key'],
                  consumer_secret=cfg['twitterAuth']['consumer_secret'],
                  access_token_key=cfg['twitterAuth']['access_token_key'],
                  access_token_secret=cfg['twitterAuth']['access_token_secret'])

SNIPPET ENDS
-------------------------------------------'''

try:
    cfg = ConfigParser()
    cfg.read('config.ini')

    fdb = pyrebase.initialize_app({
      "apiKey": cfg['firebaseConfig']['apiKey'],
      "authDomain": cfg['firebaseConfig']["authDomain"],
      "databaseURL": cfg['firebaseConfig']["databaseURL"],
      "storageBucket": cfg['firebaseConfig']["storageBucket"]
    }).database()
except Exception as ex:
    print(ex)


def __get_item(reference):
    """
    Private function acts as the interface for accessing database

    PARAMETERS
    ------------
    :param reference: str
        url subdirectory to access data through firebase json

    RETURNS
    ------------
    :return: OrderedDict
        gets a json object as ordered dictionary from the reference parameter
    """
    try:
        return fdb.child(reference).get().val()
    except Exception as e:
        print(e)
        return False


def get_quote_data_from_tweet(tweet_id):
    """
    Gets entire quote data from given tweet id

    PARAMETERS
    ------------
    :param tweet_id: int
        posted tweet's tweet id

    RETURNS
    ------------
    :return: dictionary
        Dictionary with (Quote, Movie, Year) as keys
    """
    try:
        return __get_item("/open_tweets/"+str(tweet_id)+"/quote_id")
    except Exception as e:
        print(e)
        return False


def get_quote_data_from_id(quote_id):
    """
    Gets entire quote data from given quote id

    PARAMETERS
    ------------
    :param quote_id: int
        Quote ID for required quote

    RETURNS
    ------------
    :return: dictionary
        Dictionary with (Quote, Movie, Year) as keys
    """
    try:
        return __get_item("/quotes/"+str(quote_id))
    except Exception as e:
        print(e)
        return False


def get_random_quote_data():
    """
    Picks a random quote data from the database

    RETURNS
    ------------
    :return: dictionary
        Dictionary with (Quote, Movie, Year) as keys
    """
    try:
        all_quotes = __get_item('quotes')
        random_num = randrange(len(all_quotes))
        return all_quotes[random_num + 1]
    except Exception as e:
        print(e)
        return False


def get_random_movie():
    """
    Picks a random movie name from the database

    RETURNS
    ------------
    :return: str
        String with movie name
    """
    try:
        all_quotes = __get_item('quotes')
        random_num = randrange(len(all_quotes))
        return all_quotes[random_num]['Movie']
    except Exception as e:
        print(e)
        return False


def get_open_tweets():
    """
    Gets all the tweets from database

    RETURNS
    ------------
    :return: dictionary
        Dictionary with all current open tweets
    """
    try:
        return __get_item("/open_tweets")
    except Exception as e:
        print(e)
        return False


def push_tweet_in_db(tweet_id, quote_id, time_posted):
    """
    Pushes a new tweet into the database

    PARAMETERS
    ------------
    :param tweet_id: int
        posted tweet's tweet id
    :param quote_id: int
        the quote id of the quote used
    :param time_posted: str
        timestamp when tweet was posted

    RETURNS
    -----------
    :return: int
        1 if push is successful otherwise 0
    """
    try:
        data = {
            "quote_id": quote_id,
            "time_posted": time_posted,
            "hint_status": False,
            "last_updated": time_posted
        }
        fdb.child('open_tweets').child(tweet_id).set(data)
        return True
    except Exception as e:
        print(e)
        return False


def change_tweet_open_status(tweet_id):
    """
    Removes an open tweet

    PARAMETERS
    ------------
    :param tweet_id: int
        posted tweet's tweet id

    RETURNS
    ------------
    :return: boolean
        True if successful, False otherwise
    """

    try:
        fdb.child('open_tweets').child(tweet_id).remove()
        return True
    except Exception as e:
        print(e)
        return False


def change_tweet_hint_status(tweet_id, status):
    """
    Alters the hint status of a tweet

    PARAMETERS
    ------------
    :param tweet_id: int
        posted tweet's tweet id
    :param status: boolean
        mark status True if hint is given, False otherwise

    RETURNS
    ------------
    :return: boolean
        True if successful, False otherwise
    """

    try:
        fdb.child('open_tweets').child(tweet_id).update({'hint_status': status})
        return True
    except Exception as e:
        print(e)
        return False


def change_tweet_last_updated(tweet_id, status):
    """
    Alters the last_updated time of a tweet

    PARAMETERS
    ------------
    :param tweet_id: int
        posted tweet's tweet id
    :param status: str
        timestamp for the latest updated tweet

    RETURNS
    ------------
    :return: boolean
        True if successful, False otherwise
    """

    try:
        fdb.child('open_tweets').child(tweet_id).update({'last_updated': status})
        return True
    except Exception as e:
        print(e)
        return False

