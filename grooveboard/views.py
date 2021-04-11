from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from room.models import Room, Invitation

@login_required
def grooveboard(request):
    rooms = request.user.rooms.exclude(pk=request.user.active_room_id)
    invitations = Invitation.objects.filter(email=request.user.email, status=Invitation.INVITED)

    if invitations:
        return redirect('accept_invitation')
    else:
        return render(request, 'grooveboard.html', {'rooms': rooms, 'invitations': invitations})
