from google.appengine.api import users
from google.appengine.ext import db
import webapp2
import os
import jinja2
import urllib
import urllib2
import simplejson 

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


def get_imdb_json(title):
    url = 'http://www.imdbapi.com/?t=%s' % title.strip().replace(' ', '%20')   
    content = urllib2.urlopen(url).read()
    return simplejson.loads(content)
    
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
        # I guess I could have easily done this with javascript as well, 
        # but I'm figuring this is more about learning python)
        if movie is None and movie_title is not None:
            try:
                json = get_imdb_json(title = movie_title)
                title_guess = json['Title']
                genre_guess = json['Genre']
                desc_guess = json['Plot']
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
            'logout_url': users.create_logout_url("/"),
            'user_url': user_url,
            'user_url_label': url_linktext,
            'title_guess': title_guess,
            'genre_guess': genre_guess,
            'desc_guess': desc_guess
        }

        template = jinja_environment.get_template('main.html')
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


app = webapp2.WSGIApplication([('/', MainPage), 
                              ('/addreview', MovieReview),
                              ('/addmovie', MovieInfo)], debug=True)


