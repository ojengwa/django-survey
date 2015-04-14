# Customized the Survey style #
As you will see on this page `django-survey` enable you to customized easily and in several ways the style of the page used to present the survey to the end user.

## How to change the template used by `survey_detail` ##
This method will enable you to change the overall look and feel for a Survey. Every Survey has an attribute `template_name` that enables you to overload path to the default template with your own customized version.

Here it is as a source for your inspiration the default template :
```
{% extends "survey/base.html" %}{% load i18n %}

{% block styles %}

<style type="text/css">

input[type="radio"] { vertical-align: top; }

span.required {color:red;}

span.helptext {color:green;}

div.horizontal ul li {padding-left:10px; margin-left:10px; display:inline;}

div.horizontal ul {margin-left:20px; padding-left:10px; display: inline;}

</style>

{% endblock %}

{% block content %}

<h1>{{ title }}</h1>



<form method="post" class="focus-input" action="">

    {% for question_form in survey.forms %}

        {{ question_form.as_template }}

    {% endfor %}

    <div class="submit-row"><input type="submit" value="{% trans 'Submit' %}" class="default" name="__vote" /></div>

</form>

{% endblock %}

```

Most of it is self explanatory except the line actually building  the form for each question :
```
{{ question_form.as_template }}
```
`as_template` is a method of `BaseAnswerForm` defined in the forms.py, this method is able to render a form based on a template.


## How to customize the style of the questions in your survey ##
An other place where you can alter the style of a survey is at the level of the questions. Every `Question` has an attribute `qstyle` that can be used to add the html attribute of the div surrounding the question.
For example:
```
>>> question = Question.objects.get(id=2)
>>> question.qstyle = 'class="horizontal"' 
```
Will give you the following html:
```
<div  'class="horizontal"'> 
   [ Question 2]
        [Choice 1]
        [Choice 2]
         ........
</div> 
```

This make the assumption that the style applied to this page will take care of handling this case.