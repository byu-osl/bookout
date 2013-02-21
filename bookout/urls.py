# This file is for lazy loading urls with google app engine.
# It keeps a list of all the urls for the application and routes
# them to the appropriate functions in the views.py file.
#
# Lazy loading Info: http://flask.pocoo.org/docs/patterns/lazyloading/
#  -We are only doing part of what is on this page. We are creating
#   a centralized URL map in this file and one of the functions is a
#   warmup function that loads the views into a new instance when google
#   app engine has to start up a new instance due to load increases. The example
#   on this url shows how to load in the view functions one at a time as needed.
#   Loading in one at a time will cause decorator problems, so to make things
#   easier, we are doing it like this.
#
# Warmup info: http://stackoverflow.com/questions/8235716/how-does-the-warmup-service-work-in-python-google-app-engine

from flask import Flask
from bookout import app, views, api

# Warmup
app.add_url_rule('/_ah/warmup',view_func=views.warmup)

################################ Website landing pages ##################################
# Home page
app.add_url_rule('/',view_func=views.index)

# Lookup book
app.add_url_rule('/search',view_func=views.search)

# Manager user's library
app.add_url_rule('/library',view_func=views.manage_library)

######################## Internal calls (to be called by ajax) ##########################
# Lookup a book
app.add_url_rule('/book/<ISBN>',view_func=views.lookup_book)

# Altering or accessing a user's personal library
#	the following http types should be sent to do their corresponding functions
#		GET - check to see if the given user has the given book
#		POST - add the given book to the user's library
#		DELETE - remove the book from the user's library
app.add_url_rule('/library/<ISBN>', methods = ['GET', 'POST', 'DELETE'], view_func=views.library_requests)

################################### Web service calls ###################################
# Lookup a book from app
app.add_url_rule('/api/v1/book/<ISBN>', view_func=api.get_book)

# Returns all the books in a person's library
app.add_url_rule('/api/v1/library',view_func=api.view_library)

# Alters books in a person's library
#		GET - Get a particular book
#		POST - Add a book to the library
#		DELETE - Deletes a book from a person's library
app.add_url_rule('/api/v1/library/<ISBN>', methods = ['GET','POST','DELETE'], view_func=api.library_book)

##################################### Error Handling ####################################
## Error Handlers
@app.errorhandler(404)
def page_not_found(e):
	return "404 - Page not found", 404

@app.errorhandler(500)
def server_error(e):
	return "500 - Server Error", 500
