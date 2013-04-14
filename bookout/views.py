# Views
from google.appengine.api import users
from flask import Response, jsonify, render_template, request, url_for, redirect, flash
from flaskext.login import login_required, login_user, logout_user
from books.models import Book,BookCopy
from activity.models import RequestToBorrow, WaitingToBorrow
import logging
from decorators import crossdomain
from bookout import app
from utilities.JsonIterable import *
from accounts import login as login_account, logout as logout_account, join as join_account, delete as delete_account, current_user, login_required
from accounts.models import UserAccount
from activity.models import Action
from google.appengine.api import mail
from datetime import date,timedelta
import re

import filters


#mail = Mail(app)

def warmup():
	# https://developers.google.com/appengine/docs/python/config/appconfig#Warmup_Requests
	# This function loads the views into the new instance when
	# one has to start up due to load increases on the app
	return ''

#return (datetime.now() - self.last_update) > timedelta(minutes=1000)

@app.route("/tasks/book_due_reminders")
def book_due_reminders():
	count = 0
	"""find all the books due tomorrow and send reminder emails"""
	books = BookCopy.query(BookCopy.due_date==date.today() + timedelta(days=1)).fetch()
	for book in books:
		count += 1
		owner = UserAccount.query(UserAccount.key==book.owner).get()
		mail.send_mail(sender=owner.email,
			to=UserAccount.query(UserAccount.key==book.borrower).get().email,
			subject="Book Due Soon",
			body="""Hey, remember that book you borrowed on Bookout from me, '%s'? Please get it back to me by tomorrow.
			
Thanks!
%s"""%(Book.query(Book.key==book.book).get().title,owner.name))
	return "%s reminders were sent out" %count

@app.route("/crossdomain")
@crossdomain(origin='*')
def test_view():
	"""test view for checking accessibility of cross-domain ajax requests
	
	"""
	return "this is a response"

def render_response(template, *args, **kwargs):
	"""helper function for adding variables for the template processor
	
	"""
	return render_template(template, *args, user=current_user(), **kwargs)

################################ Website landing pages ##################################
def index():
	# Each user has an invitation link (in /network) which they send to other users to
	# invite them to connect on BookOut. Currently, this is the only method of connecting
	# users. The link adds an argument to the index link (?connect=) with the inviter's
	# user ID. A modal appears in the view if otherUserID is not 0.
	
	# Grab User ID from connection invitation
	otherUserID = request.args.get('connect')
	
	# If no connect argument is present (just a regular visit to the dashboard), set to 0 (ignored in view)
	if otherUserID is None:
		connectionType = 0 #No connection request is being made
		otherUserID = 0
		otherUserName = 0
	else:
		# Get User Name from User ID
		otherUserObj = UserAccount.get_by_id(int(otherUserID))
		# Set invalid objects to invalid
		if otherUserObj is None:
			otherUserID = 0
			otherUserName = 0
			connectionType = 1 #Invalid User ID
		else:
			otherUserName = otherUserObj.name
			connectionType = 2 #Valid User
	
		# Don't let a user connect with him/herself, set to 0 so they get nothing
		if int(otherUserID) == current_user().get_id():
			connectionType = 3 #Own self
			
		# Don't let a user connect with an existing connection
		# if int(otherUserID) matches something in current_user().connected_accounts
		#	connectionType = 4 #Existing Connection
			
	return render_response('home.html',connectUserID=otherUserID,connectUserName=otherUserName,connectType=connectionType)
	
def library():
	booklist = []
	useraccount = current_user()
	for copy in useraccount.get_library():
		book = Book.query(Book.key == copy.book).get()
		book.title = book.title
		book.escapedtitle = re.escape(book.title)
		if copy.borrower is None:
			book.available = True
		else:
			book.available = False
		booklist.append(book)
	return render_response('managelibrary.html', myBooks=booklist)
	
def network():
	return render_response('network.html')
	
