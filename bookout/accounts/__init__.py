from models import UserAccount
from flaskext import login as flasklogin
import logging

def join(account, remember=False):
	user = UserAccount.create_user(account)
	if user and flasklogin.login_user(user, remember):
		return True
	return False

def login(account, remember=False):
	email = account.email()
	user = UserAccount.get_by_email(email)
	if user and flasklogin.login_user(user, remember):
		return True
	return False

def logout():
	flasklogin.logout_user()

def delete(user):
	if UserAccount.can_delete_user(user):
		return UserAccount.delete_user(user)
	return None

def current_user():
	return flasklogin.current_user

login_required = flasklogin.login_required

