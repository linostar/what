from django.db import models
from django.contrib.auth.models import User


class Teacher(User):
	number_of_quizzes = models.IntegerField(default=0)

	def __str__(self):
		return self.username


class Quiz(models.Model):
	teacher = models.ForeignKey(Teacher)
	quiz_name = models.CharField(max_length=128)
	created = models.DateTimeField()
	enabled = models.BooleanField(default=True)
	number_of_questions = models.IntegerField(default=0)

	def __str__(self):
		return self.quiz_name


class Question(models.Model):
	quiz = models.ForeignKey(Quiz)
	question_text = models.CharField(max_length=512)
	# question_type: 0 for written answer, 1 for m-choice, 2 for m-choice m-answer
	question_type = models.IntegerField(default=1)

	def __str__(self):
		# use truncated question_text
		cut = 30
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
		cut = 30
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


class Result(models.Model):
	student = models.ForeignKey(Student)
	quiz = models.ForeignKey(Quiz)
	secret_code = models.CharField(max_length=16)
	score = models.IntegerField(default=0)

	def __str__(self):
		return student + " :: " + quiz + " :: " + str(score)
