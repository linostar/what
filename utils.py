import string
import random

class Utils:
	"""utility functions for the app"""

	SITE_URL = "http://46.101.254.74:9870"
	CODE_LENGTH = 8

	@staticmethod
	def generate_quiz_code():
		quiz_code = ""
		random.seed()
		for i in range(Utils.CODE_LENGTH):
			quiz_code += random.choice(string.ascii_letters)
		return quiz_code

	@staticmethod
	def get_quiz_url(code):
		return Utils.SITE_URL + "/quiz/" + code

	@staticmethod
	def get_result_url(code):
		return Utils.SITE_URL + "/quiz/result/" + code
