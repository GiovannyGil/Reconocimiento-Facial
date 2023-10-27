from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError

# Create your views here.
# Create your views here.
def signin(request):
    if request.method == 'GET': # si el metodo es GET
        return render(request, "login/signin.html",{
            'form':AuthenticationForm
        })
    else: # si no, el metodo es POST
        user = authenticate(request, username=request.POST['username'], password=request.POST['password']) # verifica si el usuario existe
        if user is None: # si el usuario no existe
            return render(request, "login/signin.html",{
                'form':AuthenticationForm,
                'error':'Usuario y/o contraseña incorrectos'
            })
        else: # si el usuario existe
            login(request, user) # si el usuario existe, lo loguea
            return redirect('dash') # redirecciona a la página de inicio

def signout(request):
    logout(request)
    return redirect('home')


