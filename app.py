import os

from pymongo import MongoClient
# from mongoengine import connect


from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap

from helpers import get_reviews, save_review, get_average_rating


app = Flask(__name__)
Bootstrap(app)

mongo_uri = "mongodb://localhost:27017/"
mongo_conn = MongoClient(mongo_uri)
db = mongo_conn['reviewer']
reviews_table = db['reviews']

GENRES = ['Horror', 'Science Fiction', 'Comedy', 'Drama', 'Action']


@app.route('/', methods=['GET'])
def index():

    reviews = get_reviews(reviews_table)

    return render_template('index.html', reviews=reviews)


@app.route('/review/create', methods=['GET', 'POST'])
def add_review():
    if request.method == 'GET':
        return render_template('review.html', genres=GENRES)
    
    post_data = request.form.to_dict()
    author = post_data['author']
    title = post_data['title']
    genre = post_data['genre']
    rating = post_data['rating']
    review = post_data['review']

    save_review(reviews_table,
                author,
                title,
                genre,
                rating,
                review)
    
    return redirect(url_for('.index'))

@app.route('/search', methods=['POST'])
def search():
    post_data = request.form.to_dict()

    search_terms = post_data.get('terms')

    reviews = get_reviews(reviews_table,
                          search_terms,
                          order_field='rating')

    rating = get_average_rating(reviews_table,
                                search_terms)

    return render_template('movie.html',
                           movie=search_terms.title(),
                           avg_rating=rating,
                           reviews=reviews)

if __name__ == '__main__':
    app.run(debug=True)

