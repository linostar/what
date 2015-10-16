import os
import string
import random

from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.utils import translation

from what.models import Setting, Quiz


class Utils:
	"""utility functions for the app"""

	SITE_URL = settings.SITE_URL
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

	@staticmethod
	def format_duration(duration):
		hours = duration // 3600
		minutes = (duration - hours * 3600) // 60
		seconds = duration % 60
		return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

	@staticmethod
	def quiz_expired(quiz):
		now = datetime.now(timezone.utc)
		end = quiz.start_time + timedelta(0, quiz.annal.annal_duration)
		end += timedelta(0, 10) # 10 seconds mercy time
		return now >= end

	@staticmethod
	def date_is_in_past(d):
		now = datetime.now(timezone.utc)
		return now >= d

	@staticmethod
	def prepare_request(request):
		lang = "en"
		direction = "ltr"
		lang_settings = Setting.objects.first()
		if lang_settings:
			if lang_settings.direction.lower() == "rtl":
				direction= "rtl"
			if os.path.exists("locale/" + lang_settings.language):
				lang = lang_settings.language
		translation.activate(lang)
		request.LANGUAGE_CODE = translation.get_language()
		request.session['direction'] = direction
		request.session['lang'] = lang
		request.session['site_name'] = lang_settings.site_name
		return request
