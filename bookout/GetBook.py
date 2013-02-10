from google.appengine.api import urlfetch
from flask import jsonify
import json

################################ Public Methods #################################

#Temporarily using this variable until the datastore is set up
cache = {}


#Returns a JSON representing the book object
def get_book(ISBN):

	#Check cache
	if not is_book_in_cache(ISBN):
		#Book is not in the cache, so update the cache from the web service
		update_book_cache(ISBN)
	
	#Get book from cache
	return jsonify(get_book_from_cache(ISBN))
		
################################ Private Methods #################################

def external_book_search(ISBN):
	return search_google_books(ISBN)

#Calls the appropriate api then stores the data in the cache
def update_book_cache(ISBN):
	book = search_google_books(ISBN)
	
	cache[ISBN] = book

#Looks for a book in the datastore cache
def is_book_in_cache(ISBN):
	return cache.has_key(ISBN)

#Gets the book from the cache
def get_book_from_cache(ISBN):
	return cache[ISBN]

#Searches the google books api and returns a dictionary of the responses
def search_google_books(ISBN):
	apiKey = "AIzaSyCX-e_MsPRJzpAc7rhQuh0W7pg2OGVVJ8A"
	
	#Search to get volumes associated with this isbn.
	# There should only ever really be one returned, but if there are more than one, this returns the first
	url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + ISBN + "&key=" + apiKey
	response = urlfetch.fetch(url)
	if response.status_code == 200:
		json_response = response.content
		data = json.loads(json_response)
		for volume in data["items"]:
			volumeID = volume["id"]
			#For each volume returned, get the data on that book
			url = "https://www.googleapis.com/books/v1/volumes/" + volumeID + "?key=" + apiKey
			response = urlfetch.fetch(url)
			if response.status_code == 200:
				book_json = json.loads(response.content)
				break;
	
	return book_json