def discover():
	user = current_user()
	booksInNetwork = {}
	string = ""
	for connection in user.get_connections():
		u = UserAccount.getuser(connection.id())
		for copy in u.get_library():
			book = Book.query(Book.key == copy.book).get()
			booksInNetwork[copy.OLKey] = book
	
	return render_response('discover.html',books=booksInNetwork)
	
def searchbooks():
	booklist = {}
	searchterm = request.args.get('value')
	attr = request.args.get('refineSearch')
	
	if attr == "all":
		attr = None
	
	if searchterm is None:
		searchterm = ""
	else:
		searchterm = searchterm.lstrip()
		
	if searchterm is None or searchterm == "":
		pass
	else:
		cur_user = current_user()
		logging.info(cur_user)
		if not cur_user.is_authenticated():
			#Assume no books in library or network, return results only
			booklist = Book.search_books_by_attribute(searchterm,attr)
			for book in booklist:
				booklist[book] = booklist[book].to_dict()
				
				#Assume not in booklist or networkbooklist
				booklist[book]["inLibrary"] = "False"
				booklist[book]["inNetwork"] = "False"
		
		else:
			user = current_user()
			
			#Create a dictionary of the user's books
			mybooklist = {}
			for copy in user.get_library():
				mybooklist[copy.OLKey] = copy
				
			#Create a dictionary of the books in my network
			networkbooklist = {}
			string = ""
			for connection in user.get_connections():
				u = UserAccount.getuser(connection.id())
				for copy in u.get_library():
					networkbooklist[copy.OLKey] = copy

			booklist = Book.search_books_by_attribute(searchterm,attr)
			for book in booklist:
				booklist[book] = booklist[book].to_dict()

				if booklist[book]['OLKey'] in mybooklist:
					booklist[book]["inLibrary"] = "True"
				else:
					booklist[book]["inLibrary"] = "False"
					
				if booklist[book]['OLKey'] in networkbooklist:
					booklist[book]["inNetwork"] = "True"
				else:
					booklist[book]["inNetwork"] = "False"
				
	return render_response('searchbooks.html', books=booklist, search=searchterm, attribute=attr)
	
def settings():
	if request.method == 'POST' and "displayName" in request.form and "lendingLength" in request.form and "notifications" in request.form and "additionalInfo" in request.form:
		user = current_user()
		name = request.form["displayName"]
		length = request.form["lendingLength"]
		notify = request.form["notifications"]
		info = request.form["additionalInfo"]
		if user.update(name, length, notify, info):
			return "Success"
		else:
			return False
	return render_response('settings.html')
	
def about():
	return render_response('aboutbookout.html')
	
def mobile_app():
	return render_response('mobileapp.html')
	
def donate():
	return render_response('donate.html')

@login_required
def profile(userID):
	profile_user = UserAccount.get_by_id(int(userID))
	user = current_user()
	if not profile_user:
		return render_response('profile.html',exists=False)
	if user.is_connected(profile_user):
		library = []
		for copy in profile_user.get_library():
			book = Book.query(Book.key == copy.book).get()
			library.append(book)
			if copy.borrower is None:
				book.available = True
			else:
				book.available = False
			book.copyid = copy.key.id()
		return render_response('profile.html',profile_user=profile_user,library=library)
	return render_response('profile.html',connected=False)
	
def book_info():
	return render_response('bookinfo.html')

def send_connection_request(otherUserID):
	#otherUserName = UserAccount.get_by_id(otherUserID)
	return render_response('connectionrequest.html',connectUserID=otherUserID)
	
def join():
	return render_response('join.html')

def handle_join():
	g_user = users.get_current_user()
	if g_user:
		if join_account(g_user):
			return redirect(request.args.get("next") or url_for("index"))
		else:
			return render_response('join.html',invalid_join=True)
	return redirect(users.create_login_url(request.url))

def login():
	g_user = users.get_current_user()
	if g_user:
		if login_account(g_user):
			return redirect(request.args.get("next") or url_for("index"))
		else:
			return render_response('join.html',invalid_login=True)
	return redirect(users.create_login_url(request.url))

