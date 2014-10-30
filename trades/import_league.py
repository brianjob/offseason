import yahoo.application
import yahoo.oauth
	
# Yahoo! OAuth Credentials - http://developer.yahoo.com/dashboard/
CONSUMER_KEY      = 'dj0yJmk9Rm11YUJIWGdTcElOJmQ9WVdrOVpYUjZkWFUyTXpRbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD01MQ--'
CONSUMER_SECRET   = '172cc969032d0d62e4312932729536fc9d149df8'
APPLICATION_ID    = 'etzuu634'
CALLBACK_URL      = 'http://intense-retreat-2626.herokuapp.com/trades/callback'


class League_Import(object):
	def __init__(self, request_token_str=None, verifier=None):
		self.oauthapp = yahoo.application.OAuthApplication(CONSUMER_KEY, CONSUMER_SECRET, APPLICATION_ID, CALLBACK_URL)

		print str(request_token_str) + ' - ' + str(verifier) + ' - '

		if request_token_str is not None and verifier is not None:
			print 'non null'
			self.request_token = yahoo.oauth.RequestToken.from_string(request_token_str)
			self.oauthapp.token  = self.oauthapp.get_access_token(self.request_token, verifier)
		else:
			self.request_token = self.oauthapp.get_request_token(CALLBACK_URL)
			print 'null'

	def get_request_token_str(self):
		return self.oauthapp.get_request_token(CALLBACK_URL).to_string()

	def get_authorization_url(self):
		return self.oauthapp.get_authorization_url(self.request_token)

	def get_league_key(self, league_id):
		return self.run_query("select * from fantasysports.games where game_key = 'mlb'")['game_key'] + 'l' + str(league_id)

	def get_league_name(self, league_id):
		return self.run_query("select * from fantasysports.leagues where league_key = '%s'" % self.get_league_key(league_id))['league']['name']

	def run_query(self, query):
		if self.oauthapp.token is None:
			raise Exception('access token not generated')

		response = self.oauthapp.yql(query)

		if 'query' in response and 'results' in response['query']:
			return response['query']['results']
		elif 'error' in response:
			raise Exception('YQL query failed with error: "%s".' % response['error']['description'])
		else:
			raise Exception('YQL response malformed.')
