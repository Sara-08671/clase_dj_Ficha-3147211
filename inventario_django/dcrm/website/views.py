from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET, require_POST
from django.core.paginator import Paginator
from .forms import RegistroForm, AddRecordForm
from .models import Record


def home(request):
    if request.user.is_authenticated:
        search_id = request.GET.get('search_id', '').strip()
        if search_id:
            if not search_id.isdigit():
                messages.error(request, 'Ingrese un ID valido.')
                return redirect('home')
            records = Record.objects.select_related('user').filter(id=search_id)
            if not records.exists():
                messages.error(request, 'El registro no existe.')
                return redirect('home')
        else:
            records_list = Record.objects.select_related('user').all().order_by('-created_at')
            paginator = Paginator(records_list, 5)
            page_number = request.GET.get('page')
            records = paginator.get_page(page_number)
        return render(request, 'home.html', {'records': records, 'search_id': search_id})

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
    if not request.user.is_superuser:
        messages.error(request, 'Solo el administrador puede agregar usuarios.')
        return redirect('home')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Usuario agregado exitosamente.')
            return redirect('home')
    else:
        form = RegistroForm()

    return render(request, 'add_record.html', {'form': form, 'title': 'Agregar usuario'})


@login_required(login_url='home')
def customer_records(request, pk):
    try:
        customer_record = Record.objects.get(id=pk)
    except Record.DoesNotExist:
        messages.error(request, 'El registro no existe.')
        return redirect('home')
    
    records = Record.objects.all().order_by('id')
    record_ids = list(records.values_list('id', flat=True))
    current_index = record_ids.index(pk)
    prev_record = records.filter(id__lt=pk).last() if current_index > 0 else None
    next_record = records.filter(id__gt=pk).first() if current_index < len(record_ids) - 1 else None
    
    return render(request, 'record.html', {
        'customer_record': customer_record,
        'prev_record': prev_record,
        'next_record': next_record
    })


@login_required(login_url='home')
def edit_record(request, pk):
    try:
        customer_record = Record.objects.get(id=pk)
    except Record.DoesNotExist:
        messages.error(request, 'El registro no existe.')
        return redirect('home')

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
    try:
        customer_record = Record.objects.get(id=pk)
    except Record.DoesNotExist:
        messages.error(request, 'El registro no existe.')
        return redirect('home')
    user = customer_record.user
    customer_record.delete()
    user.delete()
    messages.success(request, 'Registro eliminado correctamente.')
    return redirect('home')  
