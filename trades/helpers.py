def involved_in_trade(request, trade):
	return is_proposer(request, trade) and is_receiver(request, trade)

def is_proposer(request, trade):
	return trade.team1.manager.user == request.user

def is_receiver(request, trade):
	return trade.team2.manager.user == request.user