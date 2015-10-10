from django.conf.urls.defaults import patterns, url

from Interactive.what import views


urlpatterns = patterns("",
	url(r"^quiz/$", views.index, name="index"),
	url(r"^quiz/login/$", views.signin, name="login"),
	url(r"^quiz/logout/$", views.signout, name="logout"),
	url(r"^quiz/(?P<quiz_code>[a-zA-Z]{8})/$", views.quiz, name="quiz")
	)
