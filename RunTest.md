#How to run the test suite

# Test in django-survey #
This reusable app comes with a test suite that is relatively complete. This project uses the regular [django test suite](http://www.djangoproject.com/documentation/testing/). The test are located inside a folder called "tests". The doctests are spread in 3 files, they name are self explanatory :
  * test\_images.py
  * test\_models.py
  * test\_urls.py


## How to run it ##
If you need a longer explanation on how to run the tests please read the  [django documentation](http://www.djangoproject.com/documentation/testing/#running-tests) else the short version is illustrated below.

```
django-survey\examples# manage.py test survey

Creating test database...
Creating table auth_permission
Creating table auth_group
Creating table auth_user
Creating table auth_message
Creating table django_site
Creating table django_content_type
Creating table django_session
Creating table django_admin_log
Creating table survey_survey
Creating table survey_question
Creating table survey_choice
Creating table survey_answer
Installing index for auth.Permission model
Installing index for auth.Message model
Installing index for admin.LogEntry model
Installing index for survey.Survey model
Installing index for survey.Question model
Installing index for survey.Choice model
Installing index for survey.Answer model
...
----------------------------------------------------------------------
Ran 3 tests in 7.000s

OK
Destroying test database...

```

## Coverage ##
This [presentation](http://www.slideshare.net/guest18915c/an-app-in-a-week/) give a recipe to evaluate the coverage of your test suite. This information is extracted using the [coverage.py](http://nedbatchelder.com/code/modules/coverage.html). I found this [page](http://garethrees.org/2001/12/04/python-coverage/) useful to understand how to use it.

```
# coverage.py -e
# coverage.py -x manage.py test survey
# coverage.py -r -m >report.txt
```

Then you need to analyze the file called "report.txt" and extract the information usefull to your project. In our case all the files located in django-survey :
```
Name                                                                                                               Stmts   Exec  Cover   Missing
------------------------------------------------------------------------------------------------------------------------------------------------
__init__                                                                                                               0      0   100%   
[...]
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\__init__                                              0      0   100%   
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\forms                                               172    117    68%   32, 47-49, 56, 74-86, 96, 107, 117-120, 126-136, 139-145, 147-159, 212, 226-227, 230
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\models                                              157    142    90%   28-29, 70, 82-83, 88-89, 102-104, 109, 126, 159, 211, 236
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\templatetags\__init__                                 0      0   100%   
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\templatetags\survey                                  10      7    70%   8, 16-17
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\tests\__init__                                        2      2   100%   
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\tests\test_images                                     1      1   100%   
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\tests\test_models                                     1      1   100%   
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\tests\test_urls                                       1      1   100%   
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\urls                                                  6      6   100%   
c:\yml\_myscript_\dj_things\web_development\django-survey\survey\views                                               183    126    68%   47, 54-65, 79-83, 90, 94, 96, 124-125, 150-151, 157-158, 183-186, 230-231, 246, 261-263, 280-281, 311-313, 328, 341-342, 359-360, 379, 419-425, 444-456, 462-474
[...]
manage                                                                                                                13      9    69%   10-13
management\__init__                                                                                                    0      0   100%   
settings                                                                                                              31     31   100%   
urls                                                                                                                   4      4   100%   


```