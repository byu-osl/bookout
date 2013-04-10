from google.appengine.ext import ndb
from datetime import datetime,timedelta
import logging
from bookout.accounts.models import UserAccount
import urllib
from google.appengine.api import urlfetch
import json

class Book(ndb.Model):
	"""Cached representation of a book"""
	OLKey = ndb.StringProperty(required=True)
	last_update = ndb.DateTimeProperty()
	title = ndb.StringProperty(required=True)
	author = ndb.StringProperty(required=True)
	thumbnail_link = ndb.StringProperty(required=True)
	
	def update_cache(self):
		"""update cached information about the book using the external book apis
		
		Book must have an open library key specified or this will always return False
		
		"""
		if self.OLKey:
			logging.debug("update_cache(%s)" % self.OLKey)
			book_data = Book.search_books_by_attribute(value=self.OLKey, attribute=None, cache=True)

	def cache_expired(self):
		"""determine if the cached information in the database needs to be refreshed
		
		"""
		return (datetime.now() - self.last_update) > timedelta(minutes=1000)
	
	@classmethod
	def get_by_key(cls,key=None):
		"""Convert an open library key to a Book object
		
		This is a factory method that converts an open library key into a Book object (if possible),
		abstracting away any caching/external APIs necessary to the Book's use
		
		Arguments:
		key -- the key being searched
		
		Return value:
		An instance of a Book object with the given OL key; if the key could not be resolved
		to a Book object, returns None
		
		"""
		if not key:
			logging.error("Book.get_by_key() called without an open library key")
			return None
		logging.debug("Book.get_by_key(%s)" % key)
		book = Book.query(Book.OLKey==key).get()
		if book:
			logging.debug("Key:%s was found in the book cache" % key)
			if book.cache_expired():
				book.update_cache()
		else:
			logging.debug("Key:%s not found in cache; performing external search" % key)
			book = Book(OLKey=key)
			book.update_cache()
			book = Book.query(Book.OLKey==key).get()
		return book
	
	@classmethod
	def search_books_by_attribute(self, value, attribute = None, cache = False):
		# Search with 'attribute = None' when searching for an OLID
		value = urllib.quote(value)
		books = {}
		if(attribute == None):
			query = "q=" + value
		elif(attribute == "ISBN"):
			query = "isbn=" + value
		elif(attribute == "title"):
			query = "title=" + value
		elif(attribute == "author"):
			query = "author=" + value
		else:
			logging.debug("GetBook.search_books_by_attribute() was called with an invalid attribute: %s" %attribute)
			return books
		url = "http://openlibrary.org/search.json?" + query
		response = urlfetch.fetch(url)
		counter = 0
		try:
			if response.status_code == 200:
				json_response = response.content
				data = json.loads(json_response)
				for book in data['docs']:
					curBook = Book(OLKey=None)
					curBook.OLKey = book['key']
					if 'title' in book:
						curBook.title = book['title']
					else:
						curBook.title = ""
				
					if 'author_name' in book:
						curBook.author = book['author_name'][0]
						for i in range(1, len(book['author_name'])):
							curBook.author += ", " + book['author_name'][i]
					else:
						curBook.author = ""
				
					if 'cover_i' in book:
						curBook.thumbnail_link = "http://covers.openlibrary.org/b/id/" + str(book['cover_i']) + "-M.jpg"
					else:
						curBook.thumbnail_link = ""
				
					curBook.last_update = datetime.now()
					if cache == True:
						curBook.put()
					books[counter] = curBook
					counter += 1
		except:
			pass
		return books

class BookCopy(ndb.Model):
	"""A model for linking User to Books
	
	This method was chosen over a List object on the User Account because this allows more 
	flexibility for adding additional information about a particular copy of a Book
	
	"""
	
	book = ndb.KeyProperty(kind=Book)
	OLKey = ndb.StringProperty(required=True)
	owner = ndb.KeyProperty(kind=UserAccount)
	borrower = ndb.KeyProperty(kind=UserAccount)
	due_date = ndb.DateProperty()

	def display(self):
		book = Book.query(Book.key == self.book).get()
		return book.title

	def lend(self, borrowerID, date = None):
		import datetime
		borrower = UserAccount.getuser(borrowerID)
		owner = UserAccount.get_by_id(self.owner.id())
		self.borrower = borrower.key
		if(date):
			self.due_date = datetime.datetime.strptime(date, '%Y-%m-%d');
		else:
			self.due_date = datetime.datetime.now() + datetime.timedelta(days=int(owner.lending_length))

	def return_book(self):
		self.borrower = None
		self.due_date = None

	def update_due_date(self, date):
		import datetime
		self.due_date = datetime.datetime.strptime(date, '%Y-%m-%d');

	def get_due_date(self):
		return self.due_date


