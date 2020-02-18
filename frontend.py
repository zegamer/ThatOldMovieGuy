import twitter
import json
from TwitterSearch import *

api = twitter.Api(consumer_key='77fIyHnx653Nnx0W4Iz4XRua9',
                  consumer_secret='rG0FQNYliP2jlab2Nf0VYm83a3iC0UUFmyOetHd8aaD4nSa4aE',
                  access_token_key='1227546694969167873-6Feip4gF0vg0DJxN38yLWCrPIVNYVt',
                  access_token_secret='rOozbozQIqpy5JonuSrlkxq7d4NXSeIjhUCjtotVgZeHJ')

def twitterBot():

    # Api Keys added
    # tweeting
    tweet_id = 1229730717636136961
    replies = getReplies(1229730717636136961)
    for t in replies:
        print (t._json["user"]["screen_name"])
    print (replies)

def getReplies(tweet_id):
    replies = api.GetSearch(raw_query="q=to%3AThatOldMovieGu1&since_id="+str(tweet_id))
    reply_list = []
    for t in replies:
        if t._json["in_reply_to_status_id"] ==tweet_id:
            reply_list.append(t)

    return reply_list


twitterBot()