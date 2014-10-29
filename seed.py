import django
from trades.models import League, Manager, Team, Player, Pick
from offseason.models import MessageType, Message
from django.contrib.auth.models import User

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'offseason.settings'

django.setup()

u1 = User.objects.get(pk=1)
u2, c = User.objects.get_or_create(username='dzemaitis')
u2.set_password('password')
u2.save()
u3, c = User.objects.get_or_create(username='bashin')
u3.set_password('password')
u3.save()

league, c = League.objects.get_or_create(name='Detroit Diamonds VII', yahoo_id='5940')

m1, c = Manager.objects.get_or_create(user=u1, yahoo_id='LKNRSYGJEFBCVCKO7RDN4MHLS4')
m2, c = Manager.objects.get_or_create(user=u2, yahoo_id='')
m3, c = Manager.objects.get_or_create(user=u3, yahoo_id='')

t1, c = Team.objects.get_or_create(yahoo_id='10', name='H to the Rizzo', manager=m1, league=league)
t2, c = Team.objects.get_or_create(yahoo_id='1', name='El Oso Blanco', manager=m2, league=league)
t3, c = Team.objects.get_or_create(yahoo_id='3', name="Cano's Huge Wallet", manager=m3, league=league)

t1.save()
t2.save()
t3.save()

p1 = [
	Player.objects.get_or_create(name='Anthony Rizzo',
		position='1B', real_team='CHC', fantasy_team=t1),
	Player.objects.get_or_create(name='Jose Altuve',
		position='2B', real_team='HOU', fantasy_team=t1),
	Player.objects.get_or_create(name='Bryce Harper',
		position='OF', real_team='WAS', fantasy_team=t1),
	Player.objects.get_or_create(name='Jose Fernandez',
		position='SP', real_team='FLA', fantasy_team=t1),
	Player.objects.get_or_create(name='Wade Davis',
		position='SP/RP', real_team='KC', fantasy_team=t1)
]

p2 = [
	Player.objects.get_or_create(name='Miguel Cabrera', 
		position='1B/3B', real_team='DET', fantasy_team=t2),
	Player.objects.get_or_create(name='Mike Trout', 
		position='OF', real_team='LAA', fantasy_team=t2),
	Player.objects.get_or_create(name='Felix Hernandez',
		position='SP', real_team='SEA', fantasy_team=t2),
	Player.objects.get_or_create(name='Johnny Cueto',
		position='SP', real_team='CIN', fantasy_team=t2),
	Player.objects.get_or_create(name='Andrew Cashner',
		position='SP', real_team='SD', fantasy_team=t2),
	Player.objects.get_or_create(name='Greg Holland',
		position='RP', real_team='KC', fantasy_team=t2)
]

for i in range(1, 22):
	Pick.objects.get_or_create(year=2015, round=i, team=t1)
	Pick.objects.get_or_create(year=2015, round=i, team=t2)
	Pick.objects.get_or_create(year=2015, round=i, team=t3)


mt1, c = MessageType.objects.get_or_create(code = 'SUCCESS', bootstrap_class='success')
mt2, c = MessageType.objects.get_or_create(code = 'ERROR', bootstrap_class='danger')
mt3, c = MessageType.objects.get_or_create(code = 'WARNING', bootstrap_class='warning')

msg1 = Message.objects.get_or_create(message_type=mt1, text=Message.TRADE_PROPOSED)
msg2 = Message.objects.get_or_create(message_type=mt3, text=Message.TRADE_ALREADY_PROPOSED)
msg3 = Message.objects.get_or_create(message_type=mt2, text=Message.NOT_INVOLVED)
msg4 = Message.objects.get_or_create(message_type=mt1, text=Message.TRADE_CANCELLED)
msg5 = Message.objects.get_or_create(message_type=mt2, text=Message.NOT_PROPOSER)
msg6 = Message.objects.get_or_create(message_type=mt1, text=Message.TRADE_ACCEPTED)
mst7 = Message.objects.get_or_create(message_type=mt1, text=Message.TRADE_REJECTED)
msg7 = Message.objects.get_or_create(message_type=mt2, text=Message.CANT_VIEW_TRADE)
msg8 = Message.objects.get_or_create(message_type=mt2, text=Message.CANT_VOTE)
msg9 = Message.objects.get_or_create(message_type=mt1, text=Message.VOTE_SUCCESS)
msg10 = Message.objects.get_or_create(message_type=mt2, text=Message.UNEQUAL_PICKS)
msg11 = Message.objects.get_or_create(message_type=mt2, text=Message.EMPTY_TRADE)
msg12 = Message.objects.get_or_create(message_type=mt1, text=Message.PASSWORD_CHANGED)
