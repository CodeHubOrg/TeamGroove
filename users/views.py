from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()            
            user.save()
            login(request, user)
            return redirect('grooveboard')
    else:
         form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)

    return redirect('frontpage.html')
