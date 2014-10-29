from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^trades/', include('trades.urls', namespace='trades')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'login/*$', 'django.contrib.auth.views.login'),
    url(r'logout', 'django.contrib.auth.views.logout', {'template_name': 'registration/login.html'}),
    url(r'^$', 'trades.views.home'),
    url(r'^.tMgutFCXAM_a9yQlnXOFj0GZ.EIc1k0Eq4opnsAPg--.html$', 'django.contrib.auth.views.login')
)
