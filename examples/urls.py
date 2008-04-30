from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    ('^admin/', include('django.contrib.admin.urls')),
    (r'survey/',      include('survey.urls')),
)
