from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def grooveboard(request):
    return render(request, 'grooveboard.html')
