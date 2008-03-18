from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    ('^admin/', include('django.contrib.admin.urls')),
    (r'',      include('survey.urls')),
)
