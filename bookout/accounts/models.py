from google.appengine.ext import ndb
from google.appengine.api import users
from datetime import datetime,timedelta
import logging


class UserAccount(ndb.Model):
	"""Stored information about a User"""
	
	googleid = ndb.StringProperty(required=True)
	
	def is_authenticated(self):
		return False

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.key()

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
		return BookCopy.query().fetch(20)
	
	def add_book(self,book):
		from bookout.books.models import BookCopy
		bookcopy = BookCopy(book=book.key,account=self.key)
		bookcopy.put()
		return bookcopy

