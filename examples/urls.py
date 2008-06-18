from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.views import login
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    # Example:
    ('^admin/', include('django.contrib.admin.urls')),
    (r'survey/', include('survey.urls')),
    url(r'^login/$', login,
        {'template_name':'admin/login.html'},name='auth_login'),
    url(r'^$', direct_to_template, {"template" : "main_page.html"})

)
