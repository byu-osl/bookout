# Views
from google.appengine.api import users
from flask import Response, jsonify, render_template, request, url_for, redirect, flash
from flaskext.login import login_required,login_user,logout_user
import flaskext
from books.models import Book
from accounts.models import UserAccount
import logging
from decorators import crossdomain
from bookout import app

def warmup():
	# https://developers.google.com/appengine/docs/python/config/appconfig#Warmup_Requests
	# This function loads the views into the new instance when
	# one has to start up due to load increases on the app
	return ''





def login():
	#if flaskext.login.current_user.is_authenticated():
	#	# user is already logged in, redirect 
	#	return redirect(request.args.get("next") or url_for("library"))
	if request.method == "POST" and "username" in request.form:
		username = request.form["username"]
		user = UserAccount.get_by_username(username)
		if user:
			if login_user(user, remember=False):
				return redirect(request.args.get("next") or url_for("library"))
			else:
				flash("Sorry, but you could not log in.")
		else:
			flash(u"Invalid username.")
	return render_template("login.html")

def logout():
	logout_user()
	return redirect("/")



@app.route("/crossdomain")
@crossdomain(origin='*')
def test_view():
	return "this is a response"



################################ Website landing pages ##################################
def index():
	return render_template('home.html', loggedin=True)
	
def library():
	return render_template('managelibrary.html', loggedin=True)
	
def network():
	return render_template('managenetworkconnections.html', loggedin=True)
	
def discover():
	return render_template('discover.html', loggedin=True)
	
def settings():
	return render_template('settings.html', loggedin=True)
	
#def login():
#	return render_template('signin.html', loggedin=False)
	
def sign_up():
	return render_template('join.html', loggedin=False)
	
def about():
	return render_template('aboutbookout.html', loggedin=False)
	
def mobile_app():
	return render_template('mobileapp.html', loggedin=False)
	
def donate():
	return render_template('donate.html', loggedin=False)

@login_required
def manage_library():
	retstring = ""
	for copy in flaskext.login.current_user.get_library():
		retstring += copy.display() + "<br>"
	return  render_template('library.html',username=flaskext.login.current_user.username,books=get_my_book_list(),logout_url="/logout")
	
def logout_url():
	return users.create_logout_url(url_for('index'))

######################## Internal calls (to be called by ajax) ##########################
def library_requests(ISBN):
	useraccount = flaskext.login.current_user
	#if not useraccount:
	#	logging.info("there is not a user logged in")
	#	return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('library_requests',ISBN=ISBN))
		
	if request.method == 'GET':
		#check the database to see if the book is in the user's library
		book = Book.get_by_isbn(ISBN)
		if book:
			if useraccount.get_book(book):
				return book.title
			else:
				return "You do not have this book in your library"
		else:
			return "This book was not found"
	elif request.method == 'POST':
		#add the book to the user's library
		#If not found, add it to the cache, then to the user's library
		book = Book.get_by_isbn(ISBN)

		if not book:
			return "Book " + ISBN + " was not found"
		else:
			if useraccount.get_book(book):
				return "This book is already in your library"
			useraccount.add_book(book)
			return "Book " + ISBN + " was added to " + users.get_current_user().nickname() + "'s library"
	elif request.method == 'DELETE':	
		#remove the book from the user's library
		book = Book.get_by_isbn(ISBN)
		if not book:
			return "Book not found"
		else:
			if useraccount.get_book(book):
				useraccount.remove_book(book)
			return "Successfully deleted " + ISBN + " from your library"
	else:
		#this should never be reached
		return "Error: http request was invalid"

def get_my_book_list():
	useraccount = flaskext.login.current_user
	#if not useraccount:
	#	logging.info("there is not a user logged in")
	#	return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('manage_library'))

	retstring = "<table>"
	for copy in useraccount.get_library():
		book = Book.query(Book.key == copy.book).get()
		retstring += "<tr><td>" + book.title + "</td><td><button onclick=\"remove_book('" + book.isbn + "');\">Remove</button></td></tr>"
	retstring += "</table>"
	return retstring

def search_for_book(attribute, value, page = 0, per_page=10):
	html = "<html><body>"
	books = Book.search_by_attribute(int(page), int(per_page), attribute, value)
	if books == False:
		return "No books found"
	for book in books:
		html += "<div>Title: " + book.title
		html += "<br>Author: " + book.author
		html += "<br>ISBN: " + book.isbn
		html += "<br></div>"
	html += "<form type=\"hidden\" name=\"pageNumber\" value=\"" + str(page) + "\">"
	html += "</body></html>"
	return html
