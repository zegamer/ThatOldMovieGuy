#!/usr/bin/python

'''
USE AT YOUR OWN PERIL <3
fill in your API keys before running the script
written in Python3 by Judith van Stegeren, @jd7h
'''

'''
before running the script, do this:
1. create a virtual environment
$ python -m venv venv 
$ source venv/bin/activate
2. install the dependencies
$ pip install python-twitter
3. obtain API keys from twitter
4. fill them in in the script below
'''

import time
import twitter
import backend2

#for docs, see https://python-twitter.readthedocs.io/en/latest/twitter.html

#speech generator
import random

api = twitter.Api(consumer_key='77fIyHnx653Nnx0W4Iz4XRua9',
                      consumer_secret='rG0FQNYliP2jlab2Nf0VYm83a3iC0UUFmyOetHd8aaD4nSa4aE',
                      access_token_key='1227546694969167873-6Feip4gF0vg0DJxN38yLWCrPIVNYVt',
                      access_token_secret='rOozbozQIqpy5JonuSrlkxq7d4NXSeIjhUCjtotVgZeHJ')

movieName = "The Shining"
quote = "\"Here's Johnny\""

correctAnswer = "The Shining"


def twitter_demo():

    # Api Keys added
    # api = twitter.Api(consumer_key='OSv3zbkEOMs89vWOG8WU1sulQ',
    #                   consumer_secret='NRZW1VDlz8ug0lovKWwKWDTgcdYbm1Krb2hz7KxnuboHxuTZuY',
    #                   access_token_key='972389995083317248-W71G8021PU4IEsIYKbak7dznEhbLx8w',
    #                   access_token_secret='rMcuzSrplE1B9O0jCw9vwVAJz50xzMAA6bOAU3QEOTvXn')
    #

    # get followers
    print("Getting a list of accounts I follow on Twitter...")
    friends = api.GetFriends()
    friend_ids = [friend.id for friend in friends]
    for friend in friends:
        print("Friend: ", friend.name, friend.screen_name, friend.id)

    # get a list of accounts that are following me
    print("Getting a list of followers from Twitter...")
    followers = api.GetFollowers()
    followers_ids = [user.id for user in followers]
    for follower in followers:
        print("Follower: ", follower.name, follower.screen_name, follower.id)

    # look up the user_id of a single user
    print("Looking up the details of screenname @jd7h...")
    print(api.UsersLookup(screen_name=["jd7h"]))

    print("Looking up the details of screenname @jd7h...")
    print(api.UsersLookup(screen_name=["jd7h"]))
    # this should output: [User(ID=222060384, ScreenName=jd7h)]

    #tweeting
    body = generateQuoteQuestion()
    print("Posting tweet...")
    result = api.PostUpdate(body)

    # mentions:
    # body = "mnvljarg!"
    print("Posting tweet with mention...")
    # result = api.PostUpdate(body) # including the screenname (prepended by a '@') in the tweet-body is enough to create a mention.

    # THIS PART DOESNT WORK
    # replying to a tweet:
    tweet_id = 1230502741002375170

    # Add backend answer checker here
    # body = makeReply(tweet_id, getReplies(tweet_id))
    body = answerChecker(tweet_id, backend2.answer_checker(tweet_id, correctAnswer))
    print("Posting reply...")
    result = api.PostUpdate(body, in_reply_to_status_id=tweet_id)

    # other useful stuff:
    # creating a private list
    print("Creating a private list...")
    # mylist = api.CreateList(name="My beautiful list",mode="private",description=("A secret list I created on " + time.strftime("%Y-%m-%d")))

    # Add all users from 'Following' to the new list
    print("Adding friends to the newly created list...")
    # for friend_id in friend_ids:
    #   print("Adding ", friend_id)
    #   result = api.CreateListsMember(list_id=mylist.id,user_id=friend_id)




def getReplies(tweet_id):
    replies = api.GetSearch(raw_query="q=to%3AThatOldMovieGu1&since_id="+str(tweet_id))
    reply_list = []
    for t in replies:
        if t._json["in_reply_to_status_id"] == tweet_id:
            reply_list.append(t)

    return reply_list


