from django.shortcuts import render
from trades.import_league import League_Import
from django.http import HttpResponseRedirect
from trades.models import Team

# Create your views here.
def authenticate_yahoo_user(request):
	li = League_Import()
	request.session['request_token'] = li.get_request_token_str()
	return HttpResponseRedirect(li.get_authorization_url())

def callback(request):
	li = League_Import(request.session['request_token'], request.GET['oauth_verifier'])

	bens_team = Team.objects.get(name="Cano's Huge Wallet")

	li.fill_roster(bens_team)

	profile = "did it work?"

	return render(request, 'trades/debug.html', { 'profile' : profile })