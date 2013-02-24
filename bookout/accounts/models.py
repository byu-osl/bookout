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
		"""retrieve the user's library
		
		Return value:
		list of BookCopy objects owned by the user
		"""
		from bookout.books.models import BookCopy
		return BookCopy.query(BookCopy.account==self.key).fetch()
	
	def get_book(self,book):
		"""retrieve the user's copy of a particular book
		
		Arguments:
		book - the Book being retrieved

		Return value:
		the user's BookCOpy object associated with the provided Book; None if the user does not own book
		"""
		from bookout.books.models import BookCopy
		mybook = BookCopy.query(BookCopy.book==book.key,BookCopy.account==self.key).get()
		return mybook
	
	def add_book(self,book):
		"""add a personal copy of a book to a user's account
		
		Arguments:
		book - Book object being attached to the User

		Return Value:
		a BookCopy instance that links the User to the Book; None if the Book could not be linked
		"""
		from bookout.books.models import BookCopy
		bookcopy = BookCopy(book=book.key,account=self.key)
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
		bookcopy = BookCopy.query(BookCopy.book==book.key,BookCopy.account==self.key).get()
		if bookcopy:
			bookcopy.key.delete()
		return bookcopy
	

