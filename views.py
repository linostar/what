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
