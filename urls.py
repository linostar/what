from django.conf.urls import patterns, url

from what import views


urlpatterns = patterns("",
	url(r"^$", views.index, name="index"),
	url(r"^login/$", views.signin, name="login"),
	url(r"^logout/$", views.signout, name="logout"),
	url(r"^students/$", views.cp_students, name="students"),
	url(r"^annals/$", views.cp_annals, name="annals"),
	url(r"^questions/$", views.cp_questions, name="questions"),
	url(r"^quizzes/$", views.cp_quizzes, name="quizzes"),
	url(r"^teachers/$", views.cp_teachers, name="teachers"),
	url(r"^settings/$", views.cp_settings, name="settings"),
	url(r"^students/(?P<id>\d+)/$", views.cp_students, name="student_edit"),
	url(r"^annals/(?P<id>\d+)/$", views.cp_annals, name="annal_edit"),
	url(r"^questions/(?P<id>\d+)/$", views.cp_questions, name="question_edit"),
	url(r"^quizzes/(?P<id>\d+)/$", views.cp_quizzes, name="quizz_edit"),
	url(r"^teachers/(?P<id>\d+)/$", views.cp_teachers, name="teacher_edit"),
	url(r"^settings/(?P<id>\d+)/$", views.cp_settings, name="setting_edit"),
	url(r"^(?P<quiz_code>[a-zA-Z]{8})/$", views.quiz, name="quiz"),
	url(r"^result/(?P<quiz_code>[a-zA-Z]{8})/$", views.result, name="result"),
	)
