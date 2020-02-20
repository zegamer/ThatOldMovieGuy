from requests import get
from urllib.parse import quote_plus
import json
from string import punctuation
from random import shuffle
from difflib import SequenceMatcher
import database as db


# Function gets all the movies in which the given quote exists
#
# ARGUMENTS
# search_term : the quote for which related movies are to be searched
#
# OUTPUT
# Returns a list with all the movies in which the quote exists
# If there is no similar movie then it returns the string "None"
def get_all_movies_from_quote(search_term):
    parsed_term = quote_plus(search_term)
    url = "http://api.quodb.com/search/" + parsed_term + "?titles_per_page=100&phrases_per_title=1000&page=1"
    movie_list = []
    http_output = get(url)
    try:
        json_data = json.loads(json.dumps(http_output.json()))
        search_term = search_term.translate(str.maketrans('', '', punctuation))
        iterations = len(json_data["docs"])
        for i in range(iterations):
            title = json_data["docs"][i]["title"]
            phrase = json_data["docs"][i]["phrase"].translate(str.maketrans('', '', punctuation))
            if phrase.find(search_term) != -1:
                movie_list.append(title)
        return movie_list
    except:
        return "None"


# Function iterates through the all the movies that have the given quote
# and finds out if user entered any movie similar to those in the list
#
# ARGUMENTS
# movie_list : list of all movies that have the given quote
# movie_name : User entered movie
#
# OUTPUT
# Return True if movie in list otherwise False
def movie_matcher(movie_list, movie_name):
    try:
        for i in movie_list:
            if SequenceMatcher(None, i.lower(), movie_name.lower()).ratio() > 0.7:
                return True
    except:
        return False


# Function generates list of 2 movie names and the correct one
#
# ARGUMENTS
# quote_id : The quote_id that was used in the tweet
#
# OUTPUT
# Returns a string with 3 movies in an ordered (1,2,3) list
def movie_hint(quote_id):
    quote_data = db.get_quote_data_from_id(quote_id)
    correct_movie = quote_data['Movie']
    hint_list = [correct_movie]
    while len(hint_list) <= 2:
        movie = db.get_random_movie()
        if movie not in hint_list:
            hint_list.append(movie)
    shuffle(hint_list)
    hint = "1. {}\n2. {}\n3. {}".format(hint_list[0], hint_list[1], hint_list[2])
    return hint


# Function check answers and identifies if the movie is the correct one, in the list, or is incorrect
#
# ARGUMENTS
# tweet_id : the tweet_id in which the quote was used
# movie_name : user entered movie name
#
# OUTPUT
# Returns (1) if user enters exact movie name
# Returns (2, correct movie name) if movie name is 50% true
# Returns (3) if quote exists in another movie
# Returns (4) if some words match but isn't correct
# Returns (0) if it is entirely wrong
def answer_checker(tweet_id, movie_name):
    quote_data = db.get_quote_data_from_tweet(tweet_id)
    quote = quote_data['Quote']
    correct_movie = quote_data['Movie']
    movie_list = get_all_movies_from_quote(quote)
    correctness = SequenceMatcher(None, correct_movie.lower(), movie_name.lower()).ratio()
    if correct_movie == movie_name:
        # For 100% accurate answer
        return 1
    elif correctness > 0.5:
        # Gets 50% right
        return 2, correct_movie
    elif movie_matcher(movie_list, movie_name):
        # Quote exists in another movie
        return 3
    elif 0.3 < correctness < 0.5:
        # Some words match but not exactly right
        return 4
    else:
        # Plain ol' wrong
        return 0


# (IGNORE) Previous edits
# def answer_checker(quote, movie_name, correct_movie):
#     # All the print statements will be replaced by replies directly in Twitter
#     movie_list = get_all_movies_from_quote(quote)
#     correctness = SequenceMatcher(None, correct_movie.lower(), movie_name.lower()).ratio()
#     if correct_movie == movie_name:
#         print("Bingo! You got it!")
#         return 1
#     elif correctness > 0.5:
#         print("Bingo! It is \"" + correct_movie + "\"")
#         return 1
#     elif movie_matcher(movie_list, movie_name):
#         print("You're not wrong but that's not the movie I had in mind.")
#         print(movie_hint(correct_movie, movie_list))
#         return 2
#     elif 0.3 < correctness < 0.5:
#         print("Some words do match but that's not exactly right")
#         print(movie_hint(correct_movie, movie_list))
#         return 3
#     else:
#         print("Ehh! No.")
#         return 0

