from google.appengine.api import urlfetch
from flask import jsonify
import json
from bookout.config import google_api_key
import logging

def external_book_search(ISBN):
	book = search_google_books(ISBN)
	return book

#Searches the google books api and returns a json object of the book or False if the book is not found
def search_google_books(ISBN):
	
	#Search to get volumes associated with this isbn.
	# There should only ever really be one returned, but if there are more than one, this returns the first
	url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + ISBN + "&key=" + google_api_key
	response = urlfetch.fetch(url)
	try:
		if response.status_code == 200:
			json_response = response.content
			data = json.loads(json_response)
			if int(data["totalItems"]) > 0:
				for volume in data["items"]:
					volumeID = volume["id"]
					#For each volume returned, get the data on that book
					url = "https://www.googleapis.com/books/v1/volumes/" + volumeID + "?key=" + google_api_key
					response = urlfetch.fetch(url)
					if response.status_code == 200:
						book_json = json.loads(response.content)
						break;
				return book_json
	except:
		pass

	return False	


def external_book_search_by_attribute(attribute, value, page, per_page=10):
	book = search_google_books_by_attribute(attribute, value, page, per_page)
	return book

#Searches the google books api and returns a json object of the book or False if the book is not found
def search_google_books_by_attribute(attribute, value, page, per_page=10):	
	#Search to get volumes associated with this isbn.
	# There should only ever really be one returned, but if there are more than one, this returns the first
	if(attribute == "all"):
		query = value
	elif(attribute == "ISBN"):
		query = "isbn:" + value
	elif(attribute == "title"):
		query = "intitle:" + value
	elif(attribute == "author"):
		query = "inauthor:" + value
	else:
		logging.debug("GetBook.search_google_books_by_attribute() was called with an invalid attribute: %s" %attribute)
		return None
	startIndex = "&startIndex=" + str(page * per_page)
	url = "https://www.googleapis.com/books/v1/volumes?q=" + query + startIndex + "&key=" + google_api_key
	response = urlfetch.fetch(url)
	try:
		if response.status_code == 200:
			json_response = response.content
			data = json.loads(json_response)
			return data
	except:
		pass

	return False