from models import UserAccount
from flaskext import login as flasklogin
import logging

def authenticate(username=None,password=None):
	account = UserAccount.get_by_username(username)
	if account: 
		logging.debug("AUTHENTICAION ATTEMPT: valid username provided (%s)" %(username))
	else:
		if not username:
			username = "no username provided"
		logging.info("AUTHENTICATION ATTEMPT: invalid username (%s)" %(username))
	return account

def login(account, remember=False):
	if flasklogin.login_user(account, remember):
		return True
	return False

def logout():
	flasklogin.logout_user()

def current_user():
	return flasklogin.current_user

login_required = flasklogin.login_required

