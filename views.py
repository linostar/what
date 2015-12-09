import json
import html
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout, get_user
from django.utils.translation import ugettext as _
from django.db import IntegrityError
from django.utils.safestring import mark_safe

from what.models import Teacher, Student, Quiz, Question, Answer, Annal, Setting
from what.utils import Utils


def prep_request(func):
	def func_wrapper(*args, **kwargs):
		request = Utils.prepare_request(args[0])
		if len(args) > 1:
			(*args,) = (request,) + args[1:]
		else:
			(*args,) = (request,)
		return func(*args, **kwargs)
	return func_wrapper

def check_login(func):
	def func_wrapper(*args, **kwargs):
		request = Utils.prepare_request(args[0])
		if not "userid" in request.session:
			return redirect("login")
		if len(args) > 1:
			(*args,) = (request,) + args[1:]
		else:
			(*args,) = (request,)
		return func(*args, **kwargs)
	return func_wrapper

@prep_request
def handler404(request):
	response = render(request, "what/404.html")
	response.status_code = 404
	return response

@prep_request
def handler500(request):
	response = render(request, "what/500.html")
	response.status_code = 500
	return response

@check_login
def index(request):
		return render(request, "what/index.html")

@prep_request
def signin(request):
	try:
		if request.method == "POST" and "form-username" in request.POST:
			if request.POST['form-username'] and request.POST['form-password']:
				user = authenticate(username=request.POST['form-username'],
					password=request.POST['form-password'])
				if user and user.is_active:
					# account exists and is enabled
					request.session['username'] = user.username
					request.session['userid'] = user.id
					return render(request, "what/redirect.html", {
						"redirect_url": Utils.get_app_url(),
						"message": "login_success",
						})
				elif user:
					# account exists but is disabled
					return render(request, "what/login.html",
						{"message": "account_disabled"})
				else:
					# username or password incorrect
					return render(request, "what/login.html",
						{"message": "login_error"})
			else:
				# username and/or password missing
				return render(request, "what/login.html", {
					"message": "login_missing",
					})
		else:
			# show the login form
			return render(request, "what/login.html", {
				"message": "form_login",
				})
	except KeyError:
		return render(request, "what/login.html", {"message": "login_missing"})

@prep_request
def signout(request):
	logout(request)
	if "username" in request.session:
		del request.session['username']
	if "userid" in request.session:
		del request.session['userid']
	return render(request, "what/redirect.html", {
		"redirect_url": Utils.get_app_url(),
		"message": "logout_success",
		})

@check_login
def cp_students(request):
	alert_status = ""
	message = ""
	if request.method == "GET":
		# search student
		if "q" in request.GET and request.GET['q']:
			students = Student.objects.filter(student_name__icontains=request.GET['q'])
			if students:
				message = _("<strong>{} students</strong> found matching your search.".format(len(students)))
				alert_status = "alert-info"
			else:
				message = _("<strong>No students</strong> found matching your search.")
				alert_status = "alert-warning"
			try:
				page_num = int(request.GET['page'])
			except:
				page_num = 1
			[pages_count, page_num, students] = Utils.get_from_page(students, page_num)
			return render(request, "what/cp_students.html", {
				"not_index_page": True,
				"message": mark_safe(message),
				"alert_status": alert_status,
				"page_num": page_num,
				"previous_page": max(1, page_num - 1),
				"next_page": min(pages_count, page_num + 1),
				"displayed_pages": Utils.get_displayed_pages(pages_count, page_num),
				"search_term": request.GET['q'],
				"students": students,
				})
	elif request.method == "POST":
		# delete student
		if "changelist-action" in request.POST and request.POST['changelist-action'] == "delete":
			student_ids = []
			for element in request.POST:
				if element.startswith("sel-student-") and request.POST[element]:
					try:
						student_ids.append(int(element[12:]))
					except:
						continue
			try:
				Student.objects.filter(id__in=student_ids).delete()
				message = _("{} student(s) deleted.".format(len(student_ids)))
				alert_status = "alert-success"
			except:
				message = _("Due to an unknown error, the selected student(s) could not be deleted.")
				alert_status = "alert-danger"
		elif "student-action" in request.POST:
			# add student
			if request.POST['student-action'] == "add":
				try:
					new_student = Student(student_name=(request.POST['student_name']).strip())
					new_student.save()
					message = _("Student <strong>{}</strong> successfully added.".format(request.POST['student_name']))
					alert_status = "alert-success"
				except IntegrityError:
					message = _("Student already exists in database.")
					alert_status = "alert-danger"
				except:
					message = _("Due to an unknown error, the student could not be created.")
					alert_status = "alert-danger"
			# edit student
			elif request.POST['student-action'] == "edit":
				try:
					# no need to check for teacher access on changing students
					edited_student = Student(id=request.POST['student_id'])
					edited_student.student_name = request.POST['student_name']
					edited_student.save()
					message = _("Student successfully saved.")
					alert_status = "alert-success"
				except IntegrityError:
					message = _("Student with same name already exists in database.")
					alert_status = "alert-danger"
				except:
					message = _("Due to an unknown error, the student could not be saved to database.")
					alert_status = "alert-danger"
	students = Student.objects.all().order_by("student_name")
	try:
		page_num = int(request.GET['page'])
	except:
		page_num = 1
	[pages_count, page_num, students] = Utils.get_from_page(students, page_num)
	return render(request, "what/cp_students.html", {
		"not_index_page": True,
		"alert_status": alert_status,
		"message": mark_safe(message),
		"page_num": page_num,
		"previous_page": max(1, page_num - 1),
		"next_page": min(pages_count, page_num + 1),
		"displayed_pages": Utils.get_displayed_pages(pages_count, page_num),
		"students": students,
		})

