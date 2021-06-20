from django import forms

class SearchTrackName(forms.Form):
    query = forms.CharField(label='Search by Track Name', max_length=255, required=False)
