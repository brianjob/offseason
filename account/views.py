from django.shortcuts import render, get_object_or_404
from account.import_league import League_Import, import_worker
from django.http import HttpResponseRedirect, HttpResponse
from trades.models import League, Manager, Team
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
import uuid
from rq import Queue
from worker import conn

IMPORT_LEAGUE_CALLBACK = 'http://offseason-trade.herokuapp.com/account/import_league_callback'
LINK_PROFILE_CALLBACK = 'http://offseason-trade.herokuapp.com/account/link_profile_callback'
LOGIN_CALLBACK = 'http://offseason-trade.herokuapp.com/account/login_callback'

def verify(request):
	return HttpResponse('hi');

@login_required
def dashboard(request):
	return render(request, 'account/dashboard.html')

def login_user(request):
	li = League_Import(LOGIN_CALLBACK)

	request.session['request_token'] = li.get_request_token_str()

	return HttpResponseRedirect(li.get_authorization_url())

def login_callback(request):
	print 'login callback!!'
	li = League_Import(LOGIN_CALLBACK,
		request.session['request_token'], request.GET['oauth_verifier'])

	guid=li.get_current_user_guid()
	try:
		manager = Manager.objects.get(yahoo_guid=guid)
		user = authenticate(username=manager.user.username, password=manager.user.password)
		login(request, user)
	except Manager.DoesNotExist:
		password = str(uuid.uuid4())
		print 'creating user -- login: {}, password: {}'.format(guid, password)
		User.objects.create_user(guid, '', password)
		user = authenticate(username=guid, password=password)
		login(request, user)
		manager = Manager.objects.create(yahoo_guid=guid, user=user)
		manager.save()

	return HttpResponse(reverse('account:dashboard'))

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
	request_token = request.session['request_token']
	oauth_verifier = request.GET['oauth_verifier']

	import_worker(IMPORT_LEAGUE_CALLBACK, request_token, oauth_verifier, league_id, request.user.manager)
	li = League_Import(IMPORT_LEAGUE_CALLBACK,
		request_token, oauth_verifier)
	league = li.import_league(league_id, request.user.manager)

	return render(request, 'account/league_imported.html',
		{ 'league' : league,
		  'access_token' : li.get_access_token()})

@login_required
def fill_roster(request):
	team_id = request.POST['team_id']
	access_token = request.POST['access_token']
	team = get_object_or_404(Team, pk=team_id)

	li = League_Import.create_from_access_token(access_token)
	li.fill_roster(team)

	return HttpResponse("{ result : 'success' }");

@login_required
def configure_invites(request, league_id):
	league = get_object_or_404(League, pk=league_id)

	managers_to_invite = league.manager_set.filter(user=None)
	existing_managers = league.manager_set.exclude(user=None)

	return render(request, 'account/send_invitations.html', 
		{ 'managers_to_invite' : managers_to_invite,
		  'existing_managers' : existing_managers })
