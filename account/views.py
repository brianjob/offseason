from django.shortcuts import render, get_object_or_404
from account.import_league import League_Import
from django.http import HttpResponseRedirect, HttpResponse
from trades.models import League, Manager, Team
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
import uuid

IMPORT_LEAGUE_CALLBACK = 'http://offseason-trade.herokuapp.com/account/import_league_callback'
LINK_PROFILE_CALLBACK = 'http://offseason-trade.herokuapp.com/account/link_profile_callback'
LOGIN_CALLBACK = 'http://offseason-trade.herokuapp.com/account/login_callback'

def verify(request):
	return HttpResponse('hi');

@login_required
def dashboard(request):
	err = request.GET.get('err', None)
	info = request.GET.get('info', None)
	success = request.GET.get('success', None)

	return render(request, 'account/dashboard.html',
		{ 'error_msg' : err,
		  'info_msg' : info,
		  'success_msg' : success })

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
			'?err=' + urlencode('That league has already been imported'))

	league = li.import_league(league_id, request.user.manager)

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
