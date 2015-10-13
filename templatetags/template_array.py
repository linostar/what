from django import template

register = template.Library()

@register.filter
def index(list, index):
	return list[index]

@register.filter
def question(list, index):
	return list[index].question_text

@register.filter
def answer(list, index):
	return list[index].answer_text
