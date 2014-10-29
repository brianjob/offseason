#from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from trades.models import League, Team, PlayerPiece, PickPiece, Trade, Player, Pick, Veto
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from offseason.models import Message
from trades.helpers import involved_in_trade, is_proposer, is_receiver
from django.db.models import Q
import yahoo.application
	
# Yahoo! OAuth Credentials - http://developer.yahoo.com/dashboard/
CONSUMER_KEY      = 'dj0yJmk9Rm11YUJIWGdTcElOJmQ9WVdrOVpYUjZkWFUyTXpRbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD01MQ--'
CONSUMER_SECRET   = '172cc969032d0d62e4312932729536fc9d149df8'
APPLICATION_ID    = 'etzuu634'
CALLBACK_URL      = 'https://intense-retreat-2626.herokuapp.com/trades/callback'

@login_required
def home(request):
	t = Team.objects.get(manager=request.user.manager)
	l = t.league
	return redirect('trades/league/%s' % l.id)



@login_required
def league(request, league_id=None, msg=''):
	if (league_id):
		l = get_object_or_404(League, pk=league_id)
	else:
		l = Team.objects.get(manager=request.user.manager).league

	t = Team.objects.filter(league=l).get(manager=request.user.manager)

	msg_id = request.GET.get('msg', False)

	if msg_id:
		msg = Message.objects.get(pk=msg_id)

	return render(request, 'trades/league.html',
								{'league' : l,
								 'proposer' : t,
								 'msg' : msg})
