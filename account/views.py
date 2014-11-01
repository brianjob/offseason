from django.shortcuts import render
from account.import_league import League_Import
from django.http import HttpResponseRedirect

# Create your views here.
def authenticate_yahoo_user(request):
	li = League_Import()
	request.session['request_token'] = li.get_request_token_str()
	return HttpResponseRedirect(li.get_authorization_url())

def callback(request):
	li = League_Import(request.session['request_token'], request.GET['oauth_verifier'])

	no_email_managers = li.import_league('5940')

	profile = ", ".join(no_email_managers)

	return render(request, 'trades/debug.html', { 'profile' : profile })