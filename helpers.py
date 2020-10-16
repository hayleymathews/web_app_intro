from datetime import datetime


def get_reviews(reviews_table,
                search_terms=None,
                order_field='date'):

    if search_terms:
        query = {'title': {'$regex': search_terms, '$options': 'i'}}
    else:
        query = {}
    
    sort_by = [(order_field, -1)]

    return render_reviews(reviews_table.find(query, {'_id': 0}).sort(sort_by))


def get_average_rating(reviews_table,
                       search_terms=None):
    if search_terms:
        query = {'title': {'$regex': search_terms, '$options': 'i'}}
    else:
        query = {}
    
    group = {'_id': None, 'avg': {'$avg': '$rating'}}

    pipeline = [{'$match': query},
                {'$group': group}]
    
    rating = reviews_table.aggregate(pipeline).next()

    return rating['avg']


def save_review(reviews_table,
                author,
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

    reviews_table.insert_one(record)


def todays_date():
    return datetime.today()


def render_reviews(reviews):
    for review in reviews:
        try:
            review['date'] = review['date'].strftime("%b %d %Y %I:%M%p")
            yield review
        except:
            yield review
