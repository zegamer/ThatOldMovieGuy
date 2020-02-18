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

#for docs, see https://python-twitter.readthedocs.io/en/latest/twitter.html

#speech generator
import random

api = twitter.Api(consumer_key='77fIyHnx653Nnx0W4Iz4XRua9',
                      consumer_secret='rG0FQNYliP2jlab2Nf0VYm83a3iC0UUFmyOetHd8aaD4nSa4aE',
                      access_token_key='1227546694969167873-6Feip4gF0vg0DJxN38yLWCrPIVNYVt',
                      access_token_secret='rOozbozQIqpy5JonuSrlkxq7d4NXSeIjhUCjtotVgZeHJ')

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
    tweet_id = 1229754707775827968
    body = makeReplies(tweet_id)
    # Add backend answer checker here
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

twitter_demo()