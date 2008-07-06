"""Survey Models
"""
import datetime

from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.utils import encoding
from django.template.defaultfilters import date as datefilter
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


QTYPE_CHOICES = (
    ('T', 'Text Input'),
    ('A', 'Text Area'),
    ('S', 'Select One Choice'),
    ('R', 'Radio List'),
    ('I', 'Radio Image List'),
    ('C', 'Checkbox List')
)

class Questionnaire(models.Model):
    """
    A Questionnaire consists of a number of ``Questions``. It allows sets of
    Questions to be reused in any number of surveys.
    """
    title = models.CharField(_('questionnaire title'), max_length=80)
    
    class Meta:
        verbose_name = _('questionnaire')
        verbose_name_plural = _('questionnaires')
    
    class Admin:
        list_display = ('__unicode__', 'title')
        search_fields = ('title', )
        
    def __unicode__(self):
        return u"%s" % self.title

class Question(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, related_name='questions',
                             verbose_name=_('questionnaire'))
    qtype = models.CharField(_('question type'), max_length=2,
                                choices=QTYPE_CHOICES)
    required = models.BooleanField(_('required'), default=True)
    text     = models.TextField(_('question text'), core=True)
    order = models.IntegerField(verbose_name = _("order"),
                                null=True, blank=True, core=True)
    # TODO: Add a button or check box to remove the file. There are several
    # recipes floating on internet. I like the one with a custom widget
    image = models.ImageField(verbose_name=_("image"),
                              upload_to= "survey/images/questions" + "/%Y/%m/%d/",
                              null=True, blank= True, core=False)
    # TODO: Make choice_group mandatory if qtype is choices.
    choice_group = models.ForeignKey('ChoiceGroup', related_name='questions', blank=True, null=True)
    # TODO: Modify the forms to respect the style defined by this attr (html,css)
    qstyle = models.TextField(_("Html Style"),null=True, blank=True)
    ## model validation for requiring choices.

    #@property
    def answer_count(self, survey):
        if hasattr(self, '_answer_count'):
            return self._answer_count
        self._answer_count = self.answers.filter(survey=survey).count()
        return self._answer_count


    def __unicode__(self):
        return u' - '.join([self.questionnaire.title, self.text])

    class Meta:
        unique_together = (('questionnaire', 'text'),)
        order_with_respect_to='questionnaire'
        ordering = ('questionnaire', 'order')

    class Admin:
        list_select_related = True
        list_filter = ('questionnaire', 'qtype')
        list_display_links = ('text',)
        list_display = ('questionnaire', 'text', 'qtype', 'required')
        search_fields = ('text',)

    @models.permalink
    def get_update_url(self):
        return ('question-update', (), {'questionnaire_title': self.questionnaire.title,'questionnaire_id' :self.id  })

    # TODO: add this a fallback to this optimisation with django ORM.
    @property
    def choice_count(self):
        return self.choice_group.choices.count()

    
class SurveyManager(models.Manager):

    def surveys_for(self, recipient):
        recipient_type = ContentType.objects.get_for_model(recipient)
        return Survey.objects.filter(visible=True,recipient_type=recipient_type, recipient_id=recipient.id)


class Survey(models.Model):
    """
    A ``Survey`` is the activity of gathering answers based on a 
    ``Questionnaire``. This allows you to run one or more surveys using the 
    same Questionnaire, but obviously capturing difference answers.
    """
    title   = models.CharField(_('survey title'), max_length=80)
    slug    = models.SlugField(_('slug'),
                            prepopulate_from=("title",), unique=True)
    description= models.TextField(verbose_name=_("description"),
                            help_text=_("This field appears on the public web site and should give an overview to the interviewee"),
                            blank=True)
    questionnaire = models.ForeignKey(Questionnaire, related_name='surveys',
                                 verbose_name=_('questionnaires'))
    
    ## Add validation on datetimes
    opens   = models.DateTimeField(_('survey starts accepting submissions on'))
    closes  = models.DateTimeField(_('survey stops accepting submissions on'))
    # Define the behavior of the survey
    visible = models.BooleanField(_('survey is visible'))
    public  = models.BooleanField(_('survey results are public'))
    restricted = models.BooleanField(verbose_name=_("restrict the survey to authentified user")
                                     ,blank=True,default=False)
    allows_multiple_interviews = models.BooleanField(verbose_name=_("allows multiple interviews")
                                                     ,blank=True,default=True)
    template_name = models.CharField(_('template name'),max_length=150,
                                     null=True, blank=True,
        help_text=_("This field is used to define a custom template (Example: 'dj_survey/template/my_add_interview_forms.html')."))

    # Control who can edit the survey
    # TODO: Plug this control in the view used to edit the survey
    created_by = models.ForeignKey(User, related_name="created_surveys")
    editable_by = models.ForeignKey(User,related_name="owned_surveys")

    # Integration in Pinax
    recipient_type = models.ForeignKey(ContentType,null=True)
    recipient_id = models.PositiveIntegerField(null=True)
    recipient = generic.GenericForeignKey('recipient_type', 'recipient_id')

    objects = SurveyManager()

    @property
    def _cache_name(self):
        if not self.id:
            id = 'new'
        else:
            id = int(self.id)
        return 'survey_' + repr(id) + '_status'

    @property
    def open(self):
        if not self.visible: return False
        value = cache.get(self._cache_name)
        if value is not None: return value
        now = datetime.datetime.now()
        if self.opens >= now:
            value = False
            duration = (now - self.opens).seconds
        elif self.closes >= now:
            value = True
            duration = (self.opens - now).seconds
        else:
            value = False
            duration = 60*60*24*31
        if duration:
            cache.set(self._cache_name, value, duration)
        return value

    @property
    def closed(self):
        return not self.open

    @property
    def status(self):
        if not self.visible: return _('private')
        if self.open: return _('open')
        if datetime.now() < self.opens:
            return unicode(_('opens ')) + datefilter(self.opens)
        return _('closed')

    @property
    def answer_count(self):
        if hasattr(self, '_answer_count'):
            return self._answer_count
        self._answer_count = sum(q.answer_count for q in self.questions.iterator())
        return self._answer_count

    @property
    def interview_count(self):
        # NOTSURE: Do we realy need this optimisation?
        if hasattr(self, '_interview_count'):
            return self._interview_count
        self._interview_count = len(Answer.objects.filter(
            survey=self.id).values('interview_uuid').distinct())
        return self._interview_count

    @property
    def session_key_count(self):
        # NOTSURE: Do we realy need this optimisation?
        if hasattr(self, '_session_key_count'):
            return self._submission_count
        self._submission_count = len(Answer.objects.filter(
            survey=self.id).values('session_key').distinct())
        return self._submission_count


    def has_answers_from(self, session_key):
        return bool(
            Answer.objects.filter(session_key__exact=session_key.lower(),
            survey__exact=self.id).distinct().count())



    def __unicode__(self):
        return u' - '.join([self.slug, self.title])

    class Admin:
        list_display = ('__unicode__', 'visible', 'public',
                        'opens', 'closes', 'open')

    @models.permalink
    def get_absolute_url(self):
        return ('survey-detail', (), {'survey_slug': self.slug })

    def save(self):
        res = super(Survey, self).save()
        cache.delete(self._cache_name)
        return res

    def answers_viewable_by(self, user):
        if not self.visible: return False
        if self.public: return True
        if user.is_anonymous(): return False
        return user.has_perm('survey.view_answers')

