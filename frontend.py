import twitter
import json
from datetime import datetime, timedelta
import random
import pytz
import backend
from configparser import ConfigParser
import database as db
# import pdb

#Global variables

cfg = ConfigParser()
cfg.read('config.ini')
api = twitter.Api(consumer_key=cfg['twitterAuth']['consumer_key'],
                  consumer_secret=cfg['twitterAuth']['consumer_secret'],
                  access_token_key=cfg['twitterAuth']['access_token_key'],
                  access_token_secret=cfg['twitterAuth']['access_token_secret'])


# #Api Keys added
# api = twitter.Api(consumer_key='77fIyHnx653Nnx0W4Iz4XRua9',
#                   consumer_secret='rG0FQNYliP2jlab2Nf0VYm83a3iC0UUFmyOetHd8aaD4nSa4aE',
#                   access_token_key='1227546694969167873-6Feip4gF0vg0DJxN38yLWCrPIVNYVt',
#                   access_token_secret='rOozbozQIqpy5JonuSrlkxq7d4NXSeIjhUCjtotVgZeHJ')

#Timing variables
posting_frequency = 300 #makes post every $posting_frequency$ seconds
last_tweet_time = datetime.now() - timedelta(seconds=posting_frequency+100)

tweet_lifetime = 360  # closes tweet if its older than $posting_frequency$ seconds

reply_frequency = 30 #checks for replies every $posting_frequency$ seconds
last_reply_check_time =datetime.now() - timedelta(seconds=reply_frequency+100)

#Tweet history
# contains: tweet status message, quote info, tweet status (0 unanswered, 1 hint has been given), last time we checked for replies
previous_tweet_list = []


def twitterBot():
    """
       The main function
       Responsible for timing and keeping to Twitter API rate limits
    """
    global last_tweet_time,last_reply_check_time, posting_frequency, reply_frequency, previous_tweet_list, tweet_lifetime

    while True:
        """
        Checks if it is time to tweet a new tweet
        """

        if (datetime.now()-last_tweet_time)>timedelta(seconds=posting_frequency):
            #respond to previous tweets
            open_tweets = db.get_open_tweets()
            if open_tweets:
                for i in open_tweets:
                    checkReply(i, open_tweets)

            open_tweets = db.get_open_tweets()
            if open_tweets:
                for i in open_tweets:
                    print(i)
                    # open_tweet_time = datetime.strptime(open_tweets[i]["time_posted"], '%Y-%m-%d %H:%M:%S')
                    print (open_tweets[i]["time_posted"])
                    open_tweet_time = datetime.fromisoformat(open_tweets[i]["time_posted"])
                    if (open_tweet_time<getAwareTime(datetime.now()-timedelta(seconds=tweet_lifetime))):
                        quote_data = db.get_quote_data_from_tweet(i)
                        movie = quote_data['Movie']
                        body = noReplies(movie)
                        print (body)
                        result = api.PostUpdate(body, in_reply_to_status_id=i)
                        print("Removed tweet " + str(i))
                        db.change_tweet_open_status(i)


            #Here calls funtion to get new quote

            new_quote, quote_id = db.get_random_quote_data()
            print (new_quote)
            print (quote_id)

            status = api.PostUpdate(str(generateQuoteQuestion(new_quote["Quote"])))
            tweet_time_str = status._json["created_at"]
            tweet_time = datetime.strptime(tweet_time_str, '%a %b %d %H:%M:%S %z %Y')
            print(db.push_tweet_in_db(status._json["id"], quote_id, str(tweet_time)))

            # q = [status, new_quote, 0, getAwareTime(datetime.now())]
            # previous_tweet_list.append(q)
            # print (previous_tweet_list)
            print ("Tweeted")

            last_tweet_time = datetime.now()

        """
        Check for replies
        """

        if (datetime.now() - last_reply_check_time) > timedelta(seconds=reply_frequency):
            print("check for replies")
            #filler message
            # previous_tweet_list.append ([api.GetStatus(1230969409587556352),"hello",0,getAwareTime(datetime.now())])
            open_tweets = db.get_open_tweets()
            # print (open_tweets)
            if open_tweets:
                for t in open_tweets:
                   checkReply(t, open_tweets)
            last_reply_check_time = datetime.now()

