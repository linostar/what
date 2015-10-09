from django.db import models
from django.contrib.auth.models import User


class Teacher(User):
	number_of_quizzes = models.IntegerField(default=0)


class Quiz(models.Model):
	teacher = models.ForeignKey(Teacher)
	quiz_name = models.CharField(max_length=128)
	created = models.DateTimeField()
	enabled = models.BooleanField(default=True)
	number_of_questions = models.IntegerField(default=0)


class Question(models.Model):
	quiz = models.ForeignKey(Quiz)
	question_text = models.CharField(max_length=512)
	# question_type: 0 for written answer, 1 for m-choice, 2 for m-choice m-answer
	question_type = models.IntegerField(default=1)


class Answer(models.Model):
	question = models.ForeignKey(Question)
	answer_text = models.CharField(max_length=512)
	answer_is_correct = models.BooleanField()


class Student(models.Model):
	student_name = models.CharField(max_length=64)
	number_of_quizzes = models.IntegerField(default=0)


class Result(models.Model):
	student = models.ForeignKey(Student)
	quiz = models.ForeignKey(Quiz)
	secret_code = models.CharField(max_length=16)
	score = models.IntegerField(default=0)