def logout():
	# Logs out Bookout user
	logout_account()
	#return redirect("/")
	# Logs out Google user
	return redirect(users.create_logout_url("/"))

@login_required
def manage_library():
	retstring = ""
	for copy in current_user().get_library():
		retstring += copy.display() + "<br>"
	return  render_template('library.html',username=current_user().name,books=get_my_book_list(),logout_url="/logout")

######################## Internal calls (to be called by ajax) ##########################
def delete_user():
	cur_user = current_user()
	if not cur_user:
		logging.info("there is not a user logged in")
		return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('library_requests',ISBN=ISBN))
	if delete_account(cur_user):
		return "Success"
	return ""

def library_requests(OLKey):
	cur_user = current_user()
	if not cur_user:
		logging.info("there is not a user logged in")
		return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('library_requests',ISBN=ISBN))
		
	if request.method == 'GET':
		#check the database to see if the book is in the user's library
		book = Book.get_by_key(OLKey)
		if book:
			if cur_user.get_book(book):
				return book.title
			else:
				return "You do not have this book in your library"
		else:
			return "This book was not found"
	elif request.method == 'POST':
		#add the book to the user's library
		#If not found, add it to the cache, then to the user's library
		book = Book.get_by_key(OLKey)

		if not book:
			return "Book " + OLKey + " was not found"
		else:
			if cur_user.get_book(book):
				return "This book is already in your library"
			cur_user.add_book(book)
			return "Book " + OLKey + " was added to your library"
	elif request.method == 'DELETE':	
		#remove the book from the user's library
		book = Book.get_by_key(OLKey)
		if not book:
			return "Book not found"
		else:
			if cur_user.get_book(book):
				cur_user.remove_book(book)
			return "Successfully deleted " + OLKey + " from your library"
	else:
		#this should never be reached
		return "Error: http request was invalid"

def get_my_book_list():
	cur_user = current_user()
	if not cur_user:
		logging.info("there is not a user logged in")
		return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('manage_library'))

	books = {}
	counter = 0
	for copy in cur_user.get_library():
		book = Book.query(Book.key == copy.book).get()
		books[counter] = book.to_dict()
		counter += 1
	return jsonify(JsonIterable.dict_of_dict(books))

def search_for_book(value, attribute=None):
	books = Book.search_books_by_attribute(value,attribute)
	if len(books) == 0:
		return jsonify({"Message":"No books found"})
	else:
		return jsonify(JsonIterable.dict_of_dict(books))

def manage_connections(otherUserID = None):
	cur_user = current_user()

	if request.method == 'GET':
		connections = cur_user.get_all_connections()
		users = []
		result = "you have " + str(len(connections)) + " connections"
		for connection in connections:
			result += "<br>" + connection.name
			user = dict()
			user["name"] = connection.name
			user["email"] = connection.email
			#user["username"] = connection.username
			user["id"] = connection.get_id()
			users.append(user)
		return jsonify({"connectedUsers":users})
	elif request.method == 'POST':
		cur_user = current_user()
		otherUser = UserAccount.getuser(int(otherUserID))
		result = cur_user.send_invite(otherUser)
		if(result == 0):
			return jsonify({"Message":"Invitation successfully sent"})
		elif(result == 1):
			return jsonify({"Message":"Connection already existed"})
		elif(result == 2):
			return jsonify({"Message":"Cannot create a connection with yourself"})
	elif request.method == 'DELETE':
		cur_user = current_user()
		otherUser = UserAccount.getuser(int(otherUserID))
		if cur_user.remove_connection(otherUser):
			return jsonify({"Message":"Connection successfully deleted"})
		else:
			return jsonify({"Message":"Connection didn't existed"})
	else:
		#this should never be reached
		return jsoningy({"Message":"Error: http request was invalid"})
		
def simple_add_connection(otherUserID):
	cur_user = current_user()
	otherUser = UserAccount.getuser(int(otherUserID))
	if cur_user.add_connection(otherUser):
		return jsonify({"Message":"Connection successfully created"})
	else:
		return jsonify({"Message":"Connection already existed"})

