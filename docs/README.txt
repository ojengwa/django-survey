==============
Django Survey
==============

A Django application that allows you to construct web based surveys from a number 
of question types.

Questions are constructed from a number of question types:

* Text Input
* Text Area
* Select One Choice
* Radio List
* Radio Image List
* Checkbox List

A number of Questions make up a Questionnaire. A Survey can be planned to take 
place over a specified time period using a Questionnaire. Submissions made by
users responding to a Survey are captured as Answers. The Answers can be 
displayed in an interface for any given Survey.

An example database is provided in the exampled folder using sqlite. 
Assuming that the survey application is on your Python Path, 
type manage.py runserver from a command line in the examples folder. 
Start a browser on http://127.0.0.1:8000/. The admin user name and password for 
the example database is admin and admin.
