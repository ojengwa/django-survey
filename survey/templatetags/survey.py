from django import template
from django.conf import settings
from django.core.cache import cache
from cPickle import loads, dumps, HIGHEST_PROTOCOL
import datetime
import feedparser
import re
import time

register = template.Library()


@register.filter
def has_answered(request, survey):
    if not hasattr(request, 'session'): return False
    return survey.has_answers_from(request.session.session_key)

@register.filter
def can_view_answers(user, survey):
    return survey.answers_viewable_by(user)




