# That Old Movie Guy


That Old Movie Guy is a twitterbot made by 4 students for a course at the University of Twente. This bot is a personification of an elderly movie fan who has a huge interest in movies and pop cultural references. The context was that the bot is a retired old man who has a knack for popular movie quotes and tries to keep himself active by asking it on twitter.

## Features
- Built entirely using python and firebase realtime database
- Checks all the movies where the quote has been used. 
- Uses an NLP library, [fuzzywuzzy] to match with varied replies of the user 

## Libraries
- [Pyrebase4] - Python interface for Firebase API
- [Fuzzywuzzy] - NLP library to check user replies
- [Python twitter] - Python interface for Twitter API
- [pytz] - Timezone calculations

### Installation

This twitterbot requires Python 3.7 [[Download]] to work.

#### Cloning repository
Either download from [here] or use the git shell 
> Terminal will prompt for your username and password
```sh
$ git clone https://github.com/zegamer/Fdt-ITech-Twitterbot.git
```

#### Installing libraries
```sh
$ cd Fdt-ITech-Twitterbot-master
$ pip install -r requirements.txt
```

#### Changing API keys and secrets
Open config.ini in a text editor.
Replace xxxxx with your API keys.
You can find instructions for [Twitter API]

#### Running the program



### Todos

 - Make answer checker more robust
 - Add more quotes
 - Add movie metadata to produce efficient hints


## License
----


The code is **open source** under MIT Licence.
Check licence file in the repository.

For further questions, you can reach at m.v.konda@student.utwente.nl

[frontend.py]: #
[Download]: <https://www.python.org/downloads/>
[pyrebase4]: <https://github.com/nhorvath/Pyrebase4>
[fuzzywuzzy]: <https://pypi.org/project/fuzzywuzzy/>
[pytz]: <https://pypi.org/project/pytz/>
[twitter dev]: <https://developer.twitter.com>
[QuoDB]: <http://www.quodb.com>
[Python twitter]: <https://python-twitter.readthedocs.io/en/latest/>
[here]: <https://github.com/zegamer/Fdt-ITech-Twitterbot.git>
[Twitter API]: <https://developer.twitter.com>