def answerChecker(tweet_id, checkAnswer):
    replies = getReplies(tweet_id)
    user = ""
    for t in replies:
        user = t._json["user"]["screen_name"]

    # if no one answered
    if user == "":
        answer = noReplies(correctAnswer)

    else:
        # If the user answer correctly
        if checkAnswer == 1:
            answer = random.choice(
                ["It was indeed, " + correctAnswer + ".", "Congratulations @" + str(user) + ", you are indeed correct.", "BINGO!",
                 "Cheers to @" + str(user) + ", for solving the quote.", "Thank you @" + str(user) + ", for solving the quote."]) \
                     + random.choice(["Come back tomorrow for another quote.", "It's nice to know that people are still watching this movie.",
                                      "For a second there I thought no one would get it."])

        if checkAnswer == 2:
            answer = random.choice([random.choice(["Close but no cigar my friend.", " You are getting warmer", "That is not where the quote came from but its close"]),
                                    random.choice(["They have something similar, ", "I think they have a similar quote, ", "That movie have similar quotes, ", "Some words do match, "]) \
                                    + random.choice([" but I don't think this movie was it.", " but not exactly what I was going for."]) \
                                    + random.choice(["Don't give up!", "It's not that hard.", "At least that's one movie off the list",
                                                    " ", " you can do this, I believe in you kid", " keep calm and try again"])
                                    ])


        # If the user answer incorrectly
        if checkAnswer == 3:
            answer = random.choice(['This was not what I had in mind, ', 'Not exactly bucko,', 'Nice try kiddo, ']) \
                     + random.choice(["you are welcome to try again.", "just think over it for a minute.",
                                      "don’t over think it just try again.", "nice try though."]) \
                     + random.choice([" Don't give up!", " It's not that hard.", " At least that's one movie off the list",
                                      " ", " you can do this, I believe in you kid", " keep calm and try again"])

        # If the user replies a nonexistent movie or replies in gibberish
        if checkAnswer == 0:
            answer = random.choice(["Sorry but I don't know this movie", "Is this an actual movie?",
                                     "Is this a cult classic?", "Is this a new movie?"]) \
                     + random.choice(["because I've never heard of it before.", "that doesnt sound familiar.",
                                      "I don't think I'm familiar with this movie."]) \
                     + random.choice(["Nice try though.", "I'll put in the list.", "Don't give up just yet though"])
    return answer

# def makeReply (tweet_id, user_answer):



def generateQuoteQuestion():
    Quote_of_the_Day = random.choice(["Hey there movie fans,", " Hey guys,",
                                      "I have this quote stuck in my head,",
                                      "Quote time," "Here's a question for you all,"]) \
                       + random.choice([" can any of you guys figure out where this quote comes from? ",
                                        " can you guess where this quote came from? ",
                                        " can someone please help me find out where this quote is from? "
                                        " where did this quote come from? "]) \
                       + random.choice(["Quote: ", "Line: ", " "]) + quote
    return Quote_of_the_Day

def noReplies(movie_name):
    answer = random.choice(["The quote was actually from a movie called ", "The movie in question was ", "The quote was from the movie ", "Its from "]) \
             + movie_name + \
             random.choice([". Ill try to make it easier next time", ". I guess it wan't as obvious as I thought", ". I guess this line is not as famous as I thought"])
    return answer

def hint():
    # get list form backend
    randomMovie1 = random["Cars", "Lord of the Rings", "The room", "Pacific Rim", "One of the Spiderman Movies", "Avengers", "SinCity", "Pulp fiction"]
    randomMovie2 = random["Cars", "Lord of the Rings", "The room", "Pacific Rim", "One of the Spiderman Movies", "Avengers", "SinCity", "Pulp fiction"]
    possibleAnswers = movieName + randomMovie1 + randomMovie2
    hint = random.choice("Just to make it easier, heres a hint. The movie is either:",
                         "These are several movies where the quote may have come from",
                         "I've narrowed the movie list down to just this three:",
                         "The quotes are most likely from one of these movies",
                         "To make it easier for you guys, here the three most likely movies the quote came from") + possibleAnswers
    return hint

twitter_demo()
