import os
import string
import random

from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.utils import translation

from what.models import Setting, Locale, Quiz


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
	def get_app_url():
		return Utils.SITE_URL + "/quiz/"

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
		end += timedelta(0, 30) # 30 seconds mercy time
		return now >= end

	@staticmethod
	def date_is_in_past(d):
		now = datetime.now(timezone.utc)
		return now >= d

	@staticmethod
	def locale_exists(locale):
		root_path = os.path.dirname(os.path.realpath(__file__))
		if os.path.exists(root_path + "/locale/" + locale):
			return True

	@staticmethod
	def prepare_request(request):
		lang = "en"
		direction = "ltr"
		locales = []
		locales_dir = {}
		lang_settings = Setting.objects.first()
		for loc in Locale.objects.all():
			if Utils.locale_exists(loc.short_name):
				locales.append([loc.short_name, loc.full_name])
				locales_dir[loc.short_name] = loc.direction
		if request.method == "POST" and "select-locale" in request.POST:
			request.session['override_locale'] = request.POST['select-locale']
		if "override_locale" in request.session:
			if Utils.locale_exists(request.session['override_locale']):
				lang = request.session['override_locale']
				direction = locales_dir[lang]
		elif lang_settings:
			if lang_settings.locale.direction.lower() == "rtl":
				direction= "rtl"
			if Utils.locale_exists(lang_settings.locale.short_name):
				lang = lang_settings.locale.short_name
		translation.activate(lang)
		request.LANGUAGE_CODE = translation.get_language()
		request.session['direction'] = direction
		request.session['lang'] = lang
		request.session['site_name'] = lang_settings.site_name
		request.session['locales'] = locales
		request.session['site_url'] = Utils.get_app_url()
		return request
