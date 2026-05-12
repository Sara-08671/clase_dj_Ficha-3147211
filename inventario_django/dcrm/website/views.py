# Importa la función render, que permite combinar una plantilla HTML con datos y devolver una respuesta HTTP.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


# Aquí se deben crear las vistas de la aplicación.
# Esta función define la vista principal (home) del sitio.
def home(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        action = request.POST.get('action', 'login')
        
        if action == 'register':
            email = request.POST.get('email', '')
            if User.objects.filter(username=username).exists():
                messages.error(request, "El comandante ya existe en el sistema")
                return redirect('home')
            else:
                user = User.objects.create_user(username=username, password=password, email=email)
                messages.success(request, "¡Cuenta creada! Ahora debes iniciar sesión")
                return redirect('home')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido de vuelta, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Credenciales incorrectas")
                return redirect('home')
    else:
        return render(request, 'home.html', {})
# Esta función define la vista de inicio de sesión (login) del sitio.


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"¡Bienvenido, {username}!")
            return redirect('home')
        else:
            messages.error(request, "Credenciales inválidas")
            return redirect('home')
    return render(request, 'home.html')

def logout_user(request):
    logout(request)
    messages.info(request, "Sesión cerrada")
    return redirect('home')

@require_GET
@login_required(login_url='home')
def productos(request):
    return render(request, 'productos.html', {})

@require_GET
@login_required(login_url='home')
def categorias(request):
    return render(request, 'categorias.html', {})

@require_GET
@login_required(login_url='home')
def clientes(request):
    return render(request, 'clientes.html', {})

@require_GET
@login_required(login_url='home')
def ventas(request):
    return render(request, 'ventas.html', {})