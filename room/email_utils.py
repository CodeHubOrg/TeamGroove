from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_invitation(to_email, code, room):
    from_email = settings.DEFAULT_EMAIL_FROM
    accept_url = settings.INVITE_ACCEPT_URL
    
    subject = 'Invitation to use TeamGroove'
    text_content = f'Invitation to use TeamGroove service. Your code is: {code}' 
    html_content = render_to_string('email_invitation.html', {'invitation_code': code, 'room': room, 'accept_url': accept_url})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_invitation_accepted(room, invitation):
    from_email = settings.DEFAULT_EMAIL_FROM
    subject = 'Invitation accepted'
    text_content = 'Your invitation was accepted'
    html_content = render_to_string('email_accepted_invitation.html', {'room': room, 'invitation': invitation})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [room.created_by.email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()