def checkReply(t,open_tweets):
    """
   Checks replies to a specific tweet

   PARAMETERS
   ------------
   :param t: int
       tweet id of the speciifc tweet

       open_tweets: list
       contains twitter.status objects of all open tweets

   RETURNS
   ------------
    No return
   """
    # print ("Check replies " + str(t))
    replies = getReplies(t)
    db.change_tweet_last_updated(t, str(getAwareTime(datetime.now())))
    for r in replies:
        # print ("reply")
        # print (r)
        tweet_time_str = r._json["created_at"]
        tweet_time = datetime.strptime(tweet_time_str, '%a %b %d %H:%M:%S %z %Y')
        open_tweet_time = datetime.fromisoformat(open_tweets[t]["last_updated"])

        # print (open_tweet_time < tweet_time)
        # print (open_tweet_time)
        # print (tweet_time)
        if (open_tweet_time < tweet_time and r._json["user"]["screen_name"] != "ThatOldMovieGu1"):
            print (r)
            quote_data = db.get_quote_data_from_tweet(t)
            movie = quote_data['Movie']
            correctness = backend.answer_checker(t, str(r._json["text"]).replace("@ThatOldMovieGu1 ", "").strip())
            # print (correctness)
            answer = answerGenerator(movie, r._json["user"]["screen_name"], int(correctness))
            # print (movie)
            # print (r._json["user"]["screen_name"])
            print (answer)
            # print (r._json["id"])
            if correctness==1 or db.tweet_within_response_limit(t):
                status = api.PostUpdate("@" + str(r._json["user"]["screen_name"]) + " " + str(answer), in_reply_to_status_id=r._json["id"])

            if (correctness != 1 and open_tweets[t]["hint_status"] == False):
                print ("hint")
                db.change_tweet_hint_status(t, True)
                open_tweets[t]["hint_status"] = True
                movie_hint = backend.movie_hint(open_tweets[t]["quote_id"])
                body = hint(movie_hint)
                status = api.PostUpdate(body, in_reply_to_status_id=t)
                print (status)

            if (correctness == 1):
                db.change_tweet_open_status(t)
                print ("tweet deleted " + str(t))
                return


#return timezone aware time stamp
def getAwareTime(tt):
    """
       Generates timezone aware timestamp from timezone unaware timestamp

       PARAMETERS
       ------------
       :param tt: datatime
           timezome unaware timestamp

       RETURNS
       ------------
       :return: datatime
           timezone aware timestamp
       """
    timezone = pytz.timezone("Europe/Amsterdam")
    return (timezone.localize(tt))

def getReplies(tweet_id):
    """
       Get replies that have been tweeted later than a specific tweet

       PARAMETERS
       ------------
       :param tweet_id: int
           tweet id of the specific tweet

       RETURNS
       ------------
       :return: list
           List contains twitter.status objects of all relevant tweets
       """
    replies = api.GetSearch(raw_query="q=to%3AThatOldMovieGu1&since_id="+str(tweet_id)+"&")
    reply_list = []
    for t in replies:
        if int(t._json["in_reply_to_status_id"]) == int(tweet_id):
            reply_list.append(t)

    return reply_list

def noReplies(movie_name):
    """
   Generates a reply containing the correct answer to close an unanswered tweet

   PARAMETERS
   ------------
   :param movie_name: str
       Movie quote

   RETURNS
   ------------
   :return: string
       Message that should be tweeted
   """

    answer = random.choice(["The quote was actually from a movie called ", "The movie in question was ", "The quote was from the movie ", ]) \
             + movie_name + \
             random.choice([". I'll try to make it easier next time", ". I guess it wan't as obvious as I thought"])
    return answer

