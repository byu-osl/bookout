from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api.datastore import Key
from datetime import datetime,timedelta
from flaskext.login import AnonymousUser
from werkzeug.security import generate_password_hash, check_password_hash
import logging


class Connection(ndb.Model): 
	user = ndb.KeyProperty(kind="UserAccount")


class UserAccount(ndb.Model):
	"""Stored information about a User"""
	
	name = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	book_count = ndb.IntegerProperty(default=0)
	lending_length = ndb.StringProperty(default="14")
	notification = ndb.StringProperty(default="email")
	info = ndb.StringProperty(default="")

	connected_accounts = ndb.StructuredProperty(Connection,repeated=True)
	invites_recieved = ndb.StructuredProperty(Connection,repeated=True)
	
	@property
	def pending_actions(self):
		from bookout.activity.models import Action
		return Action.query(Action.useraccount == self.key).fetch()
	
	@property
	def connections(self):
		return self.connected_accounts

	def get_network_books(self):
		from bookout.books.models import BookCopy
		return BookCopy.query(BookCopy.owner.IN(self.get_connections())).fetch()
	
	def get_connections(self):
		return UserAccount.query(UserAccount.connected_accounts.user == self.key).fetch(keys_only=True)
	
	def get_all_connections(self):
		connections = []
		for connection in self.connected_accounts:
			connections.append(UserAccount.query(UserAccount.key==connection.user).get())
		return connections
	
	def get_all_invites(self):
		connections = []
		for connection in self.invites_recieved:
			connections.append(UserAccount.query(UserAccount.key==connection.user).get())
		return connections
	
	def update(self,name,lending_length,notifications,info):
		# validate name
		self.name = name
		self.lending_length = lending_length
		self.notification = notifications
		self.info = info
		self.put()
		return True

	def is_authenticated(self):
		"""determine whether the UserAccount is authenticated
		
		This method is required by the flask-login library
		
		Return value:
		True (note: the AnonymousUser object returns False for this method)
		
		"""
		return True

	def is_active(self):
		"""determine whether the UserAccount is active or not
		
		This method is required by the flask-login library
		
		Return value:
		True if the account is active; False otherwise
		
		"""
		return True

	def is_anonymous(self):
		"""determine whether the UserAccount is anonymous
		
		This method is required by the flask-login library
		
		Return value:
		False (note: the AnonymousUser object returns True for this method)
		
		"""
		return False

	def get_id(self):
		"""get the id for this UserAccount
		
		This method is required by the flask-login library
		
		Return value:
		Integer that represents the unique ID of this UserAccount
		
		"""
		return self.key.id()

	@classmethod
	def create_user(cls,g_user):
		if UserAccount.get_by_email(g_user.email()):
			return None
		user = UserAccount(name=g_user.nickname(),email=g_user.email())
		if user:
			user.put()
			return user
		else:
			return None

	@classmethod
	def getuser(cls,id):
		return UserAccount.get_by_id(id)
	
	@classmethod
	def get_by_email(cls,email):
		user = cls.query(cls.email==email).get()
		return user

	def get_library(self):
		"""retrieve the user's library
		
		Return value:
		list of BookCopy objects owned by the user
		"""
		from bookout.books.models import BookCopy
		return BookCopy.query(BookCopy.owner==self.key).fetch()
	
	def get_book(self,book):
		"""retrieve the user's copy of a particular book
		
		Arguments:
		book - the Book being retrieved

		Return value:
		the user's BookCOpy object associated with the provided Book; None if the user does not own book
		"""
		from bookout.books.models import BookCopy
		mybook = BookCopy.query(BookCopy.book==book.key,BookCopy.owner==self.key).get()
		return mybook
	
	def add_book(self,inBook):
		"""add a personal copy of a book to a user's account
		
		Arguments:
		book - Book object being attached to the User

		Return Value:
		a BookCopy instance that links the User to the Book; None if the Book could not be linked
		"""
		from bookout.books.models import BookCopy
		bookcopy = BookCopy(book=inBook.key,owner=self.key,OLKey=inBook.OLKey)
		if bookcopy.put():
			self.book_count = self.book_count + 1
			self.put()
		return bookcopy
		
	def remove_book(self,book):
		"""delete a user's copy of a book
		
		Arguments:
		book - Book object that is to be removed

		Return value:
		the BookCopy instance that was just deleted; None if the BookCopy was not found
		"""
		from bookout.books.models import BookCopy
		bookcopy = BookCopy.query(BookCopy.book==book.key,BookCopy.owner==self.key).get()
		if bookcopy:
			bookcopy.key.delete()
			self.book_count = self.book_count - 1
			self.put()
		return bookcopy
	
	def send_invite(self, otherUser):
		"""sends an invite to another user

		Arguments:
		otherUser - a UserAccount object representing the user that should recieve the invite

		Return value:
		True if successfull, false if not
		"""
		from bookout.activity.models import ConnectionRequest
		connection = Connection(user=otherUser.key)
		if(connection in self.connected_accounts):
			return 1
		if(otherUser.get_id() == self.get_id()):
			return 2
		invitation = ConnectionRequest(useraccount=otherUser.key,connection=self.key)
		invitation.put()
		return 0

		#####This was the old implementation, before the activity class was made
		# connection = Connection(user=otherUser.key)
		# if(connection in self.connected_accounts):
		# 	return 1
		# if(otherUser.get_id() == self.get_id()):
		# 	return 2
		# if(connection in self.invites_recieved or confirmInvite):
		# 	self.connected_accounts.append(connection)
		# 	if(connection in self.invites_recieved):
		# 		self.invites_recieved.remove(connection)
		# 	self.put()
		# 	if reciprocate:
		# 		otherUser.add_connection(self, reciprocate = False, confirmInvite = True)
		# else:
		# 	otherUser.add_invite(self)
		# return 0

	def add_connection(self, otherUser, reciprocate = True):
		"""add a connection with another user without worrying about invites and such
		(parameters and return values are the same as the previous method)
		"""
		connection = Connection(user=otherUser.key)
		if(connection in self.connected_accounts):
			return False
		self.connected_accounts.append(connection)
		self.put()
		if reciprocate:
			otherUser.add_connection(self, reciprocate = False)
		return True
		
	def remove_connection(self, otherUser, reciprocate = True):
		"""remove a connection with another user

		Arguments:
		otherUser - a UserAccount object representing the user with whom the connection should be removed
		reciprocate - whether or not the connection should also be removed from the other user as well

		Return value:
		True if successfull, false if not
		"""
		connection = Connection(user=otherUser.key)
		if(connection not in self.connected_accounts):
			return False
		self.connected_accounts.remove(connection)
		self.put()
		if reciprocate:
			otherUser.remove_connection(self, reciprocate = False)
		return True

	def create_invitation_link(self):
		return "manage_connections/" + str(self.get_id())

	def add_invite(self, inviter):
		"""send an invitation to form a connection with another user

		Arguments:
		inviter: a UserAccount object representing the user that is sending the inviter
		"""
		connection = Connection(user=inviter.key)
		if(connection not in self.invites_recieved):
			self.invites_recieved.append(connection)
			self.put()

	def lend_book(self, bookID, borrowerID, due_date = None):
		"""Lend a book to another user

		Arguments:
		bookID: an ID representing the bookCopy object that will be lent out
		borrowerID: an ID representing the user that will borrow the book
		due_date: the date the book should be returned, 
			if none is given the default for the lender is used

		Return value:
		A string describing the success or failure of the operation
		"""
		from bookout.books.models import BookCopy
		bookCopy = BookCopy.get_by_id(bookID)

		# check to see if the book copy is valid
		if(bookCopy == None):
			return "Invalid book ID"
		if(bookCopy.owner != self.key):
			return "You do not own that book"
		if(bookCopy.borrower != None):
			return "That book is not avaiable to be lent out"

		bookCopy.lend(borrowerID, due_date)
		bookCopy.put()
		return "Book successfully lent"

	def borrow_book(self, bookID, lenderID, due_date = None):
		"""Borrow a book from another user

		Arguments:
		bookID: an ID representing the bookCopy object that will be borrowed
		lenderID: an ID representing the user that will lend the book
		due_date: the date the book should be returned, 
			if none is given the default for the lender is used

		Return value:
		A string describing the success or failure of the operation
		"""
		from bookout.books.models import BookCopy
		bookCopy = BookCopy.get_by_id(bookID)

		# check to see if the book copy is valid
		if(bookCopy == None):
			return "Invalid book ID"
		if(bookCopy.owner.id() != lenderID):
			return "That user does not own this book"
		if(bookCopy.borrower != None):
			return "That book is not avaiable to be lent out"

		bookCopy.lend(self.key.id(), due_date)
		bookCopy.put()
		return "Book successfully borrowed"

	def get_lent_books(self):
		"""Get all the books that the user is currently lending to anther user

		Return Value:
		A list of BookCopy objects of all the the books the user is currently lending
		"""
		from bookout.books.models import BookCopy
		return BookCopy.query(BookCopy.owner==self.key,BookCopy.borrower!=None).fetch()

	def get_borrowed_books(self):
		"""Get all the books that the user is currently borrowing from anther user

		Return Value:
		A list of BookCopy objects of all the the books the user is currently lending
		"""
		from bookout.books.models import BookCopy
		return BookCopy.query(BookCopy.borrower==self.key).fetch()

	def return_book(self, bookCopyID):
		"""Return the given book to it's owner

		Arguments:
		bookCopyID: an ID representing a BookCopy object, the book to be returned

		Return Value:
		A list of BookCopy objects of all the the books the user is currently lending
		"""
		from bookout.books.models import BookCopy
		bookcopy = BookCopy.get_by_id(int(bookCopyID))

		# verify the bookCopyID was valid
		if(bookcopy == None):
			return "Invalid book ID"
		if(bookcopy.owner != self.key and bookcopy.borrower != self.key):
			return "You are not the owner of this book, nor are you borrowing it"

		bookcopy.return_book()
		bookcopy.put()
		return "Book successfully returned to owner"

		


class Anonymous(AnonymousUser):
	name = u"Anonymous"
