from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET, require_POST
from .forms import RegistroForm, AddRecordForm
from .models import Record


def home(request):
    if request.user.is_authenticated:
        records = Record.objects.select_related('user').all().order_by('-created_at')
        return render(request, 'home.html', {'records': records})

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Hola {user.username}, ingreso exitoso.')
            return redirect('home')

        messages.error(request, 'Usuario o contrasena incorrectos.')
        return redirect('home')

    return render(request, 'home.html')


def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
            messages.success(request, 'Cuenta creada correctamente.')
            return redirect('home')
    else:
        form = RegistroForm()

    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            messages.success(request, f'Hola {user.username}, ingreso exitoso.')
            return redirect('home')

        messages.error(request, 'Credenciales invalidas.')
        return redirect('home')

    return render(request, 'home.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'Sesion cerrada correctamente.')
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


@login_required(login_url='home')
def add_record(request):
    if request.method == 'POST':
        form = AddRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            messages.success(request, 'Registro agregado exitosamente.')
            return redirect('home')
    else:
        form = AddRecordForm()

    return render(request, 'record_form.html', {'form': form, 'title': 'Agregar registro'})


@login_required(login_url='home')
def customer_records(request, pk):
    customer_record = get_object_or_404(Record, id=pk)
    return render(request, 'record.html', {'customer_record': customer_record})


@login_required(login_url='home')
def edit_record(request, pk):
    customer_record = get_object_or_404(Record, id=pk)

    if request.method == 'POST':
        form = AddRecordForm(request.POST, instance=customer_record)
        if form.is_valid():
            record = form.save()
            record.user.first_name = record.first_name
            record.user.last_name = record.last_name
            record.user.email = record.email
            record.user.save()
            messages.success(request, 'Registro actualizado correctamente.')
            return redirect('record', pk=record.id)
    else:
        form = AddRecordForm(instance=customer_record)

    return render(request, 'record_form.html', {
        'form': form,
        'title': 'Editar registro',
        'customer_record': customer_record,
    })


@require_POST
@login_required(login_url='home')
def delete_record(request, pk):
    customer_record = get_object_or_404(Record, id=pk)
    user = customer_record.user
    customer_record.delete()
    user.delete()
    messages.success(request, 'Registro eliminado correctamente.')
    return redirect('home')

#esta parte para crear la targeta de agregar usuario
def add_record(request): # esta funcion lo que hace es agregar un nuevo registro a la base de datos 
    #en esta parte debemos verificar si el usuario esta auntenticado o no, en este caso no permoite agregar usuarios
    form = RegistroForm(request.POST or None) # esta parte lo que hace es crear un formulario con los datos que se ingresan en el formulario de registro
    if request.user.is_authenticated: # esta parte lo que hace es verificar si el usuario esta auntenticado o no, en este caso no permoite agregar usuarios
        if request.method == 'POST': # esta parte lo que hace es verificar si el metodo de la solicitud es POST, en este caso se permite agregar usuarios
            if form.is_valid(): # esta parte lo que hace es verificar si el formulario es valido o no, en este caso se permite agregar usuarios
                add_record= form.save() # esta parte lo que hace es guardar el formulario en la base de datos
                messages.success(request, 'Registro agregado exitosamente.') # esta parte lo que hace es mostrar un mensaje de exito al usuario
                return redirect('home') # esta parte lo que hace es redirigir al usuario a la pagina de inicio
            return render (request, 'record_form.html', {'form': form}) # esta parte lo que hace es renderizar la plantilla de agregar registro con el formulario y el titulo
        else: # si el usuario no esta autentificado no le permite agregar registros
          messages.success(request," no estas autentidicado entonces no se puede hacer esta accion")
        return redirect('home') # redirige a la pagina principal  