def generateQuoteQuestion(quote):
    """
    Generates a question for a movie quote

    PARAMETERS
    ------------
    :param quote: str
        Movie quote

    RETURNS
    ------------
    :return: string
        Message that should be tweeted
    """
    Quote_of_the_Day = random.choice(["Hey there movie fans, can any of you guys figure out where this quote comes from? ",
                                      "I have this quote stuck in my head, can someone help me? ", "Can you guess where this quote came from? ",
                                      "Can someone help me find out where this quote is from? "]) + "Quote: " + "\""+ str(quote) +"\" "
    return Quote_of_the_Day

def answerGenerator(correctAnswer, user, checkAnswer):
    """
    Generates reply to user depending on the correctness of his answer

    PARAMETERS
    ------------
    :param correctAnswer: str
        name of the correct movie

           user: str
        screen_name of the user who replied

           checkAnswer: int
        integer representing the correctness of the answer

    RETURNS
    ------------
    :return: string
        Message that should be tweeted
    """
    answer = "43"

    if checkAnswer == 1:
        answer = random.choice(["BINGO! ", "It was indeed, " + correctAnswer + ". "]) + \
                                random.choice(["Congratulations @" + str(user),
                                               "Cheers to @" + str(user),
                                               "Thank you @" + str(user)]) \
                                + random.choice([", you are indeed correct. ", ", for solving the quote. ", " "]) + random.choice(["Come back tomorrow for another quote.", "It's nice to know that people are still watching this movie.","For a second there I thought no one would get it."])

    # If the user is 70% correct
    if checkAnswer == 2:
        answer = random.choice(["You're right, but ", "Getting warmer.... "]) \
                 + random.choice(
            ["you need to be more accurate kid. ", "specify! ", "full title please. ", "you need to be more specific. "]) \
                 + random.choice(
            ["Just want to make sure you get it right", "I think I know where you're going but I need to make sure",
             "Which one?"])


    # If the user found a similar quote on a different movie
    if checkAnswer == 3 or checkAnswer==4:
        answer = random.choice([random.choice(
            ["Close but no cigar my friend. ", "That is not where the quote came from but its close.",
             "Not really, but I understand the confusion"]),
                                random.choice(["They have something similar, ", "I think they have a similar quote, ",
                                               "That movie have similar quotes, ", "Some words do match, "]) \
                                + random.choice(
                                    ["but I don't think this movie was it. ", "but not exactly what I was going for. "])]) \
                 + random.choice(["Don't give up!", "It's not that hard.", "At least that's one movie off the list",
                                  " ", " You can do this, I believe in you kid", " Keep calm and try again"])



    # If the user answer incorrectly
    if checkAnswer == 0:
        answer = random.choice(['This was not what I had in mind, ', 'Not exactly bucko,', 'Nice try kiddo, ']) \
                 + random.choice(["you are welcome to try again.", "just think over it for a minute.",
                                  "don’t over think it just try again.", "nice try though."]) \
                 + random.choice([" Don't give up!", " It's not that hard.", " At least that's one movie off the list",
                                  " ", " you can do this, I believe in you kid", " keep calm and try again"])

    return answer

def hint(movie_names):
    """
    Generates sentence containing the hint

    PARAMETERS
    ------------
    :param movie_names: str
        Three answer options

    RETURNS
    ------------
    :return: string
        Message that should be tweeted
    """
    hint = random.choice(["Just to make it easier, heres a hint. The movie is either:",
                         "These are several movies where the quote may have come from",
                         "I've narrowed the movie list down to just these three:",
                         "The quotes are most likely from one of these movies",
                         "To make it easier for you guys, here the three most likely movies the quote came from"]) + "\n" + str(movie_names)
    return hint


"""
Run the main program 
"""
twitterBot()