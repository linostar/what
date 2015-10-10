from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user

from Interactive.what.models import Teacher, Student, Quiz, Question, Answer, Result

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
					return render(request, "what/index.html",
						{"message": "login_success"})
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
	pass
