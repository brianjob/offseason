import yahoo.application
import yahoo.oauth
from django.utils import timezone
from trades.models import Player, Team
	
# Yahoo! OAuth Credentials - http://developer.yahoo.com/dashboard/
CONSUMER_KEY      = 'dj0yJmk9Rm11YUJIWGdTcElOJmQ9WVdrOVpYUjZkWFUyTXpRbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD01MQ--'
CONSUMER_SECRET   = '172cc969032d0d62e4312932729536fc9d149df8'
APPLICATION_ID    = 'etzuu634'
CALLBACK_URL      = 'http://intense-retreat-2626.herokuapp.com/trades/callback'


class League_Import(object):
	def __init__(self, request_token_str=None, verifier=None):
		self.oauthapp = yahoo.application.OAuthApplication(CONSUMER_KEY, CONSUMER_SECRET, APPLICATION_ID, CALLBACK_URL)

		if request_token_str is not None and verifier is not None:
			self.request_token = yahoo.oauth.RequestToken.from_string(request_token_str)
			self.oauthapp.token  = self.oauthapp.get_access_token(self.request_token, verifier)
		else:
			self.request_token = self.oauthapp.get_request_token(CALLBACK_URL)

	def get_request_token_str(self):
		return self.request_token.to_string()

	def get_authorization_url(self):
		return self.oauthapp.get_authorization_url(self.request_token)

	def get_league_key(self, league_id):
		return "{}.l.{}".format(self.run_query("select * from fantasysports.games where game_key = 'mlb'")['game']['game_key'], str(league_id))

	def get_team_key(self, league_id, team_id):
		return "{}.t.{}".format(self.get_league_key(league_id), team_id)

	def get_league_name(self, league_id):
		return self.run_query("select * from fantasysports.leagues where league_key = '{}'".format(self.get_league_key(league_id)))['league']['name']

	def fill_roster(self, team):
		if team.yahoo_id is None:
			raise Exception('Roster cannot be auto filled with a null team yahoo id')
		if team.league.yahoo_id is None:
			raise Exception('Roster cannot be auto filled with a null league yahoo id')

		team_key = self.get_team_key(team.league.yahoo_id, team.yahoo_id)
		team_result = self.run_query(
			"select * from fantasysports.teams.roster where team_key='{}' and date='{}'"
			.format(team_key, timezone.now().strftime("%Y-%m-%d"))
		)['team']

		for player in team_result['players']:
			p = Player(
				name=player['name']['full'],
				position=player['display_position'].upper(),
				real_team=player['editorial_team_abbr'].upper(),
				fantasy_team=team
			)

			p.save()

	# def fill_league(self, league):
	# 	if league.yahoo_id is None:
	# 		raise Exception('League cannot be auto filled with a null league yahoo id')

	# 	league_key = self.get_league_key(league.yahoo_id)

	# 	league_result = self.run_query(
	# 		"select * from fantasysports.teams where league_key = '{}'"
	# 		.format(league_key)
	# 	)

	# 	for team in league_result:
	# 		t = Team(
	# 			name=team['name'],
	# 			league=league,
	# 			yahoo_id=team['team_id'],
	# 			manager=
	# 		)

	def run_query(self, query):
		if self.oauthapp.token is None:
			raise Exception('access token not generated')

		print 'running: ' + query

		response = self.oauthapp.yql(query)

		if 'query' in response and 'results' in response['query']:
			return response['query']['results']
		elif 'error' in response:
			raise Exception('YQL query failed with error: "%s".' % response['error']['description'])
		else:
			raise Exception('YQL response malformed.')
