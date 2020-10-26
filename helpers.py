from datetime import datetime
from statistics import mean

from pymongo import MongoClient
from fuzzywuzzy import fuzz

STORAGE = 'database'

mongo_uri = "mongodb://localhost:27017/"
mongo_conn = MongoClient(mongo_uri)
db = mongo_conn['reviewer']
reviews_table = db['reviews']

reviews_list = []


def get_reviews(search_terms=None,
                order_field='date'):
    
    if STORAGE == 'database':
        if search_terms:
            query = {'title': {'$regex': search_terms, '$options': 'i'}}
        else:
            query = {}
        
        sort_by = [(order_field, -1)]
        reviews = reviews_table.find(query, {'_id': 0}).sort(sort_by)
    else:
        if search_terms:
            reviews = [review for review in reviews_list
                       if is_fuzzy_match(search_terms, review['title'])]
        else:
            reviews = reviews_list
        
        reviews = sorted(reviews, key=lambda x: x[order_field], reverse=True)

    return render_reviews(reviews)


def get_average_rating(search_terms=None):
    if STORAGE == 'database':
        if search_terms:
            query = {'title': {'$regex': search_terms, '$options': 'i'}}
        else:
            query = {}
        
        group = {'_id': None, 'avg': {'$avg': '$rating'}}

        pipeline = [{'$match': query},
                    {'$group': group}]
        
        rating = reviews_table.aggregate(pipeline).next()['avg']
    else:
        if search_terms:
            reviews = [review for review in reviews_list
                       if is_fuzzy_match(search_terms, review['title'])]
            
        else:
            reviews = reviews_list
        
        rating = mean([review['rating'] for review in reviews])

    return rating


def save_review(author,
                title,
                genre,
                rating,
                review):
    record = {'title': title,
              'genre': genre,
              'rating': float(rating),
              'review': review,
              'author': author,
              'date': todays_date(),
              }
    
    if STORAGE == 'database':
        reviews_table.insert_one(record)
    
    else:
        reviews_list.append(record)


def todays_date():
    return datetime.today()


def render_reviews(reviews):
    if STORAGE == 'database':
        for review in reviews:
            try:
                review['date'] = review['date'].strftime("%b %d %Y %I:%M%p")
                yield review
            except:
                yield review
    else:
        for review in reviews:
            rendered_review = {k: v for k,v in review.items()}
            rendered_review['date'] = review['date'].strftime("%b %d %Y %I:%M%p")
            yield rendered_review


def is_fuzzy_match(search_term, string):
    return fuzz.ratio(search_term.lower(), string.lower()) > 90