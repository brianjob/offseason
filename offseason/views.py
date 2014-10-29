from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from offseason.models import Message
from django.contrib.auth.decorators import login_required

@login_required
def password_change_done(request):
	msg = Message.objects.get(text=Message.PASSWORD_CHANGED)
	return HttpResponseRedirect(reverse('trades:league',
		args=(request.user.manager.team.league.id, ))
	+ '?msg=' + str(msg.id))