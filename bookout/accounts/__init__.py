from models import UserAccount
from flaskext import login as flasklogin
import logging

def login(account, remember=False):
	email = account.email()
	user = UserAccount.get_by_email(email)
	if not user:
		user = UserAccount.create_user(account)
	if flasklogin.login_user(user, remember):
		return True
	return False

def logout():
	flasklogin.logout_user()

def current_user():
	return flasklogin.current_user

login_required = flasklogin.login_required

