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
posting_frequency = 120 #makes post every $posting_frequency$ seconds
last_tweet_time = datetime.now() - timedelta(seconds=posting_frequency+100)

tweet_lifetime = 100  # closes tweet if its older than $posting_frequency$ seconds

reply_frequency = 70 #checks for replies every $posting_frequency$ seconds
last_reply_check_time =datetime.now() - timedelta(seconds=reply_frequency+100)

#Tweet history
# contains: tweet status message, quote info, tweet status (0 unanswered, 1 hint has been given), last time we checked for replies
previous_tweet_list = []

def twitterBot():
    global last_tweet_time,last_reply_check_time, posting_frequency, reply_frequency, previous_tweet_list, tweet_lifetime

    while True:
        # Checks if it is time to tweet a new tweet

        if (datetime.now()-last_tweet_time)>timedelta(seconds=posting_frequency):
            #respond to previous tweets
            open_tweets = db.get_open_tweets()
            if len(open_tweets)!=0:
                for i in open_tweets:
                    print(i)
                    # open_tweet_time = datetime.strptime(open_tweets[i]["time_posted"], '%Y-%m-%d %H:%M:%S')
                    print (open_tweets[i]["time_posted"])
                    open_tweet_time = datetime.fromisoformat(open_tweets[i]["time_posted"])
                    # print (open_tweet_time)
                    # print (open_tweets[i]["time_posted"])
                    if (open_tweet_time<getAwareTime(datetime.now()-timedelta(seconds=tweet_lifetime))):
                        quote_data = db.get_quote_data_from_tweet(i)
                        movie = quote_data['Movie']
                        body = noReplies(movie)
                        print (body)
                        result = api.PostUpdate(body, in_reply_to_status_id=i)
                        db.change_tweet_open_status(i)
                        print ("Ŗemoved tweet")

            # print (type (ot))
            # for t in ot:
            #     print (ot[t])
            #     print (type(t))
            # if len(previous_tweet_list)!=0:
            #     for t in previous_tweet_list:
            #         tweet_time_str = t[0]._json["created_at"]
            #         tweet_time = datetime.strptime(tweet_time_str, '%a %b %d %H:%M:%S %z %Y')
            #         if (tweet_time<getAwareTime(datetime.now()-timedelta(seconds = tweet_lifetime))):
            #             body = "I looked through my bookshelf and found the movie :) It was from " + str(t[1][1])
            #             result = api.PostUpdate(body, in_reply_to_status_id=t[0]._json["id"])
            #             previous_tweet_list.remove(t)
            #     #Here goes through the previous tweets list and gives answers to all outstanding quotes
            #     print ("give answers to previous tweets")

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

        #Check for replies

        #Possible improvement - currently calls get replies for each tweet . Call it only once and filter out responses to each specific tweet afterwards.
        #
        if (datetime.now() - last_reply_check_time) > timedelta(seconds=reply_frequency):
            print("check for replies")
            #filler message
            # previous_tweet_list.append ([api.GetStatus(1230969409587556352),"hello",0,getAwareTime(datetime.now())])
            open_tweets = db.get_open_tweets()
            if len(open_tweets) != 0:
                for t in open_tweets:
                    replies = getReplies(t)
                    print (t)
                    print (replies)
                    for r in replies:
                        tweet_time_str = r._json["created_at"]
                        tweet_time = datetime.strptime(tweet_time_str, '%a %b %d %H:%M:%S %z %Y')
                        if (open_tweets[t]["last_modified"]<tweet_time):
                            #add check if tweet is young enough
                            # status = api.PostUpdate("@"+ str(r._json["user"]["screen_name"]) +random.choice([" Hello! You're the best!", " BANG!", " Sun"]), in_reply_to_status_id=r._json["id"])
                            quote_data = db.get_quote_data_from_tweet(t)
                            movie = quote_data['Movie']

                            print (str(r._json["text"]).replace("@ThatOldMovieGu1 ","").strip())

                            answer = answerGenerator(movie, r._json["user"]["screen_name"], backend.answer_checker(t, str(r._json["text"]).replace("@ThatOldMovieGu1 ","").strip()))
                            status = api.PostUpdate("@" + str(r._json["user"]["screen_name"]) + " " + str(answer), in_reply_to_status_id=r._json["id"])
                            print (status)
                            print(r._json["id"])
                            print("Sent a reply!")
                    db.change_tweet_last_updated(i,str(getAwareTime(datetime.now())))

            last_reply_check_time = datetime.now()

#return timezone aware time stamp
def getAwareTime(tt):
    timezone = pytz.timezone("Europe/Amsterdam")
    return (timezone.localize(tt))

