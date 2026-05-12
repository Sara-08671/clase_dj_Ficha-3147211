# Importa la función render, que permite combinar una plantilla HTML con datos y devolver una respuesta HTTP.
from django.shortcuts import render, redirect
# Importa funciones de autenticación: authenticate verifica credenciales,
# login inicia sesión, logout cierra sesión
from django.contrib.auth import authenticate, login, logout
# Importa el sistema de mensajes para mostrar notificaciones al usuario
from django.contrib import messages
# Importa decoradores para requerir métodos HTTP específicos
from django.views.decorators.http import require_GET, require_POST
# Importa el modelo User de Django
from django.contrib.auth.models import User
# Importa el decorador para requerir autenticación
from django.contrib.auth.decorators import login_required


# -------------------------------------------------------------------------------------
# VISTA PRINCIPAL (HOME) - Maneja registro e inicio de sesión
# -------------------------------------------------------------------------------------
def home(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Obtiene los datos del formulario
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Determina si es acción de login o registro
        action = request.POST.get('action', 'login')
        
        # -------------------------------------------------------------------------------------
        # ACCIÓN: REGISTRO
        # -------------------------------------------------------------------------------------
        if action == 'register':
            username = request.POST.get('username', '').strip()
            # Verifica si el usuario ya existe
            if username and User.objects.filter(username=username).exists():
                messages.error(request, "El comandante ya existe en el sistema")
                return redirect('home')
            elif username and email:
                # Crea el usuario sin iniciar sesión automáticamente
                user = User.objects.create_user(username=username, password=password, email=email)
                messages.success(request, "¡Cuenta creada! Ahora debes iniciar sesión")
                return redirect('home')
            else:
                messages.error(request, "Usuario y correo son obligatorios")
                return redirect('home')
        
        # -------------------------------------------------------------------------------------
        # ACCIÓN: LOGIN
        # -------------------------------------------------------------------------------------
        else:
            # Busca el usuario por email (Django usa username para autenticación)
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                user = None
            
            if user is not None:
                # Inicia sesión y muestra mensaje de bienvenida
                login(request, user)
                messages.success(request, f"¡Hola {user.username}! Que tengas un día increíble")
                return redirect('home')
            else:
                messages.error(request, "Credenciales incorrectas")
                return redirect('home')
    
    # Si es GET, muestra la página principal
    else:
        return render(request, 'home.html', {})


# -------------------------------------------------------------------------------------
# VISTA DE LOGIN (separada) - Alternativa para login dedicado
# -------------------------------------------------------------------------------------
def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Busca el usuario por email y luego autentica
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            login(request, user)
            messages.success(request, f"¡Hola {user.username}! Que tengas un día increíble")
            return redirect('home')
        else:
            messages.error(request, "Credenciales inválidas")
            return redirect('home')
    return render(request, 'home.html')


# -------------------------------------------------------------------------------------
# VISTA DE LOGOUT - Cierra la sesión del usuario
# -------------------------------------------------------------------------------------
def logout_user(request):
    logout(request)
    messages.info(request, "Sesión cerrada")
    return redirect('home')


# -------------------------------------------------------------------------------------
# VISTAS PROTEGIDAS - Requieren autenticación
# -------------------------------------------------------------------------------------
# Vista de productos - solo accesible mediante GET y requiere login
@require_GET
@login_required(login_url='home')
def productos(request):
    return render(request, 'productos.html', {})


# Vista de categorías - solo accesible mediante GET y requiere login
@require_GET
@login_required(login_url='home')
def categorias(request):
    return render(request, 'categorias.html', {})


# Vista de clientes - solo accesible mediante GET y requiere login
@require_GET
@login_required(login_url='home')
def clientes(request):
    return render(request, 'clientes.html', {})


# Vista de ventas - solo accesible mediante GET y requiere login
@require_GET
@login_required(login_url='home')
def ventas(request):
    return render(request, 'ventas.html', {})