@login_required
def new_trade(request, team_id):
	t2 = get_object_or_404(Team, pk=team_id)
	t1 = Team.objects.filter(league=t2.league).get(manager=request.user.manager)

	t1_picks = t1.pick_set.all()
	t2_picks = t2.pick_set.all()
	t1_arms = t1.player_set.filter(position__regex=r'SP|RP')
	t1_bats = t1.player_set.filter(position__regex=r'^((?!RP|SP).)*$')
	t2_arms = t2.player_set.filter(position__regex=r'SP|RP')
	t2_bats = t2.player_set.filter(position__regex=r'^((?!RP|SP).)*$')

	return render(request, 'trades/newtrade.html',
								{'t1' : t1,
								 't2' : t2,
								 't1_arms' : t1_arms,
								 't1_bats' : t1_bats,
								 't2_arms' : t2_arms,
								 't2_bats' : t2_bats,
								 't1_picks1' : t1_picks[:len(t1_picks)//2],
								 't1_picks2' : t1_picks[len(t1_picks)//2:],
								 't2_picks1' : t2_picks[:len(t2_picks)//2],
								 't2_picks2' : t2_picks[len(t2_picks)//2:]})

@login_required
def propose_trade(request, team_id):
	players = []
	picks = []

	for key in request.POST:
		if 'player' in key:
			players.append(key.split('_')[1])
		elif 'pick' in key:
			picks.append(key.split('_')[1])
	
	if len(players) == 0 and len(picks) == 0:
		msg = Message.objects.get(text=Message.EMPTY_TRADE)
		return HttpResponseRedirect(reverse('trades:league', 
			args=(request.user.manager.team.league.id, )) 
				+ '?msg=' + str(msg.id))

	t2 = Team.objects.get(pk=team_id)

	t1 = request.user.manager.team

	if (t1.league != t2.league):
		return render(request, 'trades/tradeproposed.html', 
			{ 'error_message' : 'you cannot propose a trade to a team in a different league' })

	trade = Trade(team1=t1, team2=t2)

	trade.save()

	t1_picks = t2_picks = 0
	for pick_id in picks:
		pick = Pick.objects.get(pk=pick_id)
		if pick.team == t1:
			t1_picks += 1
		else:
			t2_picks += 1
		pp = PickPiece(trade=trade, pick=pick)
		pp.save()

	if t1_picks != t2_picks:
		trade.delete()
		msg = Message.objects.get(text=Message.UNEQUAL_PICKS)
		return HttpResponseRedirect(reverse('trades:league', 
			args=(t1.league.id, )) + '?msg=' + str(msg.id))

	for player_id in players:
		player = Player.objects.get(pk=player_id)
		pp = PlayerPiece(trade=trade, player=player)
		pp.save()

	return HttpResponseRedirect(reverse('trades:trade', args=(trade.pk,)))

@login_required
def cancel_trade(request):
	trade_id = request.POST['trade_id']
	trade = get_object_or_404(Trade, pk=trade_id)

	if is_proposer(request, trade):
		trade.delete()
		msg = Message.objects.get(text=Message.TRADE_CANCELLED)
	else:
		msg = Message.objects.get(text=Message.NOT_PROPOSER)
	return HttpResponseRedirect(reverse('trades:league',
		args=(request.user.manager.team.league.id, ))
			+ '?msg=' + str(msg.id))

@login_required
def submit_trade(request):
	trade_id = request.POST['trade_id']
	trade = get_object_or_404(Trade, pk=trade_id)

	if not is_proposer(request, trade):
		msg = Message.objects.get(text=Message.NOT_PROPOSER)
	elif trade.proposed_date is not None:
		msg = Message.objects.get(text=Message.TRADE_ALREADY_PROPOSED)
	else:
		trade.proposed_date = timezone.now()
		trade.save()
		msg = Message.objects.get(text=Message.TRADE_PROPOSED)

	return HttpResponseRedirect(reverse('trades:league', 
		args=(trade.team1.league.id, )) + '?msg=' + str(msg.id))

@login_required
def accept_trade(request):
	trade_id = request.POST['trade_id']
	trade = get_object_or_404(Trade, pk=trade_id)

	if is_receiver(request, trade):
		trade.accepted_date = timezone.now()
		trade.save()
		msg = Message.objects.get(text=Message.TRADE_ACCEPTED)
	else:
		msg = Message.objects.get(text=Message.NOT_RECEIVER)

	return HttpResponseRedirect(reverse('trades:league', 
		args=(trade.team1.league.id, )) + '?msg=' + str(msg.id))	

@login_required
def reject_trade(request):
	trade_id = request.POST['trade_id']
	trade = get_object_or_404(Trade, pk=trade_id)

	if is_receiver(request, trade):
		trade.rejected_date = timezone.now()
		trade.save()
		msg = Message.objects.get(text=Message.TRADE_REJECTED)
	else:
		msg = Message.objects.get(text=Message.NOT_RECEIVER)

	return HttpResponseRedirect(reverse('trades:league', 
		args=(trade.team1.league.id, )) + '?msg=' + str(msg.id))

def veto(request):
	trade_id = request.POST['trade_id']
	trade = get_object_or_404(Trade, pk=trade_id)

	if trade.team1.league != request.user.manager.team.league:
		msg = Message.objects.get(text=Message.CANT_VOTE)

	else:
		Veto.objects.get_or_create(trade=trade, manager=request.user.manager)
		msg = Message.objects.get(text=Message.VOTE_SUCCESS)

	return HttpResponseRedirect(reverse('trades:league', 
		args=(trade.team1.league.id, )) + '?msg=' + str(msg.id))

@login_required
def team(request, team_id=None):
	if (team_id):
		team = get_object_or_404(Team, pk=team_id)
	else:
		team = Team.objects.get(manager=request.user.manager)

	return render(request, 'trades/team.html',
							{ 'team' : team })

@login_required
def trade(request, trade_id):
	trade = get_object_or_404(Trade, pk=trade_id)

	if is_proposer(request, trade) and trade.proposed_date is None:
		# not confirmed
		template = 'trades/confirmtrade.html'
	elif is_proposer(request, trade) and trade.accepted_date is None and trade.rejected_date is None:
		# proposed but not accepted or rejected
		template = 'trades/pendingaccept.html'
	elif is_receiver(request, trade) and trade.accepted_date is None and trade.rejected_date is None:
		# proposed but not accepted or rejected
		template = 'trades/accepttrade.html'
	elif trade.accepted_date is not None and trade.completed_date is None:
		template = 'trades/vote.html'
	elif trade.completed_date is not None or involved_in_trade(request, trade):
		template = 'trades/trade.html'
	else:
		msg = Message.objects.get(text=Message.CANT_VIEW_TRADE)
		return HttpResponseRedirect(reverse('trades:league', 
			args=(trade.team1.league.id, )) + '?msg=' + str(msg.id))

	t1_players = PlayerPiece.objects.filter(player__fantasy_team = trade.team1, trade=trade)
	t1_picks = PickPiece.objects.filter(pick__team = trade.team1, trade=trade)
	t2_players = PlayerPiece.objects.filter(player__fantasy_team = trade.team2, trade=trade)
	t2_picks = PickPiece.objects.filter(pick__team = trade.team2, trade=trade)

	return render(request, template,
							{ 'trade' : trade,
							  't1_players' : t1_players,
							  't1_picks' : t1_picks,
							  't2_players' : t2_players,
							  't2_picks' : t2_picks})
@login_required
def inbox(request):
	trades = Trade.objects.filter(team2=request.user.manager.team).exclude(proposed_date=None).filter(accepted_date=None).filter(rejected_date=None)
	return render(request, 'trades/tradelist.html', { 'trades' : trades })

@login_required
def outbox(request):
	trades = Trade.objects.filter(team1=request.user.manager.team).exclude(proposed_date=None).filter(accepted_date=None).filter(rejected_date=None)
	return render(request, 'trades/tradelist.html',	{ 'trades' : trades })

@login_required
def drafts(request):
	trades = Trade.objects.filter(team1=request.user.manager.team).filter(proposed_date=None)
	return render(request, 'trades/tradelist.html', { 'trades': trades })

@login_required
def pending(request):
	trades = Trade.objects.filter(Q(team1=request.user.manager.team) | Q(team2=request.user.manager.team)).exclude(accepted_date=None).filter(completed_date=None)
	return render(request, 'trades/tradelist.html', {'trades' : trades })

@login_required
def my_trans(request):
	trades = Trade.objects.filter(Q(team1=request.user.manager.team) | Q(team2=request.user.manager.team))
	return render(request, 'trades/tradelist.html', {'trades' : trades })

@login_required
def league_trans(request):
	trades = Trade.objects.filter(team1__league=request.user.manager.team.league).exclude(completed_date=None)
	return render(request, 'trades/tradelist.html', {'trades' : trades })


def authenticate_yahoo_user(request):
	# Exchange request token for authorized access token
	oauthapp      = yahoo.application.OAuthApplication(CONSUMER_KEY, CONSUMER_SECRET, APPLICATION_ID, CALLBACK_URL)
	
	# Fetch request token
	request_token = oauthapp.get_request_token(CALLBACK_URL)
	
	# Redirect user to authorization url
	redirect_url  = oauthapp.get_authorization_url(request_token)

	return HttpResponseRedirect(redirect_url)

def callback(request):
	# Exchange request token for authorized access token
	oauthapp      = yahoo.application.OAuthApplication(CONSUMER_KEY, CONSUMER_SECRET, APPLICATION_ID, CALLBACK_URL)

	# Exchange request token for authorized access token
	verifier  = request.GET['oauth_verifier'] # must fetch oauth_verifier from request
	oauth_token = request.GET['oauth_token']

	access_token  = oauthapp.get_access_token(oauth_token, verifier)

	# update access token
	oauthapp.token = access_token

	profile = oauthapp.getProfile()

	return render(request, 'trades/debug.html', { 'profile' : profile })