def getReplies(tweet_id):
    replies = api.GetSearch(raw_query="q=to%3AThatOldMovieGu1&since_id="+str(tweet_id)+"&")
    reply_list = []
    for t in replies:
        if t._json["in_reply_to_status_id"] == tweet_id:
            reply_list.append(t)

    return reply_list

def noReplies(movie_name):
    answer = random.choice(["The quote was actually from a movie called ", "The movie in question was ", "The quote was from the movie ", ]) \
             + movie_name + \
             random.choice([". I'll try to make it easier next time", ". I guess it wan't as obvious as I thought"])
    return answer

def makeReplies(tweet_id, checkAnswer):
    replies = getReplies(tweet_id)
    user = ""
    for t in replies:
        user = t._json["user"]["screen_name"]

    # If the user answer correctly
    if checkAnswer == 1:
        answer = random.choice(
            ["It was indeed, " + "<movie name>", "Congratulations @" + str(user) + ", you are indeed correct", "BINGO!",
             "Cheers to @" + str(user) + ", for solving the quote."])

    # If the user answer incorrectly
    if checkAnswer == 0:
        answer = random.choice(
            ['This was not what I had in mind, ', 'Not exactly bucko,', 'Nice try kiddo, ']) + random.choice(["you are welcome to try again.",
            "don't give up! It's not that hard.", "just think over it for a minute.", "don’t overthink it just try again."])

    # If the user replies a nonexistent movie or replies in gibberish
    if checkAnswer == 2:
        answer = random.choice(
            ["Sorry but I don't know this movie", "Is this an actual movie?", "That doesnt sound familiar", "I think you've made a typo"])

    return answer

def generateQuoteQuestion(quote):
    Quote_of_the_Day = random.choice(["Hey there movie fans, can any of you guys figure out where this quote comes from? ",
                                      "I have this quote stuck in my head, can someone help me? ", "Can you guess where this quote came from? ",
                                      "Can someone help me find out where this quote is from? "]) + "Quote: " + "\""+ str(quote) +"\" "
    return Quote_of_the_Day

def quoteGenerator ():
    quote = "It's 9 o'clock on a Saturday"
    movie = "Inside Man"
    year = "2006"

    return [quote, movie, year]

def answerGenerator(correctAnswer, user, checkAnswer):
    if checkAnswer == 1:
        answer = random.choice(
            ["It was indeed, " + correctAnswer, "Congratulations @" + str(user) + ", you are indeed correct", "BINGO!",
             "Cheers to @" + str(user) + ", for solving the quote."])

    if checkAnswer == 2:
        answer = random.choice(
            ["Close but no cigar my friend", "I think they have a similar quote, but I don't think this movie was it",
             "Nope! but it was close", "Some words do match but that's not exactly right"])


    # If the user answer incorrectly
    if checkAnswer == 3:
        answer = random.choice(
            ['This was not what I had in mind, ', 'Not exactly bucko,', 'Nice try kiddo, ']) + random.choice(["you are welcome to try again.",
            "don't give up! It's not that hard.", "just think over it for a minute.", "don’t overthink it just try again."])

    # If the user replies a nonexistent movie or replies in gibberish
    if checkAnswer == 0:
        answer = random.choice(
            ["Sorry but I don't know this movie", "Is this an actual movie?", "That doesnt sound familiar", "I think you've made a typo"])

    return answer

twitterBot()
# t = api.GetStatus(1230950865370066945)
# r = api.GetStatus(1230961588099801089)
# print (backend.answer_checker(t._json["id"],r._json["text"]))
# quote_data = db.get_quote_data_from_tweet(t._json["id"])
# quote = quote_data['Quote']
#
# print(answerGenerator(quote,r._json["user"]["screen_name"],backend.answer_checker(t._json["id"],r._json["text"])))


# print (answerGenerator("Hello",r._json["user"]["screen_name"],0))
# print (db.push_tweet_in_db(128958938,0,str(datetime.now()),0,str(datetime.now())))
# replies = getReplies(1229794858082148352)
# for r in replies:
#     print (r._json["user"]["screen_name"])

# status = api.PostUpdate("@Joe52806384 BANG!", in_reply_to_status_id=1229796954768584705)
# status = api.GetStatus(1229799878068490242)
# print (status)
# tweet_time_str = status._json["created_at"]
# print (tweet_time_str)
# tweet_time = datetime.strptime(tweet_time_str, '%a %b %d %H:%M:%S %z %Y')
# print (tweet_time)

# print (random.choice([" Hello! You're the best!","BANG!", " Sun"]))

# new_quote, quote_id = db.get_random_quote_data()
# print (new_quote["Quote"])

# ot = db.get_open_tweets()
# print (type (ot))
# for t in ot:
#     print (ot[t])
#     print (type(t))