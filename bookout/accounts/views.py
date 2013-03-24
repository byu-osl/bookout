from bookout import app
import flaskext


@app.route("/account/connections")
@flaskext.login.login_required
def view_connections():
	user = flaskext.login.current_user
	retval = ""
	for acct in user.get_connections():
		retval += "%s<br>" %acct.name
	return retval


@app.route("/account/allbooks")
@flaskext.login.login_required
def view_connections():
	user = flaskext.login.current_user
	retval = ""
	for bookcopy in user.get_network_books():
		retval += "%s<br>" %bookcopy.display()
	return retval

