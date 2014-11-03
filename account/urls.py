from django.conf.urls import patterns, url
from account import views

urlpatterns = patterns('account.views',

	url(r'^importleague$', views.import_league, name='import_league'),
    url(r'^import_league_callback$', views.import_league_callback, name='import_league_callback'),
    url(r'^newleague$', views.new_league, name='new_league'),
    url(r'^configureinvites$', views.configure_invites, name='configure_invites'),
    url(r'^signup$', views.register_page, name='register_page'),
    url(r'^register$', views.register, name='register'),
    url(r'^link_profile_callback$', views.link_profile_callback, name='link_profile_callback'),
    url(r'^dashboard$', views.dashboard, name='dashboard')
)