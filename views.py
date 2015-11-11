import json
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout, get_user
from django.utils.translation import ugettext as _

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
						"redirect_url": Utils.get_app_url() + "?message=login_success",
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
	return render(request, "what/logout.html", {"message": "logout_success"})

@check_login
def cp_students(request, eid=None):
	if eid:
		student = get_object_or_404(Student, id=eid)
		return render(request, "what/cp_students.html", {
			"student": student,
			})
	else:
		message = ""
		if request.method == "POST":
			if "changelist-action" in request.POST and request.POST['changelist-action'] == "delete":
				student_ids = []
				for element in request.POST:
					if element.startswith("sel-student-") and request.POST[element]:
						try:
							student_ids.append(int(element[12:]))
						except:
							continue
				Student.objects.filter(id__in=student_ids).delete()
				message = "{} student(s) deleted.".format(len(student_ids))
		students = Student.objects.all().order_by("student_name")
		return render(request, "what/cp_students.html", {
			"message": message,
			"students": students,
			})

@check_login
def cp_student_quizzes(request, eid, qindex=0):
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
def cp_annals(request, eid=None):
	if eid:
		annal = get_object_or_404(Annal, id=eid)
		return render(request, "what/cp_annals.html", {
			"annal": annal,
			})
	else:
		annals = Annal.objects.all().order_by("annal_name")
		return render(request, "what/cp_annals.html", {
			"annals": annals,
			})

@check_login
def cp_questions(request, eid=None):
	return render(request, "what/cp_questions.html", {})

@check_login
def cp_quizzes(request, eid=None):
	return render(request, "what/cp_quizzes.html", {})

@check_login
def cp_teachers(request, eid=None):
	return render(request, "what/cp_teachers.html", {})

@check_login
def cp_settings(request, eid=None):
	return render(request, "what/cp_settings.html", {})

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
