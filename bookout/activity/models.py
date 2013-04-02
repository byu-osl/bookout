from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from bookout.accounts.models import UserAccount


class Action(polymodel.PolyModel):
	useraccount = ndb.KeyProperty(kind=UserAccount)
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
		other = UserAccount.query(UserAccount.key==self.connection).get()
		#self.useraccount.add_connection(other)     								 THIS NEEDS WORK
		print "You have accepted a connection request from %s" %(other.name)
		#self.cleanup()
	
	def reject(self):
		other = UserAccount.query(UserAccount.key==self.connection).get()
		print "You have rejected a connection request from %s" %(other.name)
		#self.cleanup()

