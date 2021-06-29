import random

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages

from .forms import AddRoom, EmailInvite, AcceptInvitation, EditRoom
from .models import Room, Invitation
from spotify.models import Playlist
from .email_utils import send_invitation, send_invitation_accepted


@login_required
def add_room(request):
    if request.method == 'POST':
            form = AddRoom(request.POST)

            if form.is_valid():
                title = request.POST.get('title')                
                room = Room.objects.create(title=title, created_by=request.user)
                room.members.add(request.user)
                room.save()                             
                request.user.active_room_id = room.id
                # This would probably be a good place to get authorization
                # from Spotify - code, token, refresh token. Or do it later on?
                return redirect('grooveboard')
    else:

        form = AddRoom()

    return render(request, 'add_room.html', {'form': form})

@login_required
def activate_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id, status=Room.ACTIVE, members__in=[request.user])    
    request.user.active_room_id = room.id
    request.user.save()

    messages.info(request, "Your room was activated.")

    return redirect('room', room_id=room.id)

@login_required
def room(request, room_id):
    room = get_object_or_404(Room, pk=room_id, status=Room.ACTIVE, members__in=[request.user])
    invitations = room.invitations.filter(status=Invitation.INVITED)

    playlists = room.playlists.filter(room=room_id)
    
    return render(request, 'room.html', {'room': room, 'invitations': invitations, 'playlists': playlists})

@login_required
def invite(request):
    room = get_object_or_404(Room, pk=request.user.active_room_id, status=Room.ACTIVE)

    if request.method == 'POST':
        form = EmailInvite(request.POST)

        if form.is_valid():            
            email = request.POST.get('email')
            
            if email:
                invitations = Invitation.objects.filter(room=room, email=email)
                
                if not invitations:
                    code = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz123456789') for i in range(9))
                    invitation = Invitation.objects.create(room=room, email=email, invitation_code=code)

                    messages.info(request, f'Your new Groover at: {email} was invited.')
                    
                    send_invitation(email, code, room)

                    return redirect('room', room_id=room.id)
                else:
                    messages.info(request, f'The Groover at: {email} has already been invited.')
                    
    else:
        form = EmailInvite()

    return render(request, 'invite.html', {'room': room, 'form': form})

@login_required
def accept_invitation(request):
    if request.method == 'POST':
        form = AcceptInvitation(request.POST)

        if form.is_valid():
            code = request.POST.get('code')

            invitations = Invitation.objects.filter(code=code, email=request.user.email)

            if invitations:
                invitation = invitations[0]
                invitation.status = Invitation.ACCEPTED
                invitation.save()

                room = invitation.room
                room.members.add(request.user)
                room.save()                
                request.user.active_team_id = room.id
                request.user.save()

                messages.info(request, f'Invitation to join {room.title} accepted.')
                send_invitation_accepted(room, invitation)
                
                return redirect('grooveboard')

            else:
                messages.info(request, 'Invitation not found.')
        else:
            form = AcceptInvitation()
            return render(request, 'accept_invitation.html', {'form': form})
    else:
        form = AcceptInvitation()
    return render(request, 'accept_invitation.html', {'form': form})

@login_required
def edit_room(request):
    room = get_object_or_404(Room, pk=request.user.active_room_id, status=Room.ACTIVE, members__in=[request.user])

    if request.method == 'POST':
        form = EditRoom(request.POST)

        if form.is_valid():
            title = request.POST.get('title')

            if title:
                room.title = title
                room.save()
                messages.info(request, "Your changes were saved.")

                return redirect('room', room_id=room.id)
    else:
        form = EditRoom()
    return render(request, 'edit_room.html', {'form': form})

@login_required
def delete_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id, created_by=request.user)
    room.delete()
    
    messages.info(request, "Your room was deleted.")

    return redirect('grooveboard')