from django.shortcuts import render
from account.import_league import League_Import
from django.http import HttpResponseRedirect

def dashboard(request):
	return render(request, 'account/dashboard.html')

def import_league(request, league_id):
	li = League_Import()
	request.session['request_token'] = li.get_request_token_str()
	return HttpResponseRedirect(li.get_authorization_url())

def callback(request):
	li = League_Import(request.session['request_token'], request.GET['oauth_verifier'])

	no_email_managers = li.import_league('5940')

	profile = ", ".join(no_email_managers)

	return render(request, 'account/debug.html', { 'profile' : profile })