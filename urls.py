from django.conf.urls import patterns, url, handler404, handler500

from what import views


urlpatterns = patterns("",
	url(r"^$", views.index, name="index"),
	url(r"^login/$", views.signin, name="login"),
	url(r"^logout/$", views.signout, name="logout"),
	url(r"^(?P<quiz_code>[a-zA-Z]{8})/$", views.quiz, name="quiz"),
	url(r"^result/(?P<quiz_code>[a-zA-Z]{8})/$", views.result, name="result"),
	)

handler404 = "what.views.handler404"
handler500 = "what.views.handler500"
