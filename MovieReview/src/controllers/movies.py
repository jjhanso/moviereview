from google.appengine.api import users

#import Movie and Review models
from models.models import *
import webapp2
import os
import jinja2
import urllib
import urllib2
import json 
import logging

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), os.path.pardir, 'templates')))


    
    
class MainPage(webapp2.RequestHandler):      
    def get(self):

        if users.get_current_user():
            user_url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            user_url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
           
        movie_title=self.request.get('movie_title')
        
        movie_k = db.Key.from_path('Movie', ' ')
        if movie_title:
            movie_k = db.Key.from_path('Movie', movie_title)
            movie = db.get(movie_k)
        else:
            movie = None
        
        title_guess = ''
        genre_guess = ''
        desc_guess = ''     
        # I guess I could have easily done this with jQuery as well on the client side, 
        # but I'm figuring this is more about learning python 
        if movie is None and movie_title is not None:
            try:
                jsonData = get_imdb_json(title = movie_title)
                title_guess = jsonData['Title']
                genre_guess = jsonData['Genre']
                desc_guess = jsonData['Plot']
                #try getting movie again, with guessed title?
                movie_k = db.Key.from_path('Movie', title_guess)
                movie = db.get(movie_k)
            except KeyError:
                title_guess = ''
                genre_guess = ''
                desc_guess = ''
            
        template_values = {
            'movie': movie,
            'title': movie_title,
            'user_url': user_url,
            'user_url_label': url_linktext,
            'title_guess': title_guess,
            'genre_guess': genre_guess,
            'desc_guess': desc_guess
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

            

class MovieReview(webapp2.RequestHandler):
    def post(self):
        movie_title = self.request.get('movie_title')
        movie_k = db.Key.from_path('Movie', movie_title)
        movie = db.get(movie_k)
        
        #create new review for movie
        review = Review()
        review.movie = movie
        if users.get_current_user():
            review.user = users.get_current_user().nickname()
        
        try:
            review.rating = int(self.request.get('rating'))
        except ValueError:
            review.rating = 1
            
        review.details = self.request.get('review')
        review.put()
        self.redirect('/?' + urllib.urlencode({'movie_title': movie_title}))
        
class MovieInfo(webapp2.RequestHandler):
    def post(self):
        movie_title = self.request.get('movie_title')
        if movie_title:
            movie = Movie(key_name=movie_title)
            movie.title = movie_title
            movie.genre = self.request.get('genre')
            movie.description = self.request.get('description') 
            movie.put()
            
        self.redirect('/?' + urllib.urlencode({'movie_title': movie_title}))

class AllMovies(webapp2.RequestHandler):
    def get(self):
        #code duplification... should put in function.
        if users.get_current_user():
            user_url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            user_url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        last_cursor = self.request.get('cursor')
        #if not last_cursor:
        #    last_cursor = '-1'
            
        try:
            movies_to_return = int(self.request.get('results'))
        except ValueError:
            movies_to_return = 2
            
        movie_query = Movie.all().order('title')
        if last_cursor:
            movie_query.with_cursor(last_cursor)
        movies = movie_query.fetch(movies_to_return)
        cursor = movie_query.cursor()
        #prev_cursor = int(cursor) - movies_to_return
        
        template_values = {
            'movies': movies,
            'user_url': user_url,
            'user_url_label': url_linktext,
            'next_cursor': cursor 
            #'prev_cursor': prev_cursor
        }
        template = jinja_environment.get_template('browse.html')
        self.response.out.write(template.render(template_values))
        
    
# Method to go out and grab movie information if the movie searched for does not exist in our data store
def get_imdb_json(title):
    url = 'http://www.imdbapi.com/?t=%s' % title.strip().replace(' ', '%20')   
    content = urllib2.urlopen(url).read()
    return json.loads(content)



