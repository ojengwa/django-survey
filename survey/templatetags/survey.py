from django import template
import sys
import logging
import traceback
import pdb

from django.forms.forms import BoundField

register = template.Library()

log = logging.getLogger(__name__)

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
def repr( obj ):
    
    try:
        output = str(obj)
    except Exception, e:
        tb = traceback.format_exception(type(e), e, sys.exc_info()[2] )
        return "<br/>\n".join(tb)
    return output
    
