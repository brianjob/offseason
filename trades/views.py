#from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from trades.models import League, Team, PlayerPiece, PickPiece, Trade, Player, Pick, Veto
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from offseason.models import Message
from trades.helpers import involved_in_trade, is_proposer, is_receiver
from django.db.models import Q

REVIEW_PERIOD = 3

@login_required
def league(request, league_id, msg=''):
	l = get_object_or_404(League, pk=league_id)

	t = Team.objects.filter(league=l).get(manager=request.user.manager)

	complete_trades(l)

	pending_trades = Trade.objects.filter(team1__league=l).exclude(accepted_date=None).filter(completed_date=None)

	msg_id = request.GET.get('msg', False)

	if msg_id:
		msg = Message.objects.get(pk=msg_id)

	return render(request, 'trades/league.html',
								{'league' : l,
								 'pending_trades' : pending_trades,
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

	t2 = Team.objects.get(pk=team_id)

	if len(players) == 0 and len(picks) == 0:
		msg = Message.objects.get(text=Message.EMPTY_TRADE)
		return HttpResponseRedirect(reverse('trades:league', 
			args=(t2.league.id, )) + '?msg=' + str(msg.id))

	t1 = request.user.manager.teams_managed.get(league=t2.league)
	if t1 is None:
		t1 = request.user.manager.teams_comanaged.get(league=t2.league)

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
		args=(trade.team1.league.id, )) + '?msg=' + str(msg.id))

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

	if trade.team1.league not in [t.league for t in request.user.manager.team_set.all()]:
		msg = Message.objects.get(text=Message.CANT_VOTE)

	else:
		Veto.objects.get_or_create(trade=trade, manager=request.user.manager)
		msg = Message.objects.get(text=Message.VOTE_SUCCESS)

	return HttpResponseRedirect(reverse('trades:league', 
		args=(trade.team1.league.id, )) + '?msg=' + str(msg.id))

@login_required
def team(request, team_id):
	team = get_object_or_404(Team, pk=team_id)
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
	trades = Trade.objects.filter(team2__in=request.user.manager.team_set.all()).exclude(proposed_date=None).filter(accepted_date=None).filter(rejected_date=None)
	return render(request, 'trades/tradelist.html', 
		{ 'heading' : 'Inbox',
		  'trades' : trades })

@login_required
def outbox(request):
	trades = Trade.objects.filter(team1__in=request.user.manager.team_set.all()).exclude(proposed_date=None).filter(accepted_date=None).filter(rejected_date=None)
	return render(request, 'trades/tradelist.html',	
		{ 'heading' : 'Outbox',
		  'trades' : trades })

@login_required
def drafts(request):
	trades = Trade.objects.filter(team1__in=request.user.manager.team_set.all()).filter(proposed_date=None)
	return render(request, 'trades/tradelist.html', 
		{ 'heading' : 'Drafts',
		  'trades': trades })

@login_required
def pending(request):
	trades = Trade.objects.filter(Q(team1__in=request.user.manager.team_set.all()) | Q(team2__in=request.user.manager.team_set.all())).exclude(accepted_date=None).filter(completed_date=None)
	return render(request, 'trades/tradelist.html', 
		{ 'heading' : 'My Pending Transactions',
		 'trades' : trades })

@login_required
def my_trans(request):
	trades = Trade.objects.filter(Q(team1__in=request.user.manager.team_set.all()) | Q(team2__in=request.user.manager.team_set.all()))
	return render(request, 'trades/tradelist.html', 
		{ 'heading' : 'My Transactions',
		 'trades' : trades })

@login_required
def league_trans(request):
	trades = Trade.objects.filter(team1__league__in=[t.league for t in request.user.manager.team_set.all()]).exclude(completed_date=None)
	return render(request, 'trades/tradelist.html', 
		{ 'heading' : 'All Transactions',
		 'trades' : trades })

def complete_trades(league):
	# Here is where we are doing the completions for now
	# This should eventually be moved to a background proc but
	# those cost money with heroku
	max_accept_date = timezone.now() - timedelta(days=REVIEW_PERIOD)
	mark_for_completion = Trade.objects.filter(team1__league=league).exclude(accepted_date=None).filter(completed_date=None).filter(accepted_date__lte=max_accept_date)
	for trade in mark_for_completion:
		if trade.vetoed():
			trade.vetoed_date = timezone.now()
		else:
			trade.completed_date = timezone.now()

			# SWAP PLAYERS / PICKS

		trade.save()