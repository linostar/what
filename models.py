from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
	number_of_annals = models.IntegerField(default=0)
	user = models.OneToOneField(User)

	def __str__(self):
		return self.user.username


class Annal(models.Model):
	# An annal is the container of questions and their answers
	teacher = models.ForeignKey(Teacher)
	annal_name = models.CharField(max_length=128)
	created_on = models.DateTimeField(default=datetime.now)
	enabled = models.BooleanField(default=True)
	auto_enable = models.BooleanField(default=False)
	auto_enable_date = models.DateTimeField(null=True, blank=True)
	auto_disable = models.BooleanField(default=False)
	auto_disable_date = models.DateTimeField(null=True, blank=True)
	# Annal duration is in seconds
	annal_duration = models.IntegerField(default=300)
	number_of_questions = models.IntegerField(default=0)
	show_correct_answers_at_end = models.BooleanField(default=False)
	rules = models.TextField(null=True, blank=True)

	def __str__(self):
		return self.annal_name


class Question(models.Model):
	annal = models.ForeignKey(Annal)
	question_text = models.CharField(max_length=512)
	# question_type: 0 for written answer, 1 for m-choice, 2 for m-choice m-answer
	question_type = models.IntegerField(default=1)
	points_rewarded = models.IntegerField(default=1)

	def __str__(self):
		# use truncated question_text
		cut = 40
		if len(self.question_text) < cut:
			return self.question_text
		sep = self.question_text.rfind(" ", 0, cut)
		if sep == -1:
			return self.question_text[:cut]
		else:
			return self.question_text[:sep]


class Answer(models.Model):
	question = models.ForeignKey(Question)
	answer_text = models.CharField(max_length=512)
	answer_is_correct = models.BooleanField()

	def __str__(self):
		# use truncated answer_text
		cut = 40
		if len(self.answer_text) < cut:
			return self.answer_text
		sep = self.answer_text.rfind(" ", 0, cut)
		if sep == -1:
			return self.answer_text[:cut]
		else:
			return self.answer_text[:sep]


class Student(models.Model):
	student_name = models.CharField(max_length=64)
	number_of_quizzes = models.IntegerField(default=0)

	def __str__(self):
		return self.student_name


class Quiz(models.Model):
	student = models.ForeignKey(Student)
	annal = models.ForeignKey(Annal)
	quiz_code = models.CharField(max_length=16)
	score = models.IntegerField(default=0)
	max_score = models.IntegerField(default=0)
	number_of_questions = models.IntegerField(default=0)
	submitted = models.BooleanField(default=False)
	# time remaining in the clock when the student finishes (in seconds)
	finish_time = models.IntegerField(default=0)
	start_time = models.DateTimeField(blank=True, null=True)
	selected_questions = models.ManyToManyField(Question, blank=True)
	student_answers = models.ManyToManyField(Answer, blank=True)


class Locale(models.Model):
	short_name = models.CharField(max_length=8, default="en")
	full_name = models.CharField(max_length=32, default="English")
	direction = models.CharField(max_length=3, default="ltr")

	def __str__(self):
		return self.full_name


class Setting(models.Model):
	locale = models.ForeignKey(Locale)
	site_name = models.CharField(max_length=50, default="Interactive Tests")

	def __str__(self):
		return self.site_name

