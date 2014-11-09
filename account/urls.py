from django.conf.urls import patterns, url
from account import views

urlpatterns = patterns('account.views',

	url(r'^importleague$', views.import_league, name='import_league'),
    url(r'^import_league_callback$', views.import_league_callback, name='import_league_callback'),
    url(r'^newleague$', views.new_league, name='new_league'),
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    url(r'^login_user', views.login_user, name='login_yahoo'),
    url(r'^login_callback$', views.login_callback, name='login_callback'),
    url(r'^fill_roster', views.fill_roster, name='fill_roster')
)