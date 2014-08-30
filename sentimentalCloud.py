#!/usr/bin/env python

'''
word cloud for indico sentiment analysis
'''

import argparse as ap
from pytagcloud import create_tag_image, make_tags, LAYOUTS
from pytagcloud.lang.counter import get_tag_counts
from requests_oauthlib import OAuth1
import requests
import operator
from collections import Counter
import urllib

limit = 200
background_color = (0, 0, 0)
max_word_size = 80
width = 1280
height =800

def twitter(query):
    f = open('stopwords.txt', 'rb')
    stop_words = [line.strip() for line in f]  # loading common English stopwords from file
    tweets_words = [query, 'http', 'amp']  # common words in tweets
    if(query.startswith('#')):
            tweets_words.append(query[1:])
    else:
            tweets_words.append('#'+query)
    stop_words += tweets_words  # add common words in tweets to stopwords

    f = open('keys.txt', 'rb')
    my_secrets = [line.strip() for line in f]

    my_oauth = OAuth1(my_secrets[0],
                      client_secret=my_secrets[1],
                      resource_owner_key=my_secrets[2],
                      resource_owner_secret=my_secrets[3])

    complete_url = 'https://api.twitter.com/1.1/search/tweets.json?q=' + urllib.quote(query) + '&count=' + str(limit)
    return my_oauth, complete_url, stop_words

def wordcloud(query, layout, font, max_words, verbosity=False):
    my_oauth, complete_url, stop_words = twitter(query)
    punctuation = "#@!\"$%&'()*+,-./:;<=>?[\]^_`{|}~\'"  # characters exluded from tweets
    my_text = ''
    r = requests.get(complete_url, auth=my_oauth)
    tweets = r.json()
    if verbosity == True:
        print tweets
    for tweet in tweets['statuses']:
        text = tweet['text'].lower()
        text = ''.join(ch for ch in text if ch not in punctuation)  # exclude punctuation from tweets
        my_text += text

    words = my_text.split()
    counts = Counter(words)
    for word in stop_words:
        del counts[word]

    for key in counts.keys():
        if len(key) < 3 or key.startswith('http'):
            del counts[key]

    final = counts.most_common(max_words)
    max_count = max(final, key=operator.itemgetter(1))[1]
    final = [(name, count / float(max_count))for name, count in final]
    tags = make_tags(final, maxsize=max_word_size)
    create_tag_image(tags, query + '.png', size=(width, height), layout=layout, fontname=font, background=background_color)
    print "new png created"

if __name__=="__main__":
    parser = ap.ArgumentParser(
            description = "create wordcloud"
            )
    parser.add_argument("searchword",
            type = str,
            help = "word to query twitter"
            )
    parser.add_argument("layout",
            type = int,
            help = "layout style. look up pytagcloud.create_tag_image layouts. I recommend 3 or 4"
            )
    parser.add_argument("fontname",
            type = str,
            help = "font for png. Find fontnames in fonts.txt in this repo"
            )
    parser.add_argument("-m", "--max_words",
            action = "store",
            type = int,
            help = "set max number of words to use in wordcloud. else 150 is used.")
    parser.add_argument("-v", "--verbose",
            action = "store_true",
            help = "shows query output"
            )
    args = parser.parse_args()
    
    if args.max_words:
        max_words = args.max_words
    else: 
        max_words = 150 
    if args.verbose:
        wordcloud(args.searchword, args.layout, args.fontname, max_words, True)
    else:
        wordcloud(args.searchword, args.layout, args.fontname, max_words)
