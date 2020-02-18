from requests import get
from urllib.parse import quote_plus
import json
from string import punctuation
from random import randrange, shuffle
from difflib import SequenceMatcher
import pdb


# Function gets all the movies in which the given quote exists
def get_all_movies_from_quote(search_term):
    parsed_term = quote_plus(search_term)
    url = "http://api.quodb.com/search/" + parsed_term + "?titles_per_page=100&phrases_per_title=1000&page=1"
    print(url)
    movie_list = []
    http_output = get(url)
    json_data = json.loads(json.dumps(http_output.json()))
    search_term = search_term.translate(str.maketrans('', '', punctuation))
    iterations = len(json_data["docs"])
    for i in range(iterations):
        title = json_data["docs"][i]["title"]
        phrase = json_data["docs"][i]["phrase"].translate(str.maketrans('', '', punctuation))
        if phrase.find(search_term) != -1:
            movie_list.append(title)
    return movie_list


# Function is fired if user gets a movie name on the list but isn't the intended one
# OR
# if users are unable to guess after 2-3 tries
# It randomizes 3 movies one of which is the correct one
def movie_hint(correct_movie, movie_list):
    # pdb.set_trace()
    hint_list = [correct_movie]
    random_num = randrange(len(movie_list))
    while len(hint_list) <= 2:
        if movie_list[random_num] not in hint_list:
            hint_list.append(movie_list[random_num])
        random_num = randrange(len(movie_list))
    shuffle(hint_list)
    hint = "I'll give you a hint though:\n1. {}\n2. {}\n3. {}".format(hint_list[0], hint_list[1], hint_list[2])
    return hint


# Function check answers and identifies if the movie is the correct one, in the list, or is incorrect
def answer_checker(quote, movie_name, correct_movie):
    # All the print statements will be replaced by replies directly in Twitter
    movie_list = get_all_movies_from_quote(quote)
    if correct_movie == movie_name:
        print("Bingo!")
        return 1
    elif SequenceMatcher(None, correct_movie.lower(), movie_name.lower()).ratio() > 0.5:
        print("Bingo! It is " + correct_movie)
        return 1
    elif SequenceMatcher(None, correct_movie.lower(), movie_name.lower()).ratio() < 0.5:
        print("Some words do match but that's not exactly right")
        print(movie_hint(correct_movie, movie_list))
        return 2
    elif movie_name in movie_list:
        print("You're not wrong but that's not the movie I had in mind.")
        print(movie_hint(correct_movie, movie_list))
        return 3
    else:
        print("Ehh! No.")
        return 0

if __name__ == '__main__':
    given_quote = "I'll be back"
    print(given_quote)
    correct_answer = "Terminator 2: Judgement Day"
    answer = input("Which movie is this quote from? : ")
    while answer_checker(given_quote, answer, correct_answer) != 1:
        answer = input("Which movie is this quote from? : ")