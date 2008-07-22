from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.contrib.auth.views import login
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    # Admin
    (r'^admin/(.*)', admin.site.root),
    # Example:
    (r'survey/', include('survey.urls')),
    url(r'^login/$', login,
        {'template_name':'admin/login.html'},name='auth_login'),
    url(r'^$', direct_to_template, {"template" : "main_page.html"})

)