@check_login
def cp_student_quizzes(request, eid, qindex=0):
	"""for AJAX calls"""
	quizzes = Quiz.objects.filter(student__id=eid).values("annal", "submitted",
		"number_of_questions", "start_time", "finish_time", "score", "max_score")
	try:
		q = quizzes[int(qindex)]
		if q['max_score']:
			q['score'] = "{}/100".format(round(100 * q['score'] / q['max_score']))
		else:
			q['score'] = "0/100"
		annal = Annal.objects.filter(id=q['annal'])
		if annal:
			q['annal'] = annal[0].annal_name
		else:
			q['annal'] = "--"
		if not q['start_time']:
			q['start_time'] = "--"
		else:
			q['start_time'] = q['start_time'].strftime("%d/%m/%Y %H:%M")
		q['submitted'] = _("Yes") if q['submitted'] else _("No")
		q['finish_time'] = Utils.format_duration(annal[0].annal_duration - q['finish_time'])
		q['student_id'] = eid
		return HttpResponse(json.dumps(q), content_type="application/json")
	except:
		return HttpResponse(json.dumps({}), content_type="application/json")

@check_login
def cp_annals(request):
	alert_status = ""
	message = ""
	if request.method == "GET":
		# search annal
		if "q" in request.GET and request.GET['q']:
			annals = Annal.objects.filter(annal_name__icontains=request.GET['q'])
			if annals:
				message = _("<strong>{} annals</strong> found matching your search.".format(len(annals)))
				alert_status = "alert-info"
			else:
				message = _("<strong>No annals</strong> found matching your search.")
				alert_status = "alert-warning"
			try:
				page_num = int(request.GET['page'])
			except:
				page_num = 1
			[pages_count, page_num, annals] = Utils.get_from_page(annals, page_num)
			Utils.process_annals(annals)
			return render(request, "what/cp_annals.html", {
				"not_index_page": True,
				"message": mark_safe(message),
				"alert_status": alert_status,
				"page_num": page_num,
				"previous_page": max(1, page_num - 1),
				"next_page": min(pages_count, page_num + 1),
				"displayed_pages": Utils.get_displayed_pages(pages_count, page_num),
				"search_term": request.GET['q'],
				"annals": annals,
				})
	if request.method == "POST":
		# delete annal
		if "changelist-action" in request.POST and request.POST['changelist-action'] == "delete":
			annal_ids = []
			for element in request.POST:
				if element.startswith("sel-annal-") and request.POST[element]:
					try:
						annal_ids.append(int(element[10:]))
					except:
						continue
			try:
				Annal.objects.filter(id__in=annal_ids).delete()
				message = _("{} annal(s) deleted.".format(len(annal_ids)))
				alert_status = "alert-success"
			except:
				message = _("Due to an unknown error, the selected annal(s) could not be deleted.")
				alert_status = "alert-danger"
		elif "annal-action" in request.POST:
			# add annal
			if request.POST['annal-action'] == "add":
				# TODO: check for teacher access
				try:
					this_teacher = Teacher.objects.get(user__username=request.session['username'])
					if "annal_enabled" in request.POST and request.POST['annal_enabled'] == 'on':
						enabled = True
					else:
						enabled = False
					# TODO: use html.escape for 'rules' and allow markdown or rst instead of html
					rules = request.POST['annal_rules']
					# TODO: convert from different units of times to seconds for 'duration'
					duration = request.POST['annal_duration']
					if "annal_reveal_answers" in request.POST and request.POST['annal_reveal_answers'] == 'on':
						show_answers = True
					else:
						show_answers = False
					if "annal_starts_on_hidden" in request.POST and request.POST['annal_starts_on_hidden']:
						auto_enable = True
						auto_enable_date = Utils.convert_datetime(request.POST['annal_starts_on_text'])
					else:
						auto_enable = False
						auto_enable_date = None
					if "annal_ends_on_hidden" in request.POST and request.POST['annal_ends_on_hidden']:
						auto_disable = True
						auto_disable_date = Utils.convert_datetime(request.POST['annal_ends_on_text'])
					else:
						auto_disable = False
						auto_disable_date = None
					new_annal = Annal(annal_name=(request.POST['annal_name']).strip(), teacher=this_teacher,
						enabled=enabled, rules=rules, annal_duration=duration, show_correct_answers_at_end=show_answers,
						auto_enable=auto_enable, auto_enable_date=auto_enable_date,
						auto_disable=auto_disable, auto_disable_date=auto_disable_date)
					new_annal.save()
					message = _("Annal <strong>{}</strong> successfully added.".format(request.POST['annal_name']))
					alert_status = "alert-success"
				except:
					message = _("Due to an unknown error, the annal could not be created.")
					alert_status = "alert-danger"
			# edit annal
			elif request.POST['annal-action'] == "edit":
				try:
					# TODO: check for teacher access
					this_teacher = Teacher.objects.get(user__username=request.session['username'])
					edited_annal = Annal(id=request.POST['annal_id'])
					edited_annal.annal_name = request.POST['annal_name']
					if "annal_enabled" in request.POST:
						edited_annal.enabled = request.POST['annal_enabled']
					else:
						edited_annal.enabled = False
					if "annal_reveal_answers" in request.POST:
						edited_annal.show_correct_answers_at_end = request.POST['annal_reveal_answers']
					else:
						edited_annal.show_correct_answers_at_end = False
					edited_annal.annal_duration = int(request.POST['annal_duration'])
					edited_annal.teacher = this_teacher
					edited_annal.save()
					message = _("Annal successfully saved.")
					alert_status = "alert-success"
				except:
					message = _("Due to an unknown error, the annal could not be saved to database.")
					alert_status = "alert-danger"
	annals = Annal.objects.all().order_by("annal_name")
	try:
		page_num = int(request.GET['page'])
	except:
		page_num = 1
	[pages_count, page_num, annals] = Utils.get_from_page(annals, page_num)
	Utils.process_annals(annals)
	return render(request, "what/cp_annals.html", {
		"not_index_page": True,
		"alert_status": alert_status,
		"message": mark_safe(message),
		"page_num": page_num,
		"previous_page": max(1, page_num - 1),
		"next_page": min(pages_count, page_num + 1),
		"displayed_pages": Utils.get_displayed_pages(pages_count, page_num),
		"annals": annals,
		})

