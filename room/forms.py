from django import forms

from .models import Room

class AddRoom(forms.ModelForm):
    title = forms.CharField(label='Name of Your New Room', max_length=255)

    class Meta:
        model = Room
        fields = {'title',}

class EmailInvite(forms.Form):
    email = forms.EmailField(label='E-mail of new team member:', max_length=255)

class AcceptInvitation(forms.Form):
    code = forms.CharField(label='Enter the code from the invitation email:', max_length=20)

class EditRoom(forms.ModelForm):
    title = forms.CharField(label='Edit Your Room Name', max_length=255)

    class Meta:
        model = Room
        fields = {'title',}