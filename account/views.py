from django.shortcuts import render, get_object_or_404
from account.import_league import League_Import
from django.http import HttpResponseRedirect, HttpResponse
from trades.models import League, Manager, Team
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
import urllib
import uuid
import os

APP_NAME = os.environ['APP_NAME'];
IMPORT_LEAGUE_CALLBACK = 'http://{}.herokuapp.com/account/import_league_callback'.format(APP_NAME)
LINK_PROFILE_CALLBACK = 'http://{}.herokuapp.com/account/link_profile_callback'.format(APP_NAME)
LOGIN_CALLBACK = 'http://{}.herokuapp.com/account/login_callback'.format(APP_NAME)

def verify(request):
	return HttpResponse('hi');

@login_required
def dashboard(request):
	err = request.GET.get('err', None)
	info = request.GET.get('info', None)
	success = request.GET.get('success', None)

	my_teams = Team.objects.filter(manager=request.user.manager)

	return render(request, 'account/dashboard.html',
		{'table' : my_teams,
		 'error_msg' : err,
		  'info_msg' : info,
		  'success_msg' : success })

def login_user(request):
	li = League_Import(LOGIN_CALLBACK)

	request.session['request_token'] = li.get_request_token_str()

	return HttpResponseRedirect(li.get_authorization_url())

def login_callback(request):
	print 'login callback!!'
	try:
		li = League_Import(LOGIN_CALLBACK,
			request.session['request_token'], request.GET['oauth_verifier'])
	except KeyError:
		return render(request, 'account/authentication_error.html')

	request.session['access_token'] = li.get_access_token().to_string()
	guid=li.get_current_user_guid()
	try:
		manager = Manager.objects.get(yahoo_guid=guid)
		user = manager.user
		# http://stackoverflow.com/questions/2787650/manually-logging-in-a-user-without-password
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user)
	except Manager.DoesNotExist:
		password = str(uuid.uuid4())
		print 'creating user -- login: {}, password: {}'.format(guid, password)
		User.objects.create_user(guid, '', password)
		user = authenticate(username=guid, password=password)
		login(request, user)
		manager = Manager.objects.create(yahoo_guid=guid, user=user)
		manager.save()

	return HttpResponseRedirect(reverse('account:dashboard'))

@login_required
def new_league(request):
	return render(request, 'account/new_league.html')

@login_required
def import_league(request):
	league_id = request.POST['league_id']
	li = League_Import(IMPORT_LEAGUE_CALLBACK)

	request.session['league_id'] = league_id
	request.session['request_token'] = li.get_request_token_str()

	return HttpResponseRedirect(li.get_authorization_url())

@login_required
def import_league_callback(request):
	league_id=request.session['league_id']
	request_token = request.session['request_token']
	oauth_verifier = request.GET['oauth_verifier']

	li = League_Import(IMPORT_LEAGUE_CALLBACK,
		request_token, oauth_verifier)

	league_key = li.get_league_key(league_id)

	if League.objects.filter(yahoo_id=league_key).exists():
		return HttpResponseRedirect(reverse('account:dashboard') +
			'?err=' + urllib.quote_plus('That league has already been imported'))

	try:
		league = li.import_league(league_id, request.user.manager)
	except TypeError:
		if league is not None:
			league.delete()
			
		return HttpResponseRedirect(reverse('account:dashboard') +
			'?err=' + urllib.quote_plus('An error occured while importing your league. Make sure the league ID is correct and try again.'))

	return render(request, 'account/league_imported.html',
		{ 'league' : league,
		  'access_token' : li.get_access_token().to_string()})

@login_required
def fill_roster(request):
	team_id = request.POST['team_id']
	access_token = request.POST['access_token']
	team = get_object_or_404(Team, pk=team_id)

	li = League_Import.create_from_access_token(IMPORT_LEAGUE_CALLBACK, access_token)
	li.fill_roster(team)

	return HttpResponse('{ "result" : "success" }');

@login_required
def delete_league(request):
	league_id = request.POST['league_id']
	league = get_object_or_404(League, pk=league_id)

	if request.user.manager == league.commissioner:
		league.delete()
		return HttpResponseRedirect(reverse('account:dashboard') + '?success=' + urllib.quote_plus("League deleted successfully"))
	else:
		return HttpResponseRedirect(reverse('account:dashboard') + '?err=' + urllib.quote_plus("You must be the commisioner to delete a league"))
