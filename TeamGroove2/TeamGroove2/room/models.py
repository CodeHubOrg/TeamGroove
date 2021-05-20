from django.db import models

from users.models import CustomUser

class Room(models.Model):
    # Room status
    ACTIVE = 'active'
    DELETED = 'deleted'

    CHOICES_STATUS = (
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted')
    )    

    title = models.CharField(max_length=255)
    members = models.ManyToManyField(CustomUser, related_name='rooms')
    created_by = models.ForeignKey(CustomUser, related_name='created_rooms', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=CHOICES_STATUS, default=ACTIVE)
    
    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Invitation(models.Model):

    INVITED = 'invited'
    ACCEPTED = 'accepted'

    CHOICES_STATUS = (
        (INVITED, 'Invited'),
        (ACCEPTED, 'Accepted')
    )

    room = models.ForeignKey(Room, related_name='invitations', on_delete=models.CASCADE)
    email = models.EmailField()
    # Need to generate some sort of random code so we can authenticate who got the invite
    invitation_code = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=CHOICES_STATUS, default=INVITED)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
