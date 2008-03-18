from django import template

register = template.Library()

@register.filter
def has_answered(request, survey):
    if not hasattr(request, 'session'): return False
    return survey.has_answers_from(request.session.session_key)

@register.filter
def can_view_answers(user, survey):
    return survey.answers_viewable_by(user)
