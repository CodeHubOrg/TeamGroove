from django.shortcuts import render
from django.http import HttpResponse
from spotify_api_test import return_json_data
from django.shortcuts import render
from log_in import log_in
# Create your views here.

def search(request):
    return HttpResponse('this is a test')

def index(request):

    context = {'json': return_json_data()}
    return render(request, 'album_list/index.html', context)