def lend_book(bookCopyID, borrowerID, due_date = None):
	cur_user = current_user()
	return cur_user.lend_book(int(bookCopyID), int(borrowerID), due_date)

def borrow_book(bookCopyID, lenderID, due_date = None):
	cur_user = current_user()
	return cur_user.borrow_book(int(bookCopyID), int(lenderID), due_date)

def get_lent_books():
	cur_user = current_user()
	lentBooks = []
	for bookcopy in cur_user.get_lent_books():
		book = Book.get_by_id(bookcopy.book.id())
		borrower = UserAccount.get_by_id(bookcopy.borrower.id())
		bookInfo = dict()
		bookInfo["title"] = book.title
		bookInfo["author"] = book.author
		bookInfo["copyID"] = bookcopy.key.id()
		bookInfo["borrowerId"] = bookcopy.borrower.id()
		bookInfo["borrower"] = borrower.name
		bookInfo["due_date"] = str(bookcopy.due_date)
		lentBooks.append(bookInfo)
	return jsonify({"lentBooks":lentBooks})

def get_borrowed_books():
	cur_user = current_user()
	borrowedBooks = []
	for bookcopy in cur_user.get_borrowed_books():
		book = Book.get_by_id(bookcopy.book.id())
		owner = UserAccount.get_by_id(bookcopy.owner.id())
		bookInfo = dict()
		bookInfo["title"] = book.title
		bookInfo["author"] = book.author
		bookInfo["copyID"] = bookcopy.key.id()
		bookInfo["ownerId"] = bookcopy.owner.id()
		bookInfo["owner"] = owner.name
		bookInfo["due_date"] = str(bookcopy.due_date)
		borrowedBooks.append(bookInfo)
	return jsonify({"borrowedBooks":borrowedBooks})

def return_book(bookCopyID):
	cur_user = current_user()
	result = cur_user.return_book(bookCopyID)
	return jsonify({"Message":result})

def change_due_date(bookCopyID, newDueDate):
	cur_user = current_user()
	result = cur_user.change_due_date(bookCopyID, newDueDate)
	return jsonify({"Message":result})	
	
def see_who_in_network_has_book(OLKey):
	user = current_user()

	networkuserlist = {}
	string = ""
	for connection in user.get_connections():
		u = UserAccount.getuser(connection.id())
		for copy in u.get_library():
			if copy.OLKey == OLKey:
				user = {}
				user["username"] = u.name
				user["bookCopyID"] = copy.key.id()
				if copy.borrower == None:
					user["available"] = "True"
				else:
					user["available"] = "False"
				networkuserlist[u.get_id()] = user

	return jsonify(networkuserlist)
	
def setup_book_borrow_actions(lenderID, bookCopyID):
	borrower = current_user()
	lender = UserAccount.getuser(int(lenderID))
	bookCopy = BookCopy.get_by_id(int(bookCopyID))
	
	rtb1 = RequestToBorrow()
	rtb1.useraccount = lender.key
	rtb1.connection = borrower.key
	rtb1.book = bookCopy.key
	rtb1.put()
	
	wtb1 = WaitingToBorrow()
	wtb1.useraccount = borrower.key
	wtb1.connection = lender.key
	wtb1.book = bookCopy.key
	wtb1.put()
	return jsonify({"Message":"OK"})


def get_notifications():
	cur_user = current_user()
	notifications = []
	for notification in cur_user.pending_actions:
		info = dict()
		info["ID"] = notification.key.id()
		info["text"] = notification.text
		info["confirm_text"] = notification.accept_text
		info["confirm_activated"] = notification.can_accept
		info["reject_text"] = notification.reject_text
		info["reject_activated"] = notification.can_reject
		notifications.append(info)
	return jsonify({"notifications": notifications})

def confirm_notification(notificationID):
	action = Action.get_by_id(int(notificationID))
	result = action.confirm()
	return result

def reject_notification(notificationID):
	action = Action.get_by_id(int(notificationID))
	result = action.reject()
	return result
