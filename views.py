from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user

from what.models import Teacher, Student, Quiz, Question, Answer, Annal

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
		quiz = Quiz.objects.get(quiz_code=quiz_code)
		if quiz:
			questions = Question.objects.filter(annal=quiz.annal)
			answers = []
			for q in questions:
				answers.append(Answer.objects.filter(question=q))
			return render(request, "what/quiz.html", {
				"quiz": quiz,
				"student": quiz.student,
				"questions": questions,
				"answer": answers,
				"message": "show_quiz",
				})
	except Quiz.DoesNotExist:
		return render(request, "what/quiz.html", {
			"quiz_code": quiz_code,
			"message": "invalid_code",
			})
	except Quiz.MultipleObjectsReturned:
		# shouldn't happen because quiz_code must be unique
		raise

def result(request, quiz_code):
	try:
		quiz = Quiz.objects.get(quiz_code=quiz_code)
		if quiz:
			return render(request, "what/result.html", {
				"quiz_code": quiz_code,
				"score": quiz.score,
				"max_score": quiz.max_score,
				"number_of_questions": quiz.number_of_questions,
				"student": quiz.student,
				"message": "show_result",
				})
	except Quiz.DoesNotExist:
		return render(request, "what/result.html", {
			"quiz_code": quiz_code,
			"message": "invalid_code",
			})
	except Quiz.MultipleObjectsReturned:
		# shouldn't happen because quiz_code must be unique
		raise
