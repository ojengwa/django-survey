from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.http import HttpResponseNotFound
from django.conf import settings
from django.core.cache import cache
from django.views.generic.list_detail import object_list
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from forms import forms_for_survey
from models import Survey, Answer
from datetime import datetime

def _survey_redirect(request, survey):
    """
    Conditionally redirect to the appropriate page;
    if there is a "next" value in the GET URL parameter,
    go to the URL specified under Next.
    
    If there is no "next" URL specified, then go to
    the survey results page...but only if it is viewable
    by the user.
    
    Otherwise, only direct the user to a page showing
    their own survey answers...assuming they have answered
    any questions.
    
    If all else fails, go to the Thank You page.
    """
    if ('next' in request.REQUEST and
        request.REQUEST['next'].startswith('http:') and
        request.REQUEST['next'] != request.path):
        return HttpResponseRedirect(request.REQUEST['next'])
    if survey.answers_viewable_by(request.user):
        return HttpResponseRedirect(reverse('survey-results', None, (),
                                                {'slug': survey.slug}))
    
    # For this survey, have they answered any questions?
    if (hasattr(request, 'session') and Answer.objects.filter(
            session_key=request.session.session_key.lower(),
            question__survey__visible=True,
            question__survey__slug=survey.slug).count()):
        return HttpResponseRedirect(
            reverse('survey-submission', None, (),
                    {'slug': survey.slug,
                     'key': request.session.session_key.lower()}))
                     
    # go to thank you page
    return render_to_response('survey/thankyou.html',
                              {'survey': survey, 'title': _('Thank You')},
                              context_instance=RequestContext(request))

def survey_detail(request, slug):
    """
    
    """
    survey = get_object_or_404(Survey.objects.filter(visible=True), slug=slug)
    if survey.closed:
        if survey.answers_viewable_by(request.user):
            return HttpResponseRedirect(reverse('survey-results', None, (),
                                                {'slug': slug}))
        raise Http404 #(_('Page not found.')) # unicode + exceptions = bad
    # if user has a session and have answered some questions,
    # go ahead and redirect to the answers, or a thank you 
    if (hasattr(request, 'session') and
        survey.has_answers_from(request.session.session_key)):
        return _survey_redirect(request, survey)
    if request.POST and not hasattr(request, 'session'):
        return HttpResponse(unicode(_('Cookies must be enabled.')), status=403)
    if hasattr(request, 'session'):
        skey = 'survey_%d' % survey.id
        request.session[skey] = (request.session.get(skey, False) or
                                 request.method == 'POST')
        request.session.modified = True ## enforce the cookie save.
    survey.forms = forms_for_survey(survey, request)
    if (request.POST and all(form.is_valid() for form in survey.forms)):
        for form in survey.forms:
            form.save()
        return _survey_redirect(request, survey)

    return render_to_response('survey/survey_detail.html',
                              {'survey': survey, 'title': survey.title},
                              context_instance=RequestContext(request))

def answers_list(request, slug):
    """
    Shows a page showing survey results for an entire survey.
    """
    survey = get_object_or_404(Survey.objects.filter(visible=True), slug=slug)
    # if the user lacks permissions, show an "Insufficient Permissions page"
    if not survey.answers_viewable_by(request.user):
        if (hasattr(request, 'session') and
            survey.has_answers_from(request.session.session_key)):
            return HttpResponseRedirect(
                reverse('survey-submission', None, (),
                        {'slug': survey.slug,
                         'key': request.session.session_key.lower()}))
        return HttpResponse(unicode(_('Insufficient Privileges.')), status=403)
    return render_to_response('survey/answers_list.html',
        { 'survey': survey,
          'view_submissions': request.user.has_perm('survey.view_submissions'),
          'title': survey.title + u' - ' + unicode(_('Results'))},
        context_instance=RequestContext(request))

def answers_detail(request, slug, key):
    """
    Shows a page with survey results for a single person.
    
    If the user lacks permissions, show an "Insufficient Permissions page".
    """
    answers = Answer.objects.filter(session_key=key.lower(),
        question__survey__visible=True, question__survey__slug=slug)
    if not answers.count(): raise Http404
    survey = answers[0].question.survey

    mysubmission = (hasattr(request, 'session') and
         request.session.session_key.lower() == key.lower())

    if (not mysubmission and
        (not request.user.has_perm('survey.view_submissions') or
         not survey.answers_viewable_by(request.user))):
        return HttpResponse(unicode(_('Insufficient Privileges.')), status=403)
    return render_to_response('survey/answers_detail.html',
        {'survey': survey, 'submission': answers,
         'title': survey.title + u' - ' + unicode(_('Submission'))},
        context_instance=RequestContext(request))
