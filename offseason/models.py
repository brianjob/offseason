from django.db import models

class MessageType(models.Model):
	code = models.CharField(max_length=20)
	bootstrap_class = models.CharField(max_length=20)

	def __unicode__(self):
		return self.code

class Message(models.Model):
	message_type = models.ForeignKey(MessageType)
	text = models.CharField(max_length=1000)

	TRADE_PROPOSED = "Trade proposed successfully"
	TRADE_ALREADY_PROPOSED = "Trade already proposed"
	NOT_INVOLVED = "You are not involved with that trade"
	TRADE_CANCELLED = "Trade successfully cancelled"
	NOT_PROPOSER = "You are not the proposer of that trade"
	TRADE_ACCEPTED = "Trade accepted"
	TRADE_REJECTED = "Trade rejected"
	CANT_VIEW_TRADE = "You are not allowed to view that trade"
	CANT_VOTE = "You are not allowed to vote on that trade"
	VOTE_SUCCESS = "You have successfully voted on this trade"
	UNEQUAL_PICKS = "Trades cannot involve an unequal number of picks"
	EMPTY_TRADE = "Trades cannot be empty"
	PASSWORD_CHANGED = "Your password has been successfully changed"
	USERNAME_TAKEN = "That username is already taken. Try again, bruh."

	def __unicode__(self):
		return self.text