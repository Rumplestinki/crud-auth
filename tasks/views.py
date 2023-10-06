from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
# Create your views here.


def home(request):
    return render(request, 'home.html')


def helloword(request):
    # El cliente solicita datos
    if request.method == 'GET':
        return render(request, 'singup.html', {
            'form': UserCreationForm
        })
    else:
        # Verifica que ambas contraseñas sean iguales
        if request.POST['password1'] == request.POST['password2']:
            try:
                # Registra el usuario
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                return HttpResponse('Usuario creado correctamente')
            except:
                # Cuando el usuario ya existe
                return render(request, 'singup.html', {
                    'form': UserCreationForm,
                    'error': "El usuario ya existe"
                })
        # Cuando las contraseñas no coiciden
        return render(request, 'singup.html', {
            'form': UserCreationForm,
            'error': "Las contraseñas no coinciden"
        })
