from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list_detail import object_list
from models import Survey
from views import survey_detail, answers_detail, answers_list

urlpatterns = patterns('',
    url(r'^/?$',                    object_list,
        { 'queryset': Survey.objects.filter(visible=True), 'allow_empty': True,
          'extra_context': {'title': _('Surveys')}}, name='survey-list'),

    url(r'^(?P<slug>[-\w]+)/$',     survey_detail,   name='survey'),

    url(r'^(?P<slug>[-\w]+)/answers/$',
                                    answers_list,    name='survey-results'),

    url(r'^(?P<slug>[-\w]+)/answers/(?P<key>[a-fA-F0-9]{10,40})/$',
                                    answers_detail,  name='survey-submission'),
)
