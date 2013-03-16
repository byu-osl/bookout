from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api.datastore import Key
from datetime import datetime,timedelta
from flaskext.login import AnonymousUser
from werkzeug.security import generate_password_hash, check_password_hash
import logging


class UserAccount(ndb.Model):
	"""Stored information about a User"""
	
	username = ndb.StringProperty(required=True)
	name = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	password = ndb.StringProperty(required=True)

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

	def set_password(self, pw):
		self.password = generate_password_hash(pw)

	def check_password(self, pw):
#		return pw == self.password
		return check_password_hash(self.password, pw)

	@classmethod
	def create_user(cls,name,username,password,email):
		if UserAccount.get_by_username(username):
			return None
		if UserAccount.get_by_email(email):
			return None
		user = UserAccount(username=username,name=name,email=email,password=generate_password_hash(password))
		if user:
			user.put()
			return user
		else:
			return None

	@classmethod
	def getuser(cls,id):
		return UserAccount.get_by_id(id)

	@classmethod
	def get_by_username(cls,username):
		user = cls.query(cls.username==username).get()
		return user
	
	@classmethod
	def get_by_email(cls,email):
		user = cls.query(cls.email==email).get()
		return user

	@classmethod
	def get_current(cls):
		user = users.get_current_user()
		if user:
			# fetch the profile
			uid = user.user_id()
			account = cls.query(cls.googleid==uid).get()
			if not account:
				# create the account
				account = UserAccount(googleid=uid)
				account.put()
			return account
		else:
			return None

	def get_library(self):
		from bookout.books.models import BookCopy
		return BookCopy.query(BookCopy.account==self.key).fetch(20)
	
	def get_book(self,book):
		from bookout.books.models import BookCopy
		book = BookCopy.query(BookCopy.book==book.key,BookCopy.account==self.key).get()
		if book:
			return book
		else:
			return None
	
	def add_book(self,book):
		from bookout.books.models import BookCopy
		bookcopy = BookCopy(book=book.key,account=self.key)
		bookcopy.put()
		return bookcopy
		
	def remove_book(self,book):
		from bookout.books.models import BookCopy
		bookcopy = BookCopy.query(BookCopy.book==book.key,BookCopy.account==self.key).get()
		bookcopy.key.delete()
	

class Anonymous(AnonymousUser):
	name = u"Anonymous"

