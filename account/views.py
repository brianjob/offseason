from django.shortcuts import render, get_object_or_404
from account.import_league import League_Import
from django.http import HttpResponseRedirect
from trades.models import League, Manager, Team
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse

IMPORT_LEAGUE_CALLBACK = 'http://intense-retreat-2626.herokuapp.com/account/import_league_callback'
LINK_PROFILE_CALLBACK = 'http://intense-retreat-2626.herokuapp.com/account/link_profile_callback'

@login_required
def dashboard(request):
	return render(request, 'account/dashboard.html')

def register_page(request):
	return render(request, 'account/register.html')

def register(request):
	return HttpResponseRedirect(reverse('account:link_profile'))

@login_required
def new_league(request):
	return render(request, 'account/new_league.html')

@login_required
def import_league(request):
	li = League_Import(IMPORT_LEAGUE_CALLBACK)
	request.session['league_id'] = request.POST['league_id']
	request.session['request_token'] = li.get_request_token_str()
	return HttpResponseRedirect(li.get_authorization_url())

@login_required
def import_league_callback(request):
	league_id=request.session['league_id']
	li = League_Import(IMPORT_LEAGUE_CALLBACK,
		request.session['request_token'], request.GET['oauth_verifier'])

	league = li.import_league(league_id, request.user.manager)
	commish_team = Team.objects.filter(league=league).get(manager=league.commissioner)
	msg = 'Your league has been imported successfully! Your commissioner is: {}'.format(commish_team)
	return render(request, 'account/dashboard.html', { 'success_msg' : msg })

def link_profile(request):
	if Manager.objects.filter(user=request.user).exists():
		msg = "Your account is already linked to a Yahoo fantasy profile"
		return render(request, 'account/dashboard.html',
			{'info_msg' : msg})

	li = League_Import(LINK_PROFILE_CALLBACK)

	request.session['request_token'] = li.get_request_token_str()

	return HttpResponseRedirect(li.get_authorization_url())

@login_required
def link_profile_callback(request):
	li = League_Import(LINK_PROFILE_CALLBACK,
		request.session['request_token'], request.GET['oauth_verifier'])

	email = request.session['email']
	password = request.session['password']

	User.objects.create_user(email, email, password)

	user = authenticate(username=email, password=password)
	login(request, user)

	manager = li.get_or_create_manager(user)

	msg = 'Profile successfully Linked: {}'.format(manager.user.email)

	return render(request, 'account/dashboard.html', {'success_msg' : msg })

@login_required
def configure_invites(request, league_id):
	league = get_object_or_404(League, pk=league_id)

	managers_to_invite = league.manager_set.filter(user=None)
	existing_managers = league.manager_set.exclude(user=None)

	return render(request, 'account/send_invitations.html', 
		{ 'managers_to_invite' : managers_to_invite,
		  'existing_managers' : existing_managers })
