from django.conf.urls import patterns, url
from account import views

urlpatterns = patterns('account.views',

	url(r'^authenticate_yahoo_user$', views.authenticate_yahoo_user, name='authenticate_yahoo_user'),
    url(r'^callback$', views.callback, name='callback')
)