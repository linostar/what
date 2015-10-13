from django import template

register = template.Library()

@register.filter
def index(list, index):
	return list[index]

@register.filter
def question(list, index):
	return list[index].question_text

@register.filter
def qid(list, index):
	return list[index].id
