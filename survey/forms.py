from models import QTYPE_CHOICES, Answer, Survey, Question, Choice
from django.newforms import BaseForm, Form, ValidationError
from django.newforms import CharField, ChoiceField
from django.newforms import Textarea, TextInput, Select, RadioSelect,\
                        CheckboxSelectMultiple, MultipleChoiceField
from django.newforms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify

from itertools import chain
import uuid


class BaseAnswerForm(Form):
    def __init__(self, question, user, interview_uuid, session_key, *args, **kwdargs):
        self.question = question
        self.session_key = session_key.lower()
        self.user = user
        self.interview_uuid = interview_uuid
        super(BaseAnswerForm, self).__init__(*args, **kwdargs)
        answer = self.fields['answer']
        answer.required = question.required
        answer.label = question.text
        if not question.required:
            answer.help_text = unicode(_('(this question is optional)'))
    def save(self, commit=True):
        if not self.cleaned_data['answer']:
            if self.fields['answer'].required:
                raise ValidationError, _('This field is required.')
            return
        ans = Answer()
        ans.question = self.question
        ans.session_key = self.session_key
        ans.user = self.user
        ans.interview_uuid = self.interview_uuid
        ans.text = self.cleaned_data['answer']
        if commit: ans.save()
        return ans

class TextInputAnswer(BaseAnswerForm):
    answer = CharField()

class TextAreaAnswer(BaseAnswerForm):
    answer = CharField(widget=Textarea)

class NullSelect(Select):
    def __init__(self, attrs=None, choices=(), empty_label=u"---------"):
        self.empty_label = empty_label
        super(NullSelect, self).__init__(attrs, choices)

    def render(self, name, value, attrs=None, choices=(), **kwdargs):
        empty_choice = ()
        # kwdargs is needed because it is the only way to determine if an
        # override is provided or not.
        if 'empty_label' in kwdargs:
            if kwdargs['empty_label'] is not None:
                empty_choice = ((u'', kwdargs['empty_label']),)
        elif self.empty_label is not None:
            empty_choice = ((u'', self.empty_label),)
        base_choices = self.choices
        self.choices = chain(empty_choice, base_choices)
        result = super(NullSelect, self).render(name, value, attrs, choices)
        self.choices = base_choices
        return result

class ChoiceAnswer(BaseAnswerForm):
    answer = ChoiceField(widget=NullSelect)

    def __init__(self, *args, **kwdargs):
        super(ChoiceAnswer, self).__init__(*args, **kwdargs)
        choices = [ (str(opt.id), opt.text)
                    for opt in self.question.choices.all() ]
        self.choices = choices
        self.choices_dict = dict(choices)
        self.fields['answer'].choices = choices
    def clean_answer(self):
        key = self.cleaned_data['answer']
        if not key and self.fields['answer'].required:
            raise ValidationError, _('This field is required.')
        return self.choices_dict.get(key, key)

class ChoiceRadio(ChoiceAnswer):
    def __init__(self, *args, **kwdargs):
        super(ChoiceRadio, self).__init__(*args, **kwdargs)
        self.fields['answer'].widget = RadioSelect(choices=self.choices)

class ChoiceImage(ChoiceAnswer):
    def __init__(self, *args, **kwdargs):
        super(ChoiceImage, self).__init__(*args, **kwdargs)
        self.choices = [ (k,mark_safe('<img src="'+v+'"/>')) for k,v in self.choices ]
        self.fields['answer'].widget = RadioSelect(choices=self.choices)

class ChoiceCheckbox(BaseAnswerForm):
    answer = MultipleChoiceField(widget=CheckboxSelectMultiple)

    def __init__(self, *args, **kwdargs):
        super(ChoiceCheckbox, self).__init__(*args, **kwdargs)
        choices = [ (str(opt.id), opt.text)
                    for opt in self.question.choices.all() ]
        self.choices = choices
        print "choices in the checkbox list : ", choices
        self.choices_dict = dict(choices)
        self.fields['answer'].choices = choices
        print "##self.fields",self.fields
    def clean_answer(self):

        keys = self.cleaned_data['answer']
        print "Choice Checkbox clean answer : ", keys
        if not keys and self.fields['answer'].required:
            raise ValidationError, _('This field is required.')
        for key in keys:
            if not key and self.fields['answer'].required:
                raise ValidationError, _('Invalid Choice.')
        return [self.choices_dict.get(key, key) for key in keys]
    def save(self, commit=True):
        if not self.cleaned_data['answer']:
            if self.fields['answer'].required:
                raise ValidationError, _('This field is required.')
            return
        ans_list = []
        for text in self.cleaned_data['answer']:
            ans = Answer()
            ans.question = self.question
            ans.session_key = self.session_key
            ans.text = text
            if commit: ans.save()
            ans_list.append(ans)
        return ans_list

## each question gets a form with one element, determined by the type
## for the answer.
QTYPE_FORM = {
    'T': TextInputAnswer,
    'A': TextAreaAnswer,
    'S': ChoiceAnswer,
    'R': ChoiceRadio,
    'I': ChoiceImage,
    'C': ChoiceCheckbox,
}

def forms_for_survey(survey, request):
    ## add session validation to base page.
    sp = str(survey.id) + '_'
    session_key = request.session.session_key.lower()
    login_user = request.user
    random_uuid = uuid.uuid4().hex
    post = request.POST if request.POST else None # bug in newforms
    return [QTYPE_FORM[q.qtype](q, login_user, random_uuid, session_key, prefix=sp+str(q.id), data=post)
            for q in survey.questions.all() ]

class SurveyForm(ModelForm):
    class Meta:
        model = Survey
        exclude = ("created_by","editable_by","slug")
    def clean(self):
        title_slug = slugify(self.cleaned_data.get("title"))
        if not len(Survey.objects.filter(slug=title_slug))==0:
            raise ValidationError, _('The title of the survey must be unique.')
        return self.cleaned_data


class QuestionForm(ModelForm):
    class Meta:
        model= Question
        exclude = ("survey")

class ChoiceForm(ModelForm):
    class Meta:
        model = Choice
        exclude = ("question")
