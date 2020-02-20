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


cfg = ConfigParser()
cfg.read('config.ini')

fdb = pyrebase.initialize_app({
  "apiKey": cfg['firebaseConfig']['apiKey'],
  "authDomain": cfg['firebaseConfig']["authDomain"],
  "databaseURL": cfg['firebaseConfig']["databaseURL"],
  "storageBucket": cfg['firebaseConfig']["storageBucket"]
}).database()


# Private function acts as the interface for accessing database
def __get_item(reference):
    return fdb.child(reference).get().val()


# Gets entire quote data from given tweet id
# Returns a dictionary with (Quote, Movie, Year) as keys
def get_quote_data_from_tweet(tweet_id):
    return __get_item("/open_tweets/"+str(tweet_id)+"/quote_id")


# Gets entire quote data from given quote id
# Returns a dictionary with (Quote, Movie, Year) as keys
def get_quote_data_from_id(quote_id):
    return __get_item("/quotes/"+str(quote_id))


# Picks a random quote data from the database
# Returns a dictionary with (Quote, Movie, Year) as keys
def get_random_quote_data():
    all_quotes = __get_item('quotes')
    random_num = randrange(len(all_quotes))
    return all_quotes[random_num + 1]


# Picks a random movie name from the database
# Returns a string with movie name
def get_random_movie():
    all_quotes = __get_item('quotes')
    random_num = randrange(len(all_quotes))
    return all_quotes[random_num]['Movie']


# Pushes a new tweet into the database
#
# ARGUMENTS
# tweet_id : posted tweet's tweet id
# quote_id : the quote id of the quote used
# time_posted : timestamp when tweet was posted
#
# OUTPUT
# Return 1 if push is successful otherwise 0
def push_tweet_in_db(tweet_id, quote_id, time_posted):
    try:
        data = {
          "quote_id": quote_id,
          "time_posted": time_posted,
          "tweet_open": True
        }
        fdb.child('open_tweets').child(tweet_id).set(data)
        return 1
    except:
        return 0


# Alters the status of an open tweet
#
# ARGUMENTS
# tweet_id : posted tweet's tweet id
#
# OUTPUT
# Return 1 if update is successful otherwise 0
def change_tweet_status(tweet_id):
    try:
        fdb.child('open_tweets').child(tweet_id).update({'tweet_open': False})
        return 1
    except:
        return 0

