import twitter
import json
from datetime import datetime, timedelta
import random
import backend

#Global variables

#Api Keys added
api = twitter.Api(consumer_key='77fIyHnx653Nnx0W4Iz4XRua9',
                  consumer_secret='rG0FQNYliP2jlab2Nf0VYm83a3iC0UUFmyOetHd8aaD4nSa4aE',
                  access_token_key='1227546694969167873-6Feip4gF0vg0DJxN38yLWCrPIVNYVt',
                  access_token_secret='rOozbozQIqpy5JonuSrlkxq7d4NXSeIjhUCjtotVgZeHJ')

posting_frequency = 900 #makes post every $posting_frequency$ seconds
last_tweet_time = datetime.now() - timedelta(seconds=posting_frequency+100)
previous_tweet_list = []

reply_frequency = 60
last_reply_check_time =datetime.now() - timedelta(seconds=reply_frequency+100)


def twitterBot():
    global last_tweet_time,last_reply_check_time, posting_frequency, reply_frequency, previous_tweet_list

    while True:
        #Checks if it is time to tweet a new tweet
        if (datetime.now()-last_tweet_time)>timedelta(seconds=posting_frequency):
            if len(previous_tweet_list)!=0:

                #Here goes through the previous tweets list and gives answers to all outstanding quotes
                print ("give answers to previous tweets")

            #Here calls funtion to get new quote
            status = api.PostUpdate(str(generateQuoteQuestion()))
            previous_tweet_list.append(status)
            print (previous_tweet_list)
            print ("Tweeted")

            last_tweet_time = datetime.now()

        #Check for replies
        if (datetime.now() - last_reply_check_time) > timedelta(seconds=reply_frequency):
            for t in previous_tweet_list:
                #here checks for replies and answers if necessary
                print ("check for replies")

            last_reply_check_time = datetime.now()


def getReplies(tweet_id):
    replies = api.GetSearch(raw_query="q=to%3AThatOldMovieGu1&since_id="+str(tweet_id))
    reply_list = []
    for t in replies:
        if t._json["in_reply_to_status_id"] ==tweet_id:
            reply_list.append(t)

    return reply_list

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
        answer = "Sorry but I don't know this movie", "Is this an actual movie?", "That doesnt sound familiar", "I think you've made a typo"

    return answer

def generateQuoteQuestion():
    Quote_of_the_Day = random.choice(["Hey there movie fans, can any of you guys figure out where this quote comes from? ",
                                      "I have this quote stuck in my head, can someone help me? ", "Can you guess where this quote came from? ",
                                      "Can someone help me find out where this quote is from? "]) + "Quote: " + "\"What, a swallow carrying a coconut?\" "
    return Quote_of_the_Day


twitterBot()