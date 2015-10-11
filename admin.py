from django.contrib import admin

from what.models import Teacher, Student, Quiz, Annal, Question, Answer

class AnnalAdmin(admin.ModelAdmin):
	list_display = ["annal_name", "teacher", "enabled"]
	search_fields = ["annal_name"]


class QuestionAdmin(admin.ModelAdmin):
	list_display = ["question_text", "annal"]


class AnswerAdmin(admin.ModelAdmin):
	list_display = ["answer_text", "question", "get_annal"]

	def get_annal(self, obj):
		return obj.question.annal

	get_annal.short_description = "Annal"
	get_annal.admin_order_field = "question__annal"


class TeacherAdmin(admin.ModelAdmin):
	list_display = ["user"]


class QuizAdmin(admin.ModelAdmin):
	list_display = ["student", "annal", "score"]


admin.site.register(Annal, AnnalAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
