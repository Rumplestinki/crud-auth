from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request, 'home.html')

def signup(request):
    # El cliente solicita datos
    if request.method == 'GET':
        return render(request, 'signup.html', {
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
                login(request, user)
                # Redirecciona a tasks.html
                return redirect('tasks')
            except IntegrityError:
                # Cuando el usuario ya existe
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': "El usuario ya existe"
                })
        # Cuando las contraseñas no coiciden
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': "Las contraseñas no coinciden"
        })

# login_requied nos ayuda a que no puedan acceder a las rutas sin iniciar secion
@login_required
def tasks(request):
    # Filtra las tareas por usuario y que no esten completadas
    tasks = Task.objects.filter(user=request.user, datecomplete__isnull=True)
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def tasks_completed(request):
    # Filtra las tareas por usuario completadas
    tasks = Task.objects.filter(user=request.user, datecomplete__isnull=False).order_by
    ('-datecomplete')
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        # Muestra los datos de la tarea
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            # Actualiza los datos de la tarea
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task,
                'form': form,
                'error': 'Error al actualizar'
            })

@login_required         
def complete_task(request, task_id):
    # Cambia el estado y marca como tarea completada
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecomplete = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    # Elimina la tarea
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def create_task(request):
    
    if request.method == 'GET':
        return render(request, 'create_task.html', {
        'form': TaskForm
    })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Ingrese datos validos'
            })

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    # Si el metodo es GET renderiza el html
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    # Si es POST autentifica el usuario
    else:
        # guarda los datos en user
        user = authenticate(
            request, username=request.POST['username'], 
            password=request.POST['password'])
        # Si no exixte redirecciona y muestra un error
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'El usuario y/o la contraseña son incorrectos'
            })
        # Si existe guarda la secion y lo redirecciona
        else:
            login(request, user)
            return redirect('tasks')
