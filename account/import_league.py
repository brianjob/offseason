import yahoo.application
import yahoo.oauth
from django.utils import timezone
from trades.models import Player, Team, Manager, Pick, League
from django.contrib.auth.models import User
import uuid
	
# Yahoo! OAuth Credentials - http://developer.yahoo.com/dashboard/
CONSUMER_KEY      = 'dj0yJmk9NWdNVWRYWngwaUF5JmQ9WVdrOU1HcFpjRGt6Tm5VbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1iZA--'
CONSUMER_SECRET   = '2cc6e94d26c4a943ce7c13a47deb65f4b73f5e02'
APPLICATION_ID    = '0jYp936u'


class League_Import(object):
	def __init__(self, callback_url=None, request_token_str=None, verifier=None):
		self.oauthapp = yahoo.application.OAuthApplication(CONSUMER_KEY, CONSUMER_SECRET, APPLICATION_ID, callback_url)

		if request_token_str is not None and verifier is not None:
			self.request_token = yahoo.oauth.RequestToken.from_string(request_token_str)
			self.oauthapp.token  = self.oauthapp.get_access_token(self.request_token, verifier)
		elif callback_url is not None:
			self.request_token = self.oauthapp.get_request_token(callback_url)

	@classmethod
	def create_from_access_token(cls, access_token):
		instance = cls('')
		instance.oauthapp.token = access_token
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

		for team in league_result['team']:
			guid = team['managers']['manager']['guid']

			try:
				manager = Manager.objects.get(yahoo_guid=guid)
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
			#self.fill_roster(t)

			if team['managers']['manager'].has_key('is_commissioner') and team['managers']['manager']['is_commissioner'] == "1":
				league.commissioner = manager
				league.save()

	def import_league(self, league_id, commissioner):

		result = self.run_query(
			"select * from fantasysports.leagues where league_key='{}'"
			.format(self.get_league_key(league_id))
		)

		league = League(
			name=result['league']['name'],
			yahoo_id=result['league']['league_key'],
			commissioner=commissioner
		)

		print 'creating league: {}'.format(league.name)
		league.save()

		self.fill_league(league)

		return league

	def add_picks(self, team, year):
		for rd in range(1, 23):
			pick = Pick(round=rd, year=year, team=team)
			pick.save()

	def get_current_user_guid(self):
		return self.oauthapp.token.yahoo_guid

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

	def get_access_token(self):
		return self.oauthapp.token

def import_worker(callback, request_token, oauth_verifier, league_id, manager):
	li = League_Import(callback, request_token, oauth_verifier)
	li.import_league(league_id, manager)