class ChoiceGroup(models.Model):
    name = models.CharField(_('choice group name'), max_length=30)
    description = models.TextField(_('choice group description'), blank=True, null=True)
    # Define if the user must select at least 'choice_num_min' number of
    # choices and at most 'choice_num_max'
    choice_num_min = models.IntegerField(_("minimun number of choices"),
                                         null=True, blank=True,)
    choice_num_max = models.IntegerField(_("maximum number of choices"),
                                         null=True, blank=True,)
    
    class Meta:
        pass
    class Admin:
        pass
    
    def __unicode__(self):
        if self.description:
            return u'%s: %s' % (self.name, self.description) 
        return u'%s' % (self.name)

class Choice(models.Model):
    ## validate question is of proper qtype
    choice_group = models.ForeignKey(ChoiceGroup, related_name='choices',
                                    edit_inline=models.TABULAR,
                                    min_num_in_admin=5,
                                    num_in_admin=5, num_extra_on_change=3,
                                    verbose_name=_('choice group'),
                                    null=True,
                                    )
    text = models.CharField(_('choice text'), max_length=500, core=True)
    # TODO: Add a button or check box to remove the file. There are several
    # recipes floating on internet. I like the one with a custom widget
    image = models.ImageField(verbose_name = _("image"),
                              upload_to= "survey/images/questions" + "/%Y/%m/%d/",
                              null=True ,blank= True)

    order = models.IntegerField(verbose_name = _("order"),
                                null=True, blank=True, core=True)
    class Meta:
        unique_together = (('choice_group', 'text'),)
        order_with_respect_to='choice_group'
        ordering = ('choice_group', 'order')

    class Admin:
        list_display = ('choice_group', 'text')
        ordering = ('choice_group', 'order')

    @models.permalink
    def get_update_url(self):
        return ('choice-update', (), {'choice_group_id': self.choice_group.id,'choice_id' :self.id  })

    @property
    def count(self):
        if hasattr(self, '_count'):
            return self._count
        self._count = Answer.objects.filter(question=self.choice_group__question_id,
                                            text=self.text).count()
        return self._count

    def __unicode__(self):
        return self.text


class Answer(models.Model):
    """
    An ``Answer`` stores the response by a user to a question in a survey. 
    Note that the question may be repeated in many surveys.
    """
    user = models.ForeignKey(User, related_name='answers',
                             verbose_name=_('user'), editable=False,
                             blank=True,null=True)
    survey = models.ForeignKey(Survey, related_name='answers',
                             verbose_name=_('survey'), editable=False,
                             blank=True,null=True)
    question = models.ForeignKey(Question, related_name='answers',
                                 verbose_name=_('question'),
                                 editable=False)
    ## sessions expire, survey results do not, so keep the key.
    session_key = models.CharField(_('session key'), max_length=40)
    text = models.TextField(_('anwser text'))
    submission_date = models.DateTimeField(auto_now=True)
    # UUID is used to calculate the number of interviews
    interview_uuid = models.CharField(_("Interview uniqe identifier"),max_length=36)

    class Admin:
        list_display = ('interview_uuid','question','survey', 'user', 
                        'submission_date', 'session_key', 'text')
        list_filter = ('survey',)
        search_fields = ('text',)
        list_select_related=True
    class Meta:
        # unique_together = (('question', 'session_key'),)
        permissions = (("view_answers",     "Can view survey answers"),
                       ("view_submissions", "Can view survey submissions"))
