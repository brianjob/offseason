import yahoo.application
import yahoo.oauth
from django.utils import timezone
from trades.models import Player, Team, Manager, Pick, League
from django.contrib.auth.models import User
import uuid
import os
import simplejson as json

# Yahoo! OAuth Credentials - http://developer.yahoo.com/dashboard/
CONSUMER_KEY      = os.environ['CONSUMER_KEY']
CONSUMER_SECRET   = os.environ['CONSUMER_SECRET']
APPLICATION_ID    = os.environ['APPLICATION_ID']


class League_Import(object):
	def __init__(self, callback_url, request_token_str=None, verifier=None):
		self.oauthapp = yahoo.application.OAuthApplication(CONSUMER_KEY, CONSUMER_SECRET, APPLICATION_ID, callback_url)

		if request_token_str is not None and verifier is not None:
			self.request_token = yahoo.oauth.RequestToken.from_string(request_token_str)
			self.oauthapp.token  = self.oauthapp.get_access_token(self.request_token, verifier)
		else:
			self.request_token = self.oauthapp.get_request_token(callback_url)

	@classmethod
	def create_from_access_token(cls, callback_url, access_token_str):
		instance = cls(callback_url)
		instance.oauthapp.token = yahoo.oauth.AccessToken.from_string(access_token_str)
		return instance

	def get_request_token_str(self):
		return self.request_token.to_string()

	def get_authorization_url(self):
		return self.oauthapp.get_authorization_url(self.request_token)

	def get_league_key(self, league_id):
		return "{}.l.{}".format(self.run_query("select * from fantasysports.games where game_key = 'mlb'")['game']['game_key'], str(league_id))

	def get_team_key(self, league_key, team_id):
		return "{}.t.{}".format(league_key, team_id)

	def get_league_name(self, league_id):
		return self.run_query("select * from fantasysports.leagues where league_key = '{}'".format(self.get_league_key(league_id)))['league']['name']

	def get_num_picks(self, league):
		result = self.run_query(
			"select * from fantasysports.leagues.settings where league_key='{}'"
			.format(league.yahoo_id))

		tot = 0
		for pos in result['league']['settings']['roster_positions']['roster_position']:
			if (pos['position'] != 'DL' and pos['position'] != 'NA'):
				tot += int(pos['count'])

		return tot

	def fill_roster(self, team):
		if team.yahoo_id is None:
			raise Exception('Roster cannot be auto filled with a null team yahoo id')
		if team.league.yahoo_id is None:
			raise Exception('Roster cannot be auto filled with a null league yahoo id')

		team_key = self.get_team_key(team.league.yahoo_id, team.yahoo_id)
		date = timezone.now()
		if date.month < 4:
			date = date.replace(month=10)
			date = date.replace(year = date.year - 1)
		elif date.month > 10:
			date = date.replace(month=10)

		date_str = date.strftime("%Y-%m-%d")

		result = None
		counter = 0
		while(result is None and counter < 10):
			result = self.run_query(
				"select * from fantasysports.teams.roster where team_key='{}' and date='{}'"
				.format(team_key, date_str)
			)
			counter += 1

		if result is None:
			raise Exception("could not fetch roster for {}".format(team.name))

		team_result = result['team']

		#remove all players from team first so no duplicates
		for player in team.player_set.all():
			player.delete()

		for player in team_result['roster']['players']['player']:
			p = Player(
				name=player['name']['full'],
				position=player['display_position'].upper(),
				real_team=player['editorial_team_abbr'].upper(),
				fantasy_team=team
			)

			p.save()


	def fill_league(self, league):
		if league.yahoo_id is None:
			raise Exception('League cannot be auto filled with a null league yahoo id')

		league_key = league.yahoo_id
		league_result = self.run_query(
			"select * from fantasysports.teams where league_key = '{}'"
			.format(league_key)
		)

		num_picks = self.get_num_picks(league)

		for team in league_result['team']:
			guid = team['managers']['manager']['guid']

			try:
				manager = Manager.objects.get(yahoo_guid=guid)
				if 'email' in team['managers']['manager'] and manager.user.email == '':
					manager.user.email = team['managers']['manager']['email']
					manager.save()
			except Manager.DoesNotExist:
				try:
					email = team['managers']['manager']['email']
					username = email
				except KeyError:
					email = ''
					username = guid

					# give the user a random unique pw and they can change it later
					user = User.objects.create_user(username, email, uuid.uuid4())
					manager = Manager(yahoo_guid=guid, user=user)
					manager.save()
			
			try:
				t = Team.objects.filter(league=league).get(yahoo_id=team['team_id'])
				t.name = team['name']

			except Team.DoesNotExist:
				t = Team(
					name=team['name'],
					league=league,
					yahoo_id=team['team_id'],
					manager=manager
				)

				print 'creating team: {}'.format(t.name)

			t.save()

			if team['managers']['manager'].has_key('is_commissioner') and team['managers']['manager']['is_commissioner'] == "1":
				league.commissioner = manager
				league.save()

			if not league.is_auction_draft: # picks are only applicable to a non auction league
				self.pop_initial_picks(num_picks, t)

	def import_league(self, league_id, commissioner):
		league_key = self.get_league_key(league_id)

		result = self.run_query(
			"select * from fantasysports.leagues where league_key='{}'"
			.format(league_key)
		)

		settings = self.run_query(
			"select * from fantasysports.leagues.settings where league_key='{}'"
			.format(league_key)
		)

		league = League(
			name=result['league']['name'],
			yahoo_id=result['league']['league_key'],
			commissioner=commissioner,
			num_teams=result['league']['num_teams'],
			url=result['league']['url'],
			trade_reject_time=settings['league']['settings']['trade_reject_time'],
			can_trade_picks=settings['league']['settings']['can_trade_draft_picks'] == '1',
			scoring_type=settings['league']['settings']['scoring_type'],
			is_auction_draft=settings['league']['settings']['is_auction_draft'] == '1'
		)

		print 'creating league: {}'.format(league.name)
		print 'access token: {}'.format(self.get_access_token().to_string())
		league.save()

		self.fill_league(league)

		if not league.is_auction_draft: # picks only applicable to non auction leagues
			self.run_pick_transactions(league)

		return league

	def pop_initial_picks(self, num_picks, team):
		today = timezone.now()
		if today.month > 3:
			year = today.year + 1
		else:
			year = today.year

		for i in range(1, num_picks + 1):
			pick = Pick(round=i, year=year, team=team)
			pick.save()

	def run_pick_transactions(self, league):
		result = self.run_query(
			"select * from fantasysports.leagues.transactions where league_key='{}'"
			.format(league.yahoo_id)
		)

		for transaction in result['league']['transactions']['transaction']:
			if transaction['type'] == 'trade' and transaction['status'] == 'successful' and 'picks' in transaction:
				for pick in transaction['picks']['pick']:
					src_id = pick['source_team_key'].split('.t.')[1]
					dest_id = pick['destination_team_key'].split('.t.')[1]

					src_team = league.team_set.get(yahoo_id=src_id)
					dest_team = league.team_set.get(yahoo_id=dest_id)

					pick = src_team.pick_set.filter(round=int(pick['round']))[0]
					pick.team = dest_team;
					pick.save()

	def get_current_user_guid(self):
		return self.oauthapp.token.yahoo_guid

	def run_query(self, query):
		if self.oauthapp.token is None:
			raise Exception('access token not generated')

		print 'running: ' + query

		response = self.oauthapp.yql(query)

		print 'response: ' + json.dumps(response)

		if 'query' in response and 'results' in response['query']:
			return response['query']['results']
		elif 'error' in response:
			raise Exception('YQL query failed with error: "%s".' % response['error']['description'])
		else:
			raise Exception('YQL response malformed.')

	def get_access_token(self):
		return self.oauthapp.token
