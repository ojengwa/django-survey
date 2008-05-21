from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.http import HttpResponseNotFound
from django.template import loader, RequestContext
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list_detail import object_list
from django.views.generic.create_update import delete_object

from forms import forms_for_survey, SurveyForm, QuestionForm, ChoiceForm
from models import Survey, Answer, Question, Choice
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
            reverse('answers-detail', None, (),
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
    # if user has a session and have answered some questions
    # and the survey does not accept multiple answers,
    # go ahead and redirect to the answers, or a thank you
    if (hasattr(request, 'session') and
        survey.has_answers_from(request.session.session_key) and
        not survey.allows_multiple_interviews):
        return _survey_redirect(request, survey)
    # if the survey is restricted to authentified user redirect
    # annonymous user to the login page
    if survey.restricted and str(request.user) == "AnonymousUser":
        return HttpResponseRedirect(reverse("auth_login")+"?next=%s" % request.path)
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
    # Redirect either to 'survey.template_name' if this attribute is set or
    # to the default template
    return render_to_response(survey.template_name or 'survey/survey_detail.html',
                              {'survey': survey, 'title': survey.title},
                              context_instance=RequestContext(request))

# TODO: ajaxify this page (jquery) : add a date picker, ...
# TODO: Fix the bug that make the questions and the choices unordered

@login_required()
def survey_edit(request,slug):
    survey = get_object_or_404(Survey, slug=slug)
    return render_to_response('survey/survey_edit.html',
                              {'survey': survey},
                              context_instance=RequestContext(request))

# TODO: Refactor the object add to avoid the code duplication.
# def object_add(request, object, form, template_name,
# post_create_redirect, extra_context):

@login_required()
def survey_add(request):
    if request.method == "POST":
        request_post = request.POST.copy()
        survey_form = SurveyForm(request_post)
        if survey_form.is_valid():
            new_survey = survey_form.save(commit=False)
            new_survey.created_by =  request.user
            new_survey.editable_by = request.user
            new_survey.slug = slugify(new_survey.title)
            new_survey.save()
            return HttpResponseRedirect(reverse("surveys-editable"))


    else:
        survey_form = SurveyForm()
    return render_to_response('survey/survey_add.html',
                              {'title': _("Add a survey"),
                               'form' : survey_form},
                              context_instance=RequestContext(request))

@login_required()
def survey_update(request, survey_slug):
    if request.method == "POST":
        request_post = request.POST.copy()
        survey = get_object_or_404(Survey, slug=survey_slug)
        survey_form = SurveyForm(instance=survey,data=request_post)
        if survey_form.is_valid():
            new_survey = survey_form.save(commit=False)
            new_survey.created_by =  request.user
            new_survey.editable_by = request.user
            new_survey.slug = slugify(new_survey.title)
            new_survey.save()
            return HttpResponseRedirect(reverse("survey-edit",None,(),{"slug":survey_slug}))


    else:
        survey = get_object_or_404(Survey, slug=survey_slug)
        print "survey : ",survey
        survey_form = SurveyForm(instance=survey)
    return render_to_response('survey/survey_add.html',
                              {'title': _("Add a survey"),
                               'form' : survey_form},
                              context_instance=RequestContext(request))

@login_required()
def survey_delete(request,slug):
    # TRICK: The following line does not have any logical explination
    # except than working around a bug in FF. It has been suggested there
    # http://groups.google.com/group/django-users/browse_thread/thread/e6c96ab0538a544e/0e01cdda3668dfce#0e01cdda3668dfce
    request_post = request.POST.copy()
    return delete_object(request, slug=slug,
        **{"model":Survey,
         "post_delete_redirect": reverse("surveys-editable"),
         "template_object_name":"survey",
         "login_required": True,
         'extra_context': {'title': _('Delete survey')}
        })

@login_required()
def question_add(request,survey_slug):
    survey = get_object_or_404(Survey, slug=survey_slug)
    if request.method == "POST":
        request_post = request.POST.copy()
        question_form = QuestionForm(request_post)
        if question_form.is_valid():
            new_question = question_form.save(commit=False)
            new_question.survey = survey
            new_question.save()
            return HttpResponseRedirect(reverse("survey-edit",None,(),
                                                {"slug":survey_slug}))

    else:
        question_form = QuestionForm()
    return render_to_response('survey/question_add.html',
                              {'title': _("Add a question"),
                               'form' : question_form},
                              context_instance=RequestContext(request))

@login_required()
def question_update(request,survey_slug,question_id):
    survey = get_object_or_404(Survey, slug=survey_slug)
    question =  get_object_or_404(Question,id=question_id)
    if question not in survey.questions.iterator():
        raise Http404()

    if request.method == "POST":
        request_post = request.POST.copy()
        question_form = QuestionForm(instance=question,data=request_post)
        if question_form.is_valid():
            new_question = question_form.save(commit=False)
            new_question.survey = survey
            new_question.save()
            return HttpResponseRedirect(reverse("survey-edit",None,(),
                                                {"slug":survey_slug}))
    else:
        question_form = QuestionForm(instance=question)
    return render_to_response('survey/question_add.html',
                              {'title': _("Update question"),
                               'form' : question_form},
                              context_instance=RequestContext(request))

@login_required()
def question_delete(request,survey_slug,question_id):
    # TRICK: The following line does not have any logical explination
    # except than working around a bug in FF. It has been suggested there
    # http://groups.google.com/group/django-users/browse_thread/thread/e6c96ab0538a544e/0e01cdda3668dfce#0e01cdda3668dfce
    request_post = request.POST.copy()
    return delete_object(request, object_id=question_id,
        **{"model":Question,
         "post_delete_redirect": reverse("survey-edit",None,(), {"slug":survey_slug}),
         "template_object_name":"question",
         "login_required": True,
         'extra_context': {'title': _('Delete question')}
        })

@login_required()
def choice_add(request,question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == "POST":
        request_post = request.POST.copy()
        choice_form = ChoiceForm(request_post)
        if choice_form.is_valid():
            new_choice = choice_form.save(commit=False)
            new_choice.question = question
            new_choice.save()
            return HttpResponseRedirect(reverse("survey-edit",None,(),
                                                {"slug":question.survey.slug}))
    else:
        choice_form = ChoiceForm()
    return render_to_response('survey/choice_add.html',
                              {'title': _("Add a choice"),
                               'form' : choice_form},
                              context_instance=RequestContext(request))

@login_required()
def choice_update(request,question_id, choice_id):
    question = get_object_or_404(Question, id=question_id)
    choice = get_object_or_404(Choice, id=choice_id)
    if choice not in question.choices.iterator():
        raise Http404()
    if request.method == "POST":
        request_post = request.POST.copy()
        choice_form = ChoiceForm(instance=choice,data=request_post)
        if choice_form.is_valid():
            new_choice = choice_form.save(commit=False)
            new_choice.question = question
            new_choice.save()
            return HttpResponseRedirect(reverse("survey-edit",None,(),
                                                {"slug":question.survey.slug}))
    else:
        choice_form = ChoiceForm(instance=choice)
    return render_to_response('survey/choice_add.html',
                              {'title': _("Update choice"),
                               'form' : choice_form},
                              context_instance=RequestContext(request))

@login_required()
def choice_delete(request,survey_slug,choice_id):
    # TRICK: The following line does not have any logical explination
    # except than working around a bug in FF. It has been suggested there
    # http://groups.google.com/group/django-users/browse_thread/thread/e6c96ab0538a544e/0e01cdda3668dfce#0e01cdda3668dfce
    request_post = request.POST.copy()
    return delete_object(request, object_id=choice_id,
        **{"model":Choice,
         "post_delete_redirect": reverse("survey-edit",None,(), {"slug":survey_slug}),
         "template_object_name":"choice",
         "login_required": True,
         'extra_context': {'title': _('Delete choice')}
        })

@login_required()
def editable_survey_list(request):
    login_user= request.user

    return object_list(request,
        **{ 'queryset': Survey.objects.filter(Q(created_by=login_user) |
                                            Q(editable_by=login_user)),
          'allow_empty': True,
          'template_name':"survey/editable_survey_list.html",
          'extra_context': {'title': _('Surveys')}}
    )

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
                reverse('answers-detail', None, (),
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
