import os
import string
import random
import math

from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.utils import translation

from what.models import Setting, Locale, Quiz


class Utils:
	"""utility functions for the app"""

	SITE_URL = settings.SITE_URL
	CODE_LENGTH = 8
	ELEMENTS_PER_PAGE = 10
	MAX_PAGES_DISPLAY = 5

	@staticmethod
	def date_handler(obj):
		return obj.isoformat() if hasattr(obj, 'isoformat') else obj

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

	@staticmethod
	def get_from_page(elements, page_num):
		"""returns [pages_count, rect_page_num, spliced_list_of_elements]"""
		elen = len(elements)
		if elen <= Utils.ELEMENTS_PER_PAGE:
			return [1, 1, elements]
		pages_count = math.ceil(elen / Utils.ELEMENTS_PER_PAGE)
		if page_num < 1:
			return [pages_count, 1, elements[0:Utils.ELEMENTS_PER_PAGE]]
		if page_num >= pages_count:
			return [pages_count, pages_count, elements[(pages_count-1)*Utils.ELEMENTS_PER_PAGE:]]
		return [pages_count, page_num, elements[(page_num-1)*Utils.ELEMENTS_PER_PAGE:page_num*Utils.ELEMENTS_PER_PAGE]]

	@staticmethod
	def get_displayed_pages(pages_count, page_num):
		"""returns a generator of page numbers to be displayed"""
		total_displayed = min(pages_count, Utils.MAX_PAGES_DISPLAY)
		half_displayed = total_displayed // 2
		if page_num < 3:
			pages = range(1, total_displayed + 1)
		elif page_num > pages_count - half_displayed:
			pages = range(max(1, pages_count - total_displayed + 1), pages_count + 1)
		else:
			if total_displayed % 2:
				pages = range(max(1, page_num - half_displayed), min(pages_count, page_num + half_displayed + 1))
			else:
				pages = range(max(1, page_num - half_displayed), min(pages_count, page_num + half_displayed))
		return pages

	@staticmethod
	def convert_datetime(d):
		return datetime.strftime(datetime.strptime(d, "%m/%d/%Y %I:%M %p"), "%Y-%m-%d %H:%M")

	@staticmethod
	def format_datetime(d):
		return datetime.strftime(d, "%m/%d/%Y %I:%M %p")

	@staticmethod
	def process_annals(annals):
		for a in annals:
			setattr(a, "num_duration", getattr(a, "annal_duration"))
			setattr(a, "annal_duration", Utils.format_duration(getattr(a, "annal_duration")))
			setattr(a, "created_on", Utils.format_datetime(getattr(a, "created_on")))
			if getattr(a, "auto_enable_date"):
				setattr(a, "auto_enable_date", Utils.format_datetime(getattr(a, "auto_enable_date")))
			if getattr(a, "auto_disable_date"):
				setattr(a, "auto_disable_date", Utils.format_datetime(getattr(a, "auto_disable_date")))
