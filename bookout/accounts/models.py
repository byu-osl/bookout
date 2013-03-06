from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api.datastore import Key
from datetime import datetime,timedelta
from flaskext.login import AnonymousUser
import logging


class UserAccount(ndb.Model):
	"""Stored information about a User"""
	
	googleid = ndb.StringProperty()
	username = ndb.StringProperty(required=True)
	
	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.key.id()

	@classmethod
	def getuser(cls,id):
		return UserAccount.get_by_id(id)

	@classmethod
	def get_by_username(cls,username):
		user = cls.query(cls.username==username).get()
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

