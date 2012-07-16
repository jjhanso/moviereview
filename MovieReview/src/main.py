import webapp2
from controllers import movies


app = webapp2.WSGIApplication([('/', movies.MainPage), 
                                ('/addreview',movies.MovieReview),
                                ('/addmovie', movies.MovieInfo),
                                ('/browse', movies.AllMovies)], debug=True)