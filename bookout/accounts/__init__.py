from models import UserAccount
from flaskext import login as flasklogin

def authenticate(username=None,password=None):
	return  UserAccount.get_by_username(username)

def login(account, remember=False):
	if flasklogin.login_user(account, remember):
		return True
	return False

def logout():
	flasklogin.logout_user()

def current_user():
	return flasklogin.current_user

login_required = flasklogin.login_required

