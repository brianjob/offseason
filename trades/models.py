from django.db import models
from django.contrib.auth.models import User
from itertools import chain

class Manager(models.Model):
	yahoo_guid = models.CharField(max_length=200)
	user = models.OneToOneField(User)

	def teams(self):
		return list(chain(self.teams_managed.all(), self.teams_comanaged.all()))

	def __unicode__(self):
		return self.user.username

class League(models.Model):
	name = models.CharField(max_length=200)
	yahoo_id = models.CharField(max_length=200)
	commissioner = models.ForeignKey(Manager)
	num_teams = models.IntegerField()
	url = models.CharField(max_length=250)
	trade_reject_time = models.IntegerField()
	can_trade_picks = models.BooleanField()
	scoring_type = models.CharField(max_length=50)
	is_auction_draft = models.BooleanField()

	def __unicode__(self):
		return self.name

	def pending_trans_cnt(self):
		return Trade.objects.filter(team1__league=self).exclude(accepted_date=None).filter(completed_date=None).count()


class Team(models.Model):
	name = models.CharField(max_length=50)
	league = models.ForeignKey(League)
	yahoo_id = models.CharField(max_length=200)
	manager = models.ForeignKey(Manager)

	def inbox(self):
		return self.trades_received.filter(rejected_date=None).filter(accepted_date=None)

	def outbox(self):
		return self.trades_proposed.filter(rejected_date=None).filter(accepted_date=None)

	def team_key(self):
		return "{}.t.{}".format(self.league.yahoo_id, self.yahoo_id)

	def __unicode__(self):
		return self.name

class Player(models.Model):
	name = models.CharField(max_length=200)
	position = models.CharField(max_length=25)
	real_team = models.CharField(max_length=25)
	fantasy_team = models.ForeignKey(Team)

	def __unicode__(self):
		return self.name

class Pick(models.Model):
	round = models.IntegerField()
	year = models.IntegerField()
	team = models.ForeignKey(Team)

	def __unicode__(self):
		return str(self.round)

class Trade(models.Model):
	team1 = models.ForeignKey(Team, related_name='trades_proposed')
	team2 = models.ForeignKey(Team, related_name='trades_received')
	proposed_date = models.DateTimeField('date proposed', null = True)
	accepted_date = models.DateTimeField('date accepted', null = True)
	rejected_date = models.DateTimeField('date rejected', null = True)
	completed_date = models.DateTimeField('date completed', null = True)
	vetoed_date = models.DateTimeField('date vetoed', null = True)

	def vetoed(self):
		votes_against = len(self.veto_set.all())
		num_teams = len(self.team1.league.team_set.all())

		return votes_against > num_teams / 2

	def __unicode__(self):
		return self.team1.name + ', ' + self.team2.name + ' - ' + self.proposed_date.strftime('%m/%d/%Y')

class Veto(models.Model):
	trade = models.ForeignKey(Trade)
	manager = models.ForeignKey(Manager)

	def __unicode__(self):
		return str(self.manager) + ': ' + str(self.trade)

class PlayerPiece(models.Model):
	trade = models.ForeignKey(Trade)
	player = models.ForeignKey(Player)

	def __unicode__(self):
		return self.player.name

class PickPiece(models.Model):
	trade = models.ForeignKey(Trade)
	pick = models.ForeignKey(Pick)

	def __unicode__(self):
		return self.pick.round
