import random

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
# modules needed for emailing invites
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .forms import AddRoom, EmailInvite, AcceptInvitation
from .models import Room, Invitation


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
                
                return redirect('grooveboard')
    else:

        form = AddRoom()

    return render(request, 'addroom.html', {'form': form})

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

    return render(request, 'room.html', {'room': room, 'invitations': invitations})

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
                    # erm, kind of random but just want to get it working
                    code = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz123456789') for i in range(9))
                    invitation = Invitation.objects.create(room=room, email=email, code=code)

                    messages.info(request, 'Your new Groover at: ' + email +  ' was invited')

                    send_invitation(email, code, room)

                    return redirect('room', room_id=room.id)
                else:
                    messages.info(request, 'The Groover at:' +  email + ' has already been invited')
    else:
        form = EmailInvite()

    return render(request, 'invite.html', {'room': room, 'form': form})

@login_required
def send_invitation(to_email, code, room):
    from_email = settings.DEFAULT_EMAIL_FROM
    accept_url = settings.INVITE_ACCEPT_URL

    subject = 'Invitation to use TeamGroove'
    text_content = 'Invitation to use TeamGroove service. Your code is: %s' % code
    html_content = render_to_string('email_invitation.html', {'code': code, 'room': room, 'accept_url': accept_url})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

@login_required
def send_invitation_accepted(room, invitation):
    from_email = settings.DEFAULT_EMAIL_FROM
    subject = 'Invitation accepted'
    text_content = 'Your invitation was accepted'
    html_content = render_to_string('email_accepted_invitation.html', {'room': room, 'invitation': invitation})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [room.created_by.email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

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

                messages.info(request, 'Invitation to join ' + room.title + ' accepted.')

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
