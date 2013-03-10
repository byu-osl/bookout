# Set up the application

from flask import Flask
from flaskext.login import LoginManager
import config
from accounts.models import UserAccount,Anonymous

app = Flask('bookout')

import urls

SECRET_KEY = "yeah, not actually a secret"
app.config.from_pyfile('config.py')

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"

login_manager.setup_app(app)

@login_manager.user_loader
def load_user(id):
	return UserAccount.getuser(int(id))

