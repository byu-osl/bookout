# This file is for lazy loading urls with google app engine.
# It keeps a list of all the urls for the application and routes
# them to the appropriate functions in the views.py file.
#
# Lazy loading Info: http://flask.pocoo.org/docs/patterns/lazyloading/
#   We are only doing part of what is on this page. We are creating
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
from views import render_response
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

# User Profile
app.add_url_rule('/user/<userID>',view_func=views.profile)

# Book Info
app.add_url_rule('/bookinfo',view_func=views.book_info)

######################## Internal calls (to be called by ajax) ##########################
# Get book list
#	Returns:
#		JSON object with the following info about each book the user owns
#			last_update, thumbnail_link, OLKey, author, title
app.add_url_rule('/library/mybooklist',view_func=views.get_my_book_list)

# Deletes the current user
app.add_url_rule('/delete',view_func=views.delete_user,methods=['GET'])

# Search for a book
#	Arguements:
#		attribute - what part of the book you will search with (isbn, title, author, etc.)
#			If you want to search for a book disregarding these use "all"
#		value - the value that should be used in the search
#	Returns:
#		JSON object with each book found
app.add_url_rule('/search/<value>', view_func=views.search_for_book)
app.add_url_rule('/search/<attribute>/<value>', view_func=views.search_for_book)

# Altering or accessing a user's personal library
#	the following http types should be sent to do their corresponding functions
#		GET - check to see if the current user has the given book
#		POST - add the given book to the user's library
#		DELETE - remove the book from the user's library
app.add_url_rule('/library/<OLKey>', methods = ['GET', 'POST', 'DELETE'], view_func=views.library_requests)

# Altering or accessing a user's connections to other users
#	the following http types should be sent to do their corresponding functions
#		GET - get all the connections for the current user
#		POST - send an connection inviation to another user.
#		DELETE - remove the connection between the current user the the given user
app.add_url_rule('/manage_network/<otherUserID>', methods = ['GET', 'POST', 'DELETE'], view_func=views.manage_connections)

# temporary url - simply adds a connection to the given user
#	The end goal is to use POST requests to user for manage_connections (that one also deals with invitations)
app.add_url_rule('/add_connection/<otherUserID>', view_func=views.simple_add_connection)

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

# Change the due_date of a book that is being borrowed
# If the current user is the owner of the book the date is automaticall changed
# If the current user is the borrower, a notification is sent to the owner and he/she can accept the new due date
#	parameters:
#		bookCopyID: the id of the BookCopy object that is being returned
#		newDueDate: the new date the book will be due.  Must be in the format year-month-day
#	returns:
#		JSON object with a message: success or the reason for the failure
app.add_url_rule('/change_due_date/<bookCopyID>/<newDueDate>', view_func=views.change_due_date)

# Get all the notifications that the current user has recieved
#	returns:
#		JSON object with the following info about each notification:
#			ID, text, confirm_text, confirm_activated, reject_text, and reject_activated
app.add_url_rule('/get_notifications', view_func=views.get_notifications)

# Confirm the notification
# Performs the confirm action on the given notification
#	parameters:
# 		notificationID: the id of the notification to be confirmed
app.add_url_rule('/confirm_notification/<notificationID>', view_func=views.confirm_notification)

# Reject the notification
# Performs the reject action on the given notification
#	parameters:
# 		notificationID: the id of the notification to be rejected
app.add_url_rule('/reject_notification/<notificationID>', view_func=views.reject_notification)


# Search for a book but only within the current user's network
#	parameters:
#		OLKey - the open library key of the book being searched for
#	returns:
#		JSON object with these fields for each finding (username, bookCopyID, available)
app.add_url_rule('/search/inNetwork/<OLKey>',view_func=views.see_who_in_network_has_book)

# Starts the process for the current user to borrow a book.
#	parameters:
#		lenderID - id of the owner of the book
#		bookCopyID - the id of the BookCopy object being borrowed
app.add_url_rule('/setup_book_borrow/<lenderID>/<bookCopyID>',view_func=views.setup_book_borrow_actions)

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
	return render_response('404error.html')

@app.errorhandler(500)
def server_error(e):
	return render_response('500error.html')
