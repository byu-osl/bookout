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
from bookout import app, views

# Warmup
app.add_url_rule('/_ah/warmup',view_func=views.warmup)

# Home page
app.add_url_rule('/',view_func=views.index)

# Lookup a book
app.add_url_rule('/book/<ISBN>',view_func=views.lookup_book)


## Error Handlers
@app.errorhandler(404)
def page_not_found(e):
	return "404 - Page not found", 404

@app.errorhandler(500)
def server_error(e):
	return "500 - Server Error", 500
