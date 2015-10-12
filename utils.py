import string
import random

class Utils:
	"""utility functions for the app"""

	CODE_LENGTH = 8

	@staticmethod
	def generate_quiz_code():
		quiz_code = ""
		random.seed()
		for i in range(Utils.CODE_LENGTH):
			quiz_code += random.choice(string.ascii_letters)
		return quiz_code
