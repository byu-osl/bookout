import datetime

# Some data types are not json iterable. This utility
#  class iterates over data structures and converts the
#  non iterable items into iterable items. All methods
#  then return a copy of the original structure so the
#  original structure is never modified.
class JsonIterable:
	
	# Convert non iterable items in a dictionary
	@staticmethod
	def dictionary(obj):
		copy = obj
		for key, value in copy.iteritems():
			if type(value) is datetime.datetime:
				copy[key] = str(value)
		return copy
	
	# Convert non iterable items in a dictionary
	#  of dictionaries
	@staticmethod
	def dict_of_dict(obj):
		copy = obj
		for key, value in copy.iteritems():
			copy[key] = JsonIterable.dictionary(value)
		return copy
