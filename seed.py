import django

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'offseason.settings'

from offseason.models import MessageType, Message



django.setup()

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
msg13 = Message.objects.get_or_create(message_type=mt2, text=Message.USERNAME_TAKEN)
