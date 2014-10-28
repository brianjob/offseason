from django.conf.urls import patterns, url
from trades import views

urlpatterns = patterns('trades.views',

    url(r'league/(?P<league_id>\d+)$', views.league, name='league'),
    url(r'league$', views.league, name='league'),
    url(r'^team/(?P<team_id>\d+)$', views.team, name='team'),
    url(r'^team$', views.team, name='team'),

    url(r'newtrade/(?P<team_id>\d+)$', views.new_trade, name='new_trade'),
    url(r'propose/(?P<team_id>\d+)$', views.propose_trade, name='propose_trade'),
    url(r'^trade/(?P<trade_id>\d+)$', views.trade, name='trade'),

    url(r'^submit$', views.submit_trade, name='submit_trade'),
    url(r'^cancel$', views.cancel_trade, name='cancel_trade'),
    url(r'^accept$', views.accept_trade, name='accept_trade'),
    url(r'^reject$', views.reject_trade, name='reject_trade'),
    url(r'^veto$', views.veto, name='veto'),

    url(r'^inbox$', views.inbox, name='inbox'),
    url(r'^outbox$', views.outbox, name='outbox'),
    url(r'^drafts$', views.drafts, name='drafts'),
    url(r'^pending$', views.pending, name='pending'),
    url(r'^my_trans$', views.my_trans, name='my_trans'),
    url(r'^league_trans$', views.league_trans, name='league_trans')
)
