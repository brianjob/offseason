from django.conf.urls import patterns, url
from account import views

urlpatterns = patterns('account.views',

	url(r'^importleague$', views.import_league, name='import_league'),
    url(r'^callback$', views.callback, name='callback'),
    url(r'^newleague$', views.new_league, name='new_league'),
    url(r'^configureinvites$', views.configure_invites, name='configure_invites')
)