@check_login
def cp_questions(request, eid=None):
	return render(request, "what/cp_questions.html", {
		"not_index_page": True,
		})

@check_login
def cp_quizzes(request, eid=None):
	return render(request, "what/cp_quizzes.html", {
		"not_index_page": True,
		})

@check_login
def cp_teachers(request, eid=None):
	return render(request, "what/cp_teachers.html", {
		"not_index_page": True,
		})

@check_login
def cp_settings(request, eid=None):
	return render(request, "what/cp_settings.html", {
		"not_index_page": True,
		})

@prep_request
def quiz(request, quiz_code):
	try:
		if request.method == "POST" and "remaining-time-heidden" in request.POST:
			# quiz answered are POSTed
			quiz = get_object_or_404(Quiz, quiz_code=quiz_code)
			quiz.submitted = True
			if quiz.start_time and Utils.quiz_expired(quiz):
				# quiz has already expired
				quiz.save()
				return render(request, "what/quiz.html", {
					"student": quiz.student,
					"rules": quiz.annal.rules,
					"result_url": Utils.get_result_url(quiz_code),
					"user_message": _("Hello,"),
					"message": "quiz_expired",
					})
			elif quiz.start_time:
				# calculate the score
				score = 0
				max_score = 0
				student_answers = []
				for key in request.POST.keys():
					if key.startswith("chosen-answer-q"):
						try:
							question = get_object_or_404(Question, id=int(key[15:]))
							max_score += question.points_rewarded
							answer = get_object_or_404(Answer, id=int(request.POST[key]))
							student_answers.append(answer)
							if answer.answer_is_correct:
								score += question.points_rewarded
						except ValueError:
							# non-int instead of question/answer id
							continue
				quiz.student_answers = student_answers
				quiz.score = score
				quiz.max_score = max_score
				try:
					quiz.finish_time = max(int(request.POST.get("remaining-time-hidden", 0)), 0)
				except:
					quiz.finish_time = 0
				quiz.save()
				return redirect("result", quiz_code=quiz_code)
			else:
				# dude, how did you get here?!
				raise Http404
		else:
			quiz = get_object_or_404(Quiz, quiz_code=quiz_code)
			is_enabled = quiz.annal.enabled
			if quiz.annal.auto_enable and quiz.annal.auto_enable_date:
				if Utils.date_is_in_past(quiz.annal.auto_enable_date):
					is_enabled = True
			if quiz.annal.auto_disable and quiz.annal.auto_disable_date:
				if Utils.date_is_in_past(quiz.annal.auto_disable_date):
					is_enabled = False
			quiz.annal.enabled = is_enabled
			quiz.annal.save()
			quiz.save()
			if not is_enabled:
				# Quiz is disabled
				return render(request, "what/quiz.html", {
					"student": quiz.student,
					"rules": quiz.annal.rules,
					"result_url": Utils.get_result_url(quiz_code),
					"user_message": _("Hello,"),
					"message": "quiz_disabled",
					})
			if quiz.submitted:
				# User cannot take the quiz twice
				return render(request, "what/quiz.html", {
					"student": quiz.student,
					"rules": quiz.annal.rules,
					"result_url": Utils.get_result_url(quiz_code),
					"user_message": _("Hello,"),
					"message": "quiz_submitted",
					})
			else:
				if quiz.start_time and Utils.quiz_expired(quiz):
					# quiz time has already expired
					quiz.submitted = True
					quiz.save()
					return render(request, "what/quiz.html", {
						"student": quiz.student,
						"rules": quiz.annal.rules,
						"result_url": Utils.get_result_url(quiz_code),
						"user_message": _("Hello,"),
						"message": "quiz_expired",
						})
				# show the questions and start the quiz
				quiz.start_time = datetime.now()
				if quiz.selected_questions.all():
					questions = quiz.selected_questions.all()
				else:
					questions = Question.objects.filter(annal=quiz.annal).order_by(
						"?")[:quiz.number_of_questions]
					quiz.selected_questions.add(*questions)
					quiz.save()
				answers = []
				for q in questions:
					answers.append(Answer.objects.filter(question=q).order_by("?"))
				return render(request, "what/quiz.html", {
					"quiz": quiz,
					"rules": quiz.annal.rules,
					"teacher": quiz.annal.teacher.user,
					"duration": Utils.format_duration(quiz.annal.annal_duration),
					"student": quiz.student,
					"indexes": range(len(questions)),
					"questions": list(questions),
					"answers": answers,
					"user_message": _("Good luck,"),
					"message": "show_quiz",
					})
	except Quiz.MultipleObjectsReturned:
		# shouldn't happen because quiz_code must be unique
		raise

@prep_request
def result(request, quiz_code):
	try:
		quiz = get_object_or_404(Quiz, quiz_code=quiz_code)
		if not quiz.submitted:
			# quiz is not submitted yet
			return render(request, "what/result.html", {
					"student": quiz.student,
					"quiz_url": Utils.get_quiz_url(quiz_code),
					"user_message": _("Hello,"),
					"message": "quiz_not_submitted"
					})
		else:
			# display results
			try:
				score = round(quiz.score * 100 / quiz.max_score)
			except ZeroDivisionError:
				score = 0
			return render(request, "what/result.html", {
				"quiz_code": quiz_code,
				"quiz_name": quiz.annal.annal_name,
				"score": score,
				"start_time": quiz.start_time,
				"finish_time": Utils.format_duration(
					quiz.annal.annal_duration - quiz.finish_time),
				"number_of_questions": quiz.number_of_questions,
				"student": quiz.student,
				"user_message": _("Hello,"),
				"message": "show_result",
				})
	except Quiz.MultipleObjectsReturned:
		# shouldn't happen because quiz_code must be unique
		raise
