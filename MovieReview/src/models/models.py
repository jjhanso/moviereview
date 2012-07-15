from google.appengine.ext import db

class Movie(db.Model):
    """Models an individual Movie entry"""
    title = db.StringProperty()
    genre = db.StringProperty()
    description = db.StringProperty(multiline=True)
    #review = db.ReferenceProperty(Review, collection_name='reviews')
    
class Review(db.Model):
    """ Models a review for a movie """
    movie = db.ReferenceProperty(Movie, collection_name='reviews')
    user = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    rating = db.RatingProperty()
    details = db.StringProperty(multiline=True)