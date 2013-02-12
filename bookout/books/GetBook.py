from google.appengine.api import urlfetch
from flask import jsonify
import json

def external_book_search(ISBN):
	book = search_google_books(ISBN)
	return book

#Searches the google books api and returns a json object of the book or False if the book is not found
def search_google_books(ISBN):
	apiKey = "AIzaSyCX-e_MsPRJzpAc7rhQuh0W7pg2OGVVJ8A"
	
	#Search to get volumes associated with this isbn.
	# There should only ever really be one returned, but if there are more than one, this returns the first
	url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + ISBN + "&key=" + apiKey
	response = urlfetch.fetch(url)
	try:
		if response.status_code == 200:
			json_response = response.content
			data = json.loads(json_response)
			if int(data["totalItems"]) > 0:
				for volume in data["items"]:
					volumeID = volume["id"]
					#For each volume returned, get the data on that book
					url = "https://www.googleapis.com/books/v1/volumes/" + volumeID + "?key=" + apiKey
					response = urlfetch.fetch(url)
					if response.status_code == 200:
						book_json = json.loads(response.content)
						break;
				return book_json
	except:
		pass

	return False	


