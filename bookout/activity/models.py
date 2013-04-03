from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from bookout.accounts.models import UserAccount
from bookout.books.models import BookCopy,Book


class Action(polymodel.PolyModel):
	useraccount = ndb.KeyProperty(kind=UserAccount)
	created = ndb.DateTimeProperty(auto_now_add=True)
	text = "This is the default text, it should never show up"
	can_accept = False 
	accept_text = "Accept"
	can_reject = False
	reject_text = "Reject" 
	
	def confirm(self):
		print "CONFIRMED"
	
	def reject(self):
		print "REJECT"
		
	def cleanup(self):
		self.key.delete()


"""
ACTION SUBCLASS TEMPLATE

class MyCustomAction(Action):
	# put any custom attributes here
	text = "Put whatever text here that needs to be displayed to the user"
	can_accept = True # or False if there is no accept option
	accept_text = "Accept" # this is what the button should say when accepting
	can_reject = True # or False if there is no reject option
	reject_text = "Reject" # this is that the button should say when rejecting
	
	def confirm(self):
		# do whatever stuff should be done when the user confirms
	
	def reject(self):
		# do whatever stuff should be done when the user rejects


"""


class ConnectionRequest(Action):
	connection = ndb.KeyProperty(kind=UserAccount)
	
	@property
	def text(self):
		other = UserAccount.query(UserAccount.key==self.connection).get()
		return "%s has requested to connect" %(other.name)
		
	can_accept = True 
	accept_text = "Confirm"
	can_reject = True
	reject_text = "Reject" 
	
	def confirm(self):
		invitee = UserAccount.query(UserAccount.key==self.connection).get()
		invited = UserAccount.query(UserAccount.key==self.useraccount).get()
		invited.add_connection(invitee)
		self.cleanup()
		return "You have accepted a connection request from %s" %(invitee.name)
	
	def reject(self):
		other = UserAccount.query(UserAccount.key==self.connection).get()
		self.cleanup()
		return "You have rejected a connection request from %s" %(other.name)


class RequestToBorrow(Action):
	connection = ndb.KeyProperty(kind=UserAccount)
	book = ndb.KeyProperty(kind=BookCopy)
	
	@property
	def text(self):
		other = UserAccount.query(UserAccount.key==self.connection).get()
		bookcopy = BookCopy.query(BookCopy.key==self.book).get()
		book = Book.query(Book.key==bookcopy.book).get()
		return "%s has requested to borrow '%s' from your library" %(other.name,book.title)
		
	can_accept = True 
	accept_text = "Allow"
	can_reject = True
	reject_text = "Deny" 
	
	def confirm(self):
		other = UserAccount.query(UserAccount.key==self.connection).get()
		bookcopy = BookCopy.query(BookCopy.key==self.book).get()
		book = Book.query(Book.key==bookcopy.book).get()
		print "You have accepted a connection request from %s" %(other.name)
		#self.cleanup()
	
	def reject(self):
		other = UserAccount.query(UserAccount.key==self.connection).get()
		bookcopy = BookCopy.query(BookCopy.key==self.book).get()
		book = Book.query(Book.key==bookcopy.book).get()
		print "You have denied %s permission to borrow %s" %(other.name,book.title)
		#self.cleanup()


class WaitingToBorrow(Action):
	connection = ndb.KeyProperty(kind=UserAccount)
	book = ndb.KeyProperty(kind=BookCopy)
	
	@property
	def text(self):
		other = UserAccount.query(UserAccount.key==self.connection).get()
		bookcopy = BookCopy.query(BookCopy.key==self.book).get()
		book = Book.query(Book.key==bookcopy.book).get()
		return "You have requested to borrow '%s' from %s" %(book.title,other.name)
		
	can_accept = False 
	accept_text = "Allow"
	can_reject = True
	reject_text = "Cancel Request" 
	
	def confirm(self):
		other = UserAccount.query(UserAccount.key==self.connection).get()
		bookcopy = BookCopy.query(BookCopy.key==self.book).get()
		book = Book.query(Book.key==bookcopy.book).get()
		print "You have accepted a connection request from %s" %(other.name)
		#self.cleanup()
	
	def reject(self):
		other = UserAccount.query(UserAccount.key==self.connection).get()
		bookcopy = BookCopy.query(BookCopy.key==self.book).get()
		book = Book.query(Book.key==bookcopy.book).get()
		print "You have denied %s permission to borrow %s" %(other.name,book.title)
		#self.cleanup()




