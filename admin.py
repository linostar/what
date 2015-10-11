from django.contrib import admin

from what.models import Teacher, Student, Quiz, Annal, Question, Answer

class AnnalAdmin(admin.ModelAdmin):
	list_display = ["annal_name", "teacher", "enabled", "number_of_questions",
	"created_on"]
	search_fields = ["annal_name"]

	def get_form(self, request, obj=None, **kwargs):
		self.exclude = ["created_on", "number_of_questions"]
		return super().get_form(request, obj, **kwargs)


class QuestionAdmin(admin.ModelAdmin):
	list_display = ["question_text", "annal"]


class AnswerAdmin(admin.ModelAdmin):
	list_display = ["answer_text", "question", "get_annal"]

	def get_annal(self, obj):
		return obj.question.annal

	get_annal.short_description = "Annal"
	get_annal.admin_order_field = "question__annal"


class TeacherAdmin(admin.ModelAdmin):
	list_display = ["get_user", "number_of_annals"]

	def get_user(self, obj):
		return obj.user.username

	def get_form(self, request, obj=None, **kwargs):
		self.exclude = ["number_of_annals"]
		return super().get_form(request, obj, **kwargs)

	get_user.short_description = "Teacher"
	get_user.admin_order_field = "user__username"


class StudentAdmin(admin.ModelAdmin):
	list_display = ["student_name", "number_of_quizzes"]

	def get_form(self, request, obj=None, **kwargs):
		self.exclude = ["number_of_quizzes"]
		return super().get_form(request, obj, **kwargs)


class QuizAdmin(admin.ModelAdmin):
	list_display = ["get_student", "annal", "score"]

	def get_student(self, obj):
		return obj.student.student_name

	def get_form(self, request, obj=None, **kwargs):
		self.exclude = ["quiz_code"]
		return super().get_form(request, obj, **kwargs)

	get_student.short_description = "Quiz for"
	get_student.admin_order_field = "student__student_name"


admin.site.register(Annal, AnnalAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
