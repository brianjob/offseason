from django.shortcuts import render, get_object_or_404
from account.import_league import League_Import
from django.http import HttpResponseRedirect
from trades.models import League
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
	return render(request, 'account/dashboard.html')

@login_required
def new_league(request):
	return render(request, 'account/new_league.html')

@login_required
def import_league(request):
	li = League_Import()
	request.session['league_id'] = request.POST['league_id']
	request.session['request_token'] = li.get_request_token_str()
	return HttpResponseRedirect(li.get_authorization_url())

@login_required
def callback(request):
	league_id=request.session['league_id']
	li = League_Import(request.session['request_token'], request.GET['oauth_verifier'])

	no_email_managers = li.import_league(league_id, request.user.manager)

	profile = ", ".join(no_email_managers)

	return render(request, 'account/debug.html', { 'profile' : profile })

@login_required
def configure_invites(request, league_id):
	league = get_object_or_404(League, pk=league_id)

	managers_to_invite = league.manager_set.filter(user=None)
	existing_managers = league.manager_set.exclude(user=None)

	return render(request, 'account/send_invitations.html', 
		{ 'managers_to_invite' : managers_to_invite,
		  'existing_managers' : existing_managers })
