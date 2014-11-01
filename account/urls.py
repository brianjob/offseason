from django.conf.urls import patterns, url
from account import views

urlpatterns = patterns('account.views',

	url(r'^importleague$', views.import_league, name='import_league'),
    url(r'^callback$', views.callback, name='callback')
)