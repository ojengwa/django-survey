# Pre-requisite #
> You need to run this application using the latest trunk of Django, see: http://www.djangoproject.com/download/. From [revision 81](https://code.google.com/p/django-survey/source/detail?r=81) and above "django-survey" relies on "newforms-admin", this feature has been merged in django's trunk for the milestone called : [1.0 alpha](http://code.djangoproject.com/milestone/1.0%20alpha)
Python [uuid](http://pypi.python.org/pypi/uuid/) module is a prerequisite to run django-survey. It is a standard library from python 2.5.

# Getting django-survey #
> Download the django-survey application by following the SVN checkout instructions: http://code.google.com/p/django-survey/source/checkout.  The trunk is the main place for checkins.  While it may be occasionally stable, we'll make tags or branches for official snapshots.

# Using django-survey #
> The source directory you checkout will hold four subdirectories:
    * docs:  empty, though its intended purpose should be clear
    * examples: a sample Django project using django-survey
    * survey: the django-survey application
    * tests: empty, to be filled with tests (see: http://www.djangoproject.com/documentation/testing/).

> Run the sample project from the top of the source tree:
```
$ ls -CF
docs/		examples/	survey/		tests/
$ python examples/manage.py runserver
Validating models...
0 errors found

Django version 0.97-pre-SVN-unknown, using settings 'examples.settings'
Development server is running at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

> After directing your browser to the development server (printed above), you will be able to view an existing survey.  Log in to the admin interface (use admin/admin for the username/passwd) to add/modify/delete users, surveys, questions, etc. in the sample project's sqlite3 database.