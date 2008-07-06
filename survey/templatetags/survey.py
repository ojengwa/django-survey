from django import template

register = template.Library()

@register.filter
def has_answered(request, survey):
    if not hasattr(request, 'session'): return False
    return survey.has_answers_from(request.session.session_key)

@register.filter
def can_view_answers(user, survey):
    return survey.answers_viewable_by(user)

@register.filter_function
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)

@register.filter
def answer_count(question, survey):
    """ Counts the number of answers to a question in a survey."""
    return question.answers.filter(survey=survey).count()

@register.filter
def answers(question, survey):
    """ Returns the answers to a question in a survey."""
    return question.answers.filter(survey=survey)

@register.filter
def choice_count(answers, choice):
    """ Counts the number of the specified choice made to a question in a 
    survey. """
    return answers.filter(text=choice.text).count()