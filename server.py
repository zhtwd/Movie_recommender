from flask import Flask
from flask import request
from flask import jsonify
from collections import defaultdict
import json
import random
import operator
import logging

app = Flask(__name__)


# set up logger
logger = logging.getLogger('reco_server')
logger.setLevel(logging.DEBUG)
hdlr = logging.FileHandler('logs/reco.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 


@app.before_first_request
def initialize():
    global follows, watch, watch_reversed, movies, movie_reversed, movie_rank
    follows = defaultdict(set)
    watch = defaultdict(lambda: defaultdict(int))
    watch_reversed = defaultdict(set)
    movies = {}
    movie_reversed = defaultdict(set)
    movie_rank = defaultdict(float)
    
    with open('movie.json') as movie_file:
        movies = json.load(movie_file)
    
    for movie in movies:
        genres = movies[movie]
        for genre in genres:
            movie_reversed[genre].add(movie)

    logger.info('loaded movie lib %s' % movies)
    logger.info('generated reversed index for movie lib %s' % movie_reversed)
 

@app.route('/')
def load_movie():
    return "recommendation server"


@app.route('/follow', methods=['POST'])
def add_follower():
    if not request.json or not 'from' in request.json \
            or not 'to' in request.json:
        logger.info('bad request %s' % request.json)
        return 'bad request\n'
    follower = request.json['from']
    followee = request.json['to']
    follows[follower].add(followee)
    logger.info('%s follows %s' % (follower, followee))
    return 'sucess\n'


@app.route('/watch', methods=['POST'])
def add_watch():
    if not request.json or not 'user' in request.json \
            or not 'movie' in request.json:
        logger.info('bad request %s' % request.json)
        return 'bad request\n'
    user = request.json['user']
    movie = request.json['movie']
    watch[user][movie] += 1
    watch_reversed[movie].add(user)
    logger.info('%s watched %s' % (user, movie))
    return 'sucess\n'


@app.route('/recommendations', methods=['GET'])
def recommend():
    if not request.args or not request.args['user']:
        logger.info('bad request %s' % request.args)
        return 'bad request\n'
    user = request.args['user']
    logger.info('getting recommendation for user %s' % user)
    res = get_rank(user)
    return jsonify({'list': res})


def get_rank(user):
    global movie_rank
    movie_rank = defaultdict(float)
    others_watched_history(user)
    followee_watched(user)
    movie_similarity(user)
    sorted_movie_rank = sorted(movie_rank.items(),
                               key=operator.itemgetter(1), reverse=True)
    reco = []
    if user in watch:
        liked_movies = sorted(watch[user].items(),
                              key=operator.itemgetter(1), reverse=True)
        reco.extend(zip(*liked_movies)[0][:2])
    logger.info('recommend using personal movie history: %s' % reco)
    
    reco.extend(zip(*sorted_movie_rank)[0][:5-len(reco)])
    logger.info('recommend using designed logic: %s' % reco)

    while len(reco) < 5:
        random_movie = random.choice(movies.keys())
        if random_movie not in reco:
            reco.append(random_movie)
    logger.info('final recommending list: %s' % reco)

    return reco


def cosine_similarity(a, b):
    return len(set(a).intersection(set(b))) / float(len(set(a)) * len(set(b)))


def others_watched_history(user):
    if user not in watch:
        return
    for movie in set(watch[user].keys()):
        for other_user in watch_reversed[movie].difference(user):
            similarity = 0.1
            try:
                similarity = max(similarity, cosine_similarity(
                    watch[user], watch[other_user]))
            except:
                pass
            for other_movie in set(watch[other_user].keys()):
                if other_movie == movie:
                    continue
                movie_rank[other_movie] += similarity
    logger.info(('movie ranking after using movie history'
                 ' of other users: %s') % movie_rank)


def followee_watched(user):
    if user not in follows:
        return
    followees = follows[user]    
    for followee in followees:
        similarity = 0.5
        try:
            similarity += cosine_similarity(watch[user], watch[followee])
        except:
            pass
        for movie in watch[followee]:
            movie_rank[movie] += similarity
    logger.info(('movie ranking after using movie history'
                 ' based on followed people: %s') % movie_rank)


def movie_similarity(user):
    if user not in watch:
        return
    for movie in set(watch[user].keys()):
        for genre in movies[movie]:
            for other_movie in movie_reversed[genre].difference(movie):
                if other_movie == movie:
                    continue
                similarity = 0.1
                try:
                    similarity = max(similarity, 
                            cosine_similarity(movies[movie], movies[other_movie]))
                except:
                    pass
                movie_rank[other_movie] += similarity
    logger.info('movie ranking after using movie genres: %s'
                % movie_rank)


if __name__ == "__main__":
   
    app.run(host='0.0.0.0', debug=True)
