from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user

from what.models import Teacher, Student, Quiz, Question, Answer, Annal
from what.utils import Utils


def handler404(request):
	response = render(request, "what/404.html")
	response.status_code = 404
	return response

def handler500(request):
	response = render(request, "what/500.html")
	response.status_code = 500
	return response

def index(request):
	if not request.user.is_authenticated():
		return redirect("login")
	else:
		return render(request, "what/index.html", {
			'userid': get_user(request).id,
			'username': get_user(request).username,
			})

def signin(request):
	try:
		if request.method == "POST":
			if request.POST['username'] and request.POST['password']:
				user = authenticate(username=request.POST['username'],
					password=request.POST['password'])
				if user and user.is_active:
					# account exists and is enabled
					return render(request, "what/index.html", {
						"message": "login_success",
						"userid": get_user(request).id,
						"username": get_user(request).username,
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
			# show the login form
			return render(request, "what/login.html")
	except KeyError:
		return render(request, "what/login.html", {"message": "login_missing"})

def signout(request):
	logout(request)
	return render(request, "what/logout.html", {"message": "logout_success"})

def quiz(request, quiz_code):
	try:
		if request.method == "POST":
			# quiz answered are POSTed
			quiz = get_object_or_404(Quiz, quiz_code=quiz_code)
			quiz.submitted = True
			if quiz.start_time and Utils.quiz_expired(quiz):
				# quiz has already expired
				pass
			else:
				pass
			quiz.save()
			return redirect("result", quiz_code=quiz_code)
		else:
			quiz = get_object_or_404(Quiz, quiz_code=quiz_code)
			if quiz.submitted:
				# User cannot take the quiz twice
				return render(request, "what/quiz.html", {
					"student": quiz.student,
					"result_url": Utils.get_result_url(quiz_code),
					"user_message": "Hello,",
					"message": "quiz_submitted",
					})
			else:
				if quiz.start_time and Utils.quiz_expired(quiz):
					# quiz time has already expired
					quiz.submitted = True
					quiz.save()
					return render(request, "what/quiz.html", {
						"student": quiz.student,
						"result_url": Utils.get_result_url(quiz_code),
						"user_message": "Hello,",
						"message": "quiz_expired",
						})
				# show the questions and start the quiz
				quiz.start_time = datetime.now()
				quiz.save()
				questions = Question.objects.filter(annal=quiz.annal).order_by(
					"?")[:quiz.number_of_questions]
				answers = []
				for q in questions:
					answers.append(Answer.objects.filter(question=q).order_by("?"))
				return render(request, "what/quiz.html", {
					"quiz": quiz,
					"teacher": quiz.annal.teacher.user,
					"duration": Utils.format_duration(quiz.annal.annal_duration),
					"student": quiz.student,
					"indexes": range(len(questions)),
					"questions": list(questions),
					"answers": answers,
					"user_message": "Good luck,",
					"message": "show_quiz",
					})
	except Quiz.MultipleObjectsReturned:
		# shouldn't happen because quiz_code must be unique
		raise

def result(request, quiz_code):
	try:
		quiz = get_object_or_404(Quiz, quiz_code=quiz_code)
		if not quiz.submitted:
			return render(request, "what/result.html", {
					"student": quiz.student,
					"message": "quiz_not_submitted"
					})
		else:
			return render(request, "what/result.html", {
				"quiz_code": quiz_code,
				"score": quiz.score,
				"max_score": quiz.max_score,
				"number_of_questions": quiz.number_of_questions,
				"student": quiz.student,
				"message": "show_result",
				})
	except Quiz.MultipleObjectsReturned:
		# shouldn't happen because quiz_code must be unique
		raise
