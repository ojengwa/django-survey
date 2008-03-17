from models import QTYPE_CHOICES, Answer
from django.newforms import BaseForm, Form, ValidationError
from django.newforms import CharField, ChoiceField
from django.newforms import Textarea, TextInput, Select, RadioSelect
from django.utils.translation import ugettext_lazy as _
from itertools import chain


class BaseAnswerForm(Form):
    def __init__(self, question, session_key, *args, **kwdargs):
        self.question = question
        self.session_key = session_key.lower()
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
                    for opt in self.question._choices.all() ]
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
        self.choices = [ (k,'<img src="'+v+'"/>') for k,v in self.choices ]
        self.fields['answer'].widget = RadioSelect(choices=self.choices)

## each question gets a form with one element, determined by the type
## for the answer.
QTYPE_FORM = {
    'T': TextInputAnswer,
    'A': TextAreaAnswer,
    'S': ChoiceAnswer,
    'R': ChoiceRadio,
    'I': ChoiceImage,
}

def forms_for_survey(survey, request):
    ## add session validation to base page.
    sp = str(survey.id) + '_'
    session_key = request.session.session_key.lower()
    post = request.POST if request.POST else None # bug in newforms
    return [QTYPE_FORM[q.qtype](q, session_key, prefix=sp+str(q.id), data=post)
            for q in survey.questions.all() ]
