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
import accounts.views

# Warmup
app.add_url_rule('/_ah/warmup',view_func=views.warmup)

################################ Website landing pages ##################################
# Home page
app.add_url_rule('/',view_func=views.index)

# Manager user's library
app.add_url_rule('/old-library',view_func=views.manage_library)

# Library
app.add_url_rule('/library',view_func=views.library)

# Network
app.add_url_rule('/network',view_func=views.network)

# Discover
app.add_url_rule('/discover',view_func=views.discover)

# Search
app.add_url_rule('/searchbooks', view_func=views.searchbooks)

# Settings
app.add_url_rule('/settings',view_func=views.settings,methods=["GET","POST"])

# Login
app.add_url_rule('/login',view_func=views.login,methods=["GET","POST"])

# Join
app.add_url_rule('/join',view_func=views.join)

# Handle-join
app.add_url_rule('/handle-join',view_func=views.handle_join)

# About
app.add_url_rule('/about',view_func=views.about)

# Mobile App
app.add_url_rule('/mobileapp',view_func=views.mobile_app)

# Donate
app.add_url_rule('/donate',view_func=views.donate)

# Logout
app.add_url_rule('/logout',view_func=views.logout)

# User Info
app.add_url_rule('/userinfo',view_func=views.user_info)

# Book Info
app.add_url_rule('/bookinfo',view_func=views.book_info)

######################## Internal calls (to be called by ajax) ##########################
# Get book list
app.add_url_rule('/library/mybooklist',view_func=views.get_my_book_list)

# Search for a book
#	The attribute is what part of the book you will search with (isbn, title, auther, etc.)
#		If you want to search for a book disregarding these use "all"
#	The value is the value that should be used in the search
#	The page is which page of results you want to recieve
#	the current page of search results you are viewing is stored in a hidden form called "pageNumber" 
#		returned by the search urls (if none is given, 0 is used)
#	per_page is the number of books you want on each page (if none is given, 10 is used)
app.add_url_rule('/search/<value>', view_func=views.search_for_book)
app.add_url_rule('/search/<attribute>/<value>', view_func=views.search_for_book)

# Altering or accessing a user's personal library
#	the following http types should be sent to do their corresponding functions
#		GET - check to see if the given user has the given book
#		POST - add the given book to the user's library
#		DELETE - remove the book from the user's library
app.add_url_rule('/library/<OLKey>', methods = ['GET', 'POST', 'DELETE'], view_func=views.library_requests)

# Altering or accessing a user's connections to other users
#	the following http types should be sent to do their corresponding functions
#		GET - get all the connections for the current user
#		POST - add a connection between the current user the the given user
#		DELETE - remove the connection between the current user the the given user
app.add_url_rule('/manage_network/<otherUserID>', methods = ['GET', 'POST', 'DELETE'], view_func=views.manage_connections)

# temporary url - simply adds a connection to the given user
#	The end goal is to use POST requests to user for manage_connections (that one also deals with invitations)
app.add_url_rule('/add_connection/<otherUserID>', view_func=views.simple_add_connection)

# Get all the invitations that the current user has recieved
#	returns a JSON object with information about all the user that have sent invites
#		includes the following about each user: name, email, id
app.add_url_rule('/invites', view_func=views.manage_invites)

# Lend a book to another user (will use the user that is currently logged in)
#	parameters:
#		bookCopyID: The id that corresponds to the book that will be lent out
#		userID: The id of the user that the book is being lent to
#	returns:
#		JSON array with a message: success or the reason for a failure
app.add_url_rule('/lend_book/<bookCopyID>/<borrowerID>/<due_date>', view_func=views.lend_book)

# Borrow a book from another user (will use the user that is currently logged in)
#	parameters:
#		bookCopyID: The id that corresponds to the book that will be borrowed
#		userID: The id of the user that the book is being borrowed from
#	returns:
#		JSON array with a message: success or the reason for a failure
app.add_url_rule('/borrow_book/<bookCopyID>/<lenderID>/<due_date>', view_func=views.borrow_book)

# Get all the books that the current user is loaning to another user
#	returns json with the following information for each book:
#		book's title, book's author, id of the bookcopy, borrower id, and borrower name
app.add_url_rule('/lent_books', view_func=views.get_lent_books)

# Get all the books that the current user is borrowing from another user
#	returns json with the following information for each book:
#		book's title, book's author, id of the bookcopy, owner id, and owner name
app.add_url_rule('/borrowed_books', view_func=views.get_borrowed_books)

# Return the given book to it's owner.  Can be called when either the owner or borrower is logged in
#	parameters:
#		bookCopyID: the id of the BookCopy object that is being returned
#	returns:
#		JSON array with a message: success or the reason for a failure
app.add_url_rule('/return_book/<bookCopyID>', view_func=views.return_book)


app.add_url_rule('/search/inNetwork/<OLKey>',view_func=views.see_who_in_network_has_book)

################################### Web service calls ###################################
# Lookup a book from app
app.add_url_rule('/api/v1/book/<ISBN>', view_func=api.get_book)

# Returns all the books in a person's library
app.add_url_rule('/api/v1/library', view_func=api.view_library)

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
