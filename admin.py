from django.contrib import admin

from what.utils import Utils
from what.models import Teacher, Student, Quiz, Annal, Question, Answer

class AnnalAdmin(admin.ModelAdmin):
	list_display = ["annal_name", "teacher", "enabled", "number_of_questions",
	"created_on"]
	search_fields = ["annal_name"]
	actions = ["delete_selected"]

	def get_form(self, request, obj=None, **kwargs):
		self.exclude = ["created_on", "number_of_questions"]
		return super().get_form(request, obj, **kwargs)

	def save_model(self, request, obj, form, change):
		if not obj.id:
			obj.teacher.number_of_annals += 1
			obj.teacher.save()
		obj.save()

	def delete_model(self, request, obj):
		obj.teacher.number_of_annals -= 1
		obj.teacher.save()
		obj.delete()

	def delete_selected(self, request, queryset):
		for obj in queryset:
			obj.teacher.number_of_annals -= 1
			obj.teacher.save()
			obj.delete()


class QuestionAdmin(admin.ModelAdmin):
	list_display = ["get_question", "points_rewarded", "annal"]
	actions = ["delete_selected"]

	def get_question(self, obj):
		return obj.question_text

	def save_model(self, request, obj, form, change):
		if not obj.id:
			obj.annal.number_of_questions += 1
			obj.annal.save()
		obj.save()

	def delete_model(self, request, obj):
		obj.annal.number_of_questions -= 1
		obj.annal.save()
		obj.delete()

	def delete_selected(self, request, queryset):
		for obj in queryset:
			obj.annal.number_of_questions -= 1
			obj.annal.save()
			obj.delete()

	get_question.short_description = "Question"
	get_question.admin_order_field = "question_text"


class AnswerAdmin(admin.ModelAdmin):
	list_display = ["get_answer", "question", "get_annal", "answer_is_correct"]

	def get_answer(self, obj):
		return obj.answer_text

	def get_annal(self, obj):
		return obj.question.annal

	get_answer.short_description = "Answer"
	get_answer.admin_order_field = "answer_text"
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
	list_display = ["get_url", "get_student", "annal", "score",
	"max_score", "number_of_questions", "submitted", "start_time",
	"get_finish_time"]
	actions = ["delete_selected"]

	def get_student(self, obj):
		return obj.student.student_name

	def get_url(self, obj):
		return Utils.get_quiz_url(obj.quiz_code)

	def get_finish_time(self, obj):
		return Utils.format_duration(obj.annal.annal_duration - obj.finish_time)

	def get_form(self, request, obj=None, **kwargs):
		self.exclude = ["quiz_code", "score", "max_score", "finish_time"]
		return super().get_form(request, obj, **kwargs)

	def save_model(self, request, obj, form, change):
		if not obj.id:
			obj.quiz_code = Utils.generate_quiz_code()
			obj.student.number_of_quizzes += 1
			obj.student.save()
		obj.save()

	def delete_model(self, request, obj):
		obj.student.number_of_quizzes -= 1
		obj.student.save()
		obj.delete()

	def delete_selected(self, request, queryset):
		for obj in queryset:
			obj.student.number_of_quizzes -= 1
			obj.student.save()
			obj.delete()

	get_student.short_description = "Quiz for"
	get_student.admin_order_field = "student__student_name"
	get_url.short_description = "Quiz link"
	get_url.admin_order_field = "quiz_code"
	get_finish_time.short_description = "Finished in"
	get_finish_time.admin_order_field = "-finish_time"


admin.site.register(Annal, AnnalAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
