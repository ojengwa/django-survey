"""Survey Models
"""
from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.utils import encoding
from django.template.defaultfilters import date as datefilter
from django.utils.translation import ugettext_lazy as _
from datetime import *

QTYPE_CHOICES = (
    ('T', 'Text Input'),
    ('A', 'Text Area'),
    ('S', 'Select One Choice'),
    ('R', 'Radio List'),
    ('I', 'Radio Image List')
)

class Survey(models.Model):
    slug    = models.SlugField(_('survey name'), unique=True)
    title   = models.CharField(_('survey title'), max_length=80)
    visible = models.BooleanField(_('survey is visible'))
    public  = models.BooleanField(_('survey results are public'))
    ## Add validation on datetimes
    opens   = models.DateTimeField(_('survey starts accepting submissions on'))
    closes  = models.DateTimeField(_('survey stops accepting submissions on'))

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
        now = datetime.now()
        if self.opens >= now:
            value = False
            duration = (now - self.opens).seconds
        elif self.closes >= now:
            value = True
            duration = (self.closes - now).seconds
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
        if not self.visible: return _('')
        if self.open: return _('open')
        if datetime.now() < self.opens:
            return unicode(_('opens ')) + datefilter(self.opens)
        return _('closed')

    @property
    def answer_count(self):
        if hasattr(self, '_answer_count'):
            return self._answer_count
        self._answer_count = sum(q.answer_count for q in self.questions)
        return self._answer_count

    @property
    def submission_count(self):
        if hasattr(self, '_submission_count'):
            return self._submission_count
        self._submission_count = len(Answer.objects.filter(
            question__survey=self.id).values('session_key').distinct())
        return self._submission_count

    def has_answers_from(self, session_key):
        return bool(
            Answer.objects.filter(session_key__exact=session_key.lower(),
            question__survey__id__exact=self.id).distinct().count())

    def __unicode__(self):
        return u' - '.join([self.slug, self.title])

    class Admin:
        list_display = ('__unicode__', 'visible', 'public',
                        'opens', 'closes', 'open')

    @models.permalink
    def get_absolute_url(self):
        return ('survey', (), {'slug': self.slug })

    def save(self):
        res = super(Survey, self).save()
        cache.delete(self._cache_name)
        return res

    def answers_viewable_by(self, user):
        if not self.visible: return False
        if self.public: return True
        if user.is_anonymous(): return False
        return user.has_perm('survey.view_answers')


class Question(models.Model):
    survey   = models.ForeignKey(Survey, related_name='questions',
                                 edit_inline=models.TABULAR,
                                 min_num_in_admin=5,
                                 num_in_admin=5, num_extra_on_change=3,
                                 verbose_name=_('survey'))
    qtype    = models.CharField(_('question type'), max_length=2,
                                choices=QTYPE_CHOICES)
    required = models.BooleanField(_('required'), default=True)
    text     = models.TextField(_('question text'), core=True)

    ## model validation for requiring choices.

    @property
    def answer_count(self):
        if hasattr(self, '_answer_count'):
            return self._answer_count
        self._answer_count = self.answers.count()
        return self._answer_count

    def __unicode__(self):
        return u' - '.join([self.survey.slug, self.text])

    class Meta:
        unique_together = (('survey', 'text'),)
        order_with_respect_to='survey'
        ordering = ('survey', 'id')

    class Admin:
        list_select_related = True
        list_filter = ('survey', 'qtype')
        list_display_links = ('text',)
        list_display = ('survey', 'text', 'qtype', 'required')
        search_fields = ('text',)

    @property
    def choices(self):
        return self._choices.extra(
            select={
                '_count':
                    'SELECT COUNT(*) '
                    'FROM "survey_answer" '
                    'WHERE ("survey_answer"."text" = "survey_choice"."text" '
                    '       AND "survey_answer"."question_id" = '
                    '           "survey_choice"."question_id")'
            },
        )

class Choice(models.Model):
    ## validate question is of proper qtype
    question = models.ForeignKey(Question, related_name='_choices',
                                 edit_inline=models.TABULAR,
                                 min_num_in_admin=5,
                                 num_in_admin=5, num_extra_on_change=3,
                                 verbose_name=_('question'))
    text = models.CharField(_('choice text'), max_length=500, core=True)

    @property
    def count(self):
        if hasattr(self, '_count'):
            return self._count
        self._count = Answer.objects.filter(question=self.question_id,
                                            text=self.text).count()
        return self._count

    def __unicode__(self):
        return self.text

    class Meta:
        unique_together = (('question', 'text'),)
        order_with_respect_to='question'
        ordering = ('question', 'id')

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers',
                                 verbose_name=_('question'),
                                 editable=False)
    ## sessions expire, survey results do not, so keep the key.
    session_key = models.CharField(_('session key'), max_length=40)
    text = models.TextField(_('anwser text'))

    class Admin:
        list_display = ('question', 'session_key', 'text')
        #list_filter = ('question__survey',)
        search_fields = ('text',)
        list_select_related=True
    class Meta:
        unique_together = (('question', 'session_key'),)
        permissions = (("view_answers",     "Can view survey answers"),
                       ("view_submissions", "Can view survey submissions"))
