from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^home$', home),
	(r'^login$', login),
	(r'^logged$', login),
	(r'^logout$', log_out),
    (r'^contact$', contact),
    (r'^send$', contact),
    (r'^loans$', loans),
    (r'^payments$', payments),
    (r'^transfer$', transfer),
    (r'^sucess$', sucess),
    (r'^balance$', balance),
    (r'^about$', about),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),

)

if settings.SERVE_STATIC_FILES:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
    # staticfiles
    urlpatterns += staticfiles_urlpatterns()