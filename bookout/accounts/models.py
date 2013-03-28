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

	connected_accounts = ndb.StructuredProperty(Connection,repeated=True)
	invites_recieved = ndb.StructuredProperty(Connection,repeated=True)
	
	@property
	def connections(self):
		return self.connected_accounts

	def get_network_books(self):
		from bookout.books.models import BookCopy
		return BookCopy.query(BookCopy.owner.IN(self.get_connections())).fetch()
	
	def get_connections(self):
		return UserAccount.query(UserAccount.connections.user == self.key).fetch(keys_only=True)
	
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
		bookcopy = BookCopy(book=inBook.key,owner=self.key)
		bookcopy.put()
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
		return bookcopy
	
	def add_connection(self, otherUser, reciprocate = True, confirmInvite = False):
		"""add a connection with another user

		Arguments:
		otherUser - a UserAccount object representing the user the connection should be made with
		reciprocate - whether or not the connection should also be added to the other user as well

		Return value:
		True if successfull, false if not
		"""
		connection = Connection(user=otherUser.key)
		if(connection in self.connected_accounts):
			return 1
		if(otherUser.get_id() == self.get_id()):
			return 2
		if(connection in self.invites_recieved or confirmInvite):
			self.connected_accounts.append(connection)
			if(connection in self.invites_recieved):
				self.invites_recieved.remove(connection)
			self.put()
			if reciprocate:
				otherUser.add_connection(self, reciprocate = False, confirmInvite = True)
		else:
			otherUser.add_invite(self)
		return 0

	def just_add_connection(self, otherUser, reciprocate = True):
		"""add a connection with another user without worrying about invites and such
		(parameters and return values are the same as the previous method)
		"""
		connection = Connection(user=otherUser.key)
		if(connection in self.connected_accounts):
			return False
		self.connected_accounts.append(connection)
		self.put()
		if reciprocate:
			otherUser.add_connection(self, reciprocate = False, confirmInvite = True)
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
		connection = Connection(user=inviter.key)
		if(connection not in self.invites_recieved):
			self.invites_recieved.append(connection)
			self.put()

	def lend_book(self, bookID, borrowerID, due_date = None):
		from bookout.books.models import BookCopy
		bookCopy = BookCopy.get_by_id(bookID)
		if(bookCopy == None):
			return "You Don't have that book"
		bookCopy.lend(borrowerID, due_date)
		bookCopy.put()
		return "Book successfully lent"

	def borrow_book(self, bookID, lenderID, due_date = None):
		from bookout.books.models import BookCopy
		bookCopy = BookCopy.get_by_id(bookID)
		if(bookCopy == None):
			return "The other user does not have that book"
		bookCopy.lend(self.key.id(), due_date)
		bookCopy.put()
		return "Book successfully borrowed"

	def get_lent_books(self):
		from bookout.books.models import BookCopy
		return BookCopy.query(BookCopy.owner==self.key,BookCopy.borrower!=None).fetch()

	def get_borrowed_books(self):
		from bookout.books.models import BookCopy
		return BookCopy.query(BookCopy.borrower==self.key).fetch()
		


class Anonymous(AnonymousUser):
	name = u"Anonymous"
