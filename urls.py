from django.conf.urls.defaults import patterns, url

from Interactive.what import views


urlpatterns = patterns("",
	url(r"^$", views.index, name="index"),
	url(r"^login/$", views.signin, name="login"),
	url(r"^logout/$", views.signout, name="logout"),
	url(r"^(?P<quiz_code>[a-zA-Z]{8})/$", views.quiz, name="quiz")
	)
