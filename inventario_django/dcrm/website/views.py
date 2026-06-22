from functools import wraps
import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import AddRecordForm, NotificacionForm, RegistroForm
from .models import Notificacion, Record


IDENTIFIER_RE = r'^[A-Za-z0-9_.@-]{3,150}$'
PASSWORD_RE = r'^[A-Za-z0-9@_.\-]{1,128}$'

ROLE_ADMIN = 'admin'
ROLE_ORGANIZADOR = 'organizador'
ROLE_RESIDENTE = 'residente'
ORGANIZER_GROUP_NAME = 'Organizador'

# Mapa de roles usado para explicar permisos en templates y README.
ROLE_LABELS = {
    ROLE_ADMIN: 'Administrador',
    ROLE_ORGANIZADOR: 'Organizador',
    ROLE_RESIDENTE: 'Residente',
}


def user_has_admin_role(user):
    # Administrador: is_superuser=True. Tiene acceso total al CRUD y notificaciones.
    return user.is_superuser


def user_has_organizer_role(user):
    # Organizador: is_staff=True o grupo Organizador. Tiene permisos de gestion.
    return user.is_staff or user.groups.filter(name=ORGANIZER_GROUP_NAME).exists()


def user_has_management_role(user):
    # Administrador y Organizador pueden gestionar usuarios y notificaciones.
    return user_has_admin_role(user) or user_has_organizer_role(user)


def get_user_role(user):
    if user_has_admin_role(user):
        return ROLE_ADMIN
    if user_has_organizer_role(user):
        return ROLE_ORGANIZADOR
    return ROLE_RESIDENTE


def get_role_label(role):
    return ROLE_LABELS.get(role, ROLE_RESIDENTE)


def user_can_manage_record(user, record):
    # Residente solo puede gestionar su propio registro; Admin/Organizador gestionan todos.
    return user_has_management_role(user) or record.user_id == user.id


def admin_required(view_func):
    # Decorador central de seguridad para vistas de Admin/Organizador.
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debe iniciar sesion para acceder a esta seccion.')
            return redirect('login')
        if not user_has_management_role(request.user):
            messages.error(request, 'No tiene permisos de administrador u organizador.')
            return redirect('notificaciones')
        return view_func(request, *args, **kwargs)

    return wrapper


def get_accessible_record_or_redirect(request, pk):
    try:
        customer_record = Record.objects.select_related('user').get(id=pk)
    except Record.DoesNotExist:
        messages.error(request, 'El registro no existe.')
        return redirect('home')

    if not user_can_manage_record(request.user, customer_record):
        messages.error(request, 'No tiene permiso para gestionar este registro.')
        return redirect('home')

    return customer_record


def paginate_queryset(request, queryset, per_page=6):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


# PAGINA PRINCIPAL + LOGIN

def home(request):
    if request.user.is_authenticated:
        can_manage_records = user_has_management_role(request.user)
        records_base = Record.objects.select_related('user').all()

        if not can_manage_records:
            records_base = records_base.filter(user=request.user)

        search_id = request.GET.get('search_id', '').strip()

        if search_id:
            if not search_id.isdigit():
                messages.error(request, 'Ingrese un ID valido.')
                return redirect('home')

            records = records_base.filter(id=search_id)

            if not records.exists():
                messages.error(request, 'El registro no existe o no tiene permiso para verlo.')
                return redirect('home')
        else:
            records_list = records_base.order_by('-created_at')
            paginator = Paginator(records_list, 5)
            page_number = request.GET.get('page')
            records = paginator.get_page(page_number)

        # Mostrar notificaciones en el dashboard según rol
        notificaciones = Notificacion.objects.para_usuario(request.user).order_by('-created_at')[:5]

        return render(
            request,
            'home.html',
            {
                'records': records,
                'search_id': search_id,
                'can_manage_records': can_manage_records,
                'user_role': get_user_role(request.user),
                'role_label': get_role_label(get_user_role(request.user)),
                'notificaciones': notificaciones,
            }
        )

    if request.method == 'POST':
        messages.error(request, 'Inicia sesion desde el formulario oficial de login.')
        return redirect('login')

    return redirect('login')


# REGISTRO DE USUARIO

def register_user(request):
    # Registro público permite seleccionar rol (Admin/Organizador/Residente).
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistroForm(request.POST, role_selection=True)

        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada correctamente. Ahora inicia sesion.')
            return redirect('login')
    else:
        form = RegistroForm(role_selection=True)

    return render(request, 'register.html', {'form': form})


# LOGIN

def login_user(request):
    if request.method == 'POST':
        identificador = request.POST.get('email') or request.POST.get('username') or ''
        password = request.POST.get('password') or ''

        if not re.match(IDENTIFIER_RE, identificador.strip()) or not re.match(PASSWORD_RE, password):
            messages.error(request, 'El usuario/correo y la contrasena contienen caracteres no permitidos.')
            return redirect('login')

        identificador = identificador.strip()

        try:
            if '@' in identificador:
                user_obj = User.objects.get(email__iexact=identificador)
            else:
                user_obj = User.objects.get(username=identificador)
        except User.DoesNotExist:
            messages.error(request, 'Credenciales invalidas.')
            return redirect('login')

        user = authenticate(
            request,
            username=user_obj.username,
            password=password
        )

        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, f'Hola {user.username}, ingreso exitoso.')
            return redirect('home')

        messages.error(request, 'Credenciales invalidas.')
        return redirect('login')

    return render(request, 'login.html')


# CERRAR SESION

def logout_user(request):
    logout(request)
    messages.success(request, 'Sesion cerrada correctamente.')
    return redirect('login')


# PAGINAS PROTEGIDAS

@require_GET
@login_required(login_url='login')
def productos(request):
    return render(request, 'productos.html')


@require_GET
@login_required(login_url='login')
def categorias(request):
    return render(request, 'categorias.html')


@require_GET
@login_required(login_url='login')
def clientes(request):
    return render(request, 'clientes.html')


@require_GET
@login_required(login_url='login')
def ventas(request):
    return render(request, 'ventas.html')


# AGREGAR USUARIO

@admin_required
def add_record(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, role_selection=True)

        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario agregado exitosamente.')
            return redirect('home')
    else:
        form = RegistroForm(role_selection=True)

    return render(
        request,
        'add_record.html',
        {
            'form': form,
            'title': 'Agregar usuario',
        }
    )


# VER REGISTRO

@login_required(login_url='login')
def customer_records(request, pk):
    customer_record = get_accessible_record_or_redirect(request, pk)
    records = Record.objects.select_related('user').all()

    if not user_has_management_role(request.user):
        records = records.filter(user=request.user)

    records = records.order_by('id')
    record_ids = list(records.values_list('id', flat=True))
    current_index = record_ids.index(pk)

    prev_record = records.filter(id__lt=pk).last()
    next_record = records.filter(id__gt=pk).first()

    return render(
        request,
        'record.html',
        {
            'customer_record': customer_record,
            'prev_record': prev_record,
            'next_record': next_record,
            'can_manage_records': user_can_manage_record(request.user, customer_record),
        }
    )


# EDITAR

@admin_required
def edit_record(request, pk):
    customer_record = get_accessible_record_or_redirect(request, pk)

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

    return render(
        request,
        'record_form.html',
        {
            'form': form,
            'title': 'Editar registro',
            'customer_record': customer_record,
        }
    )


# ELIMINAR

@require_POST
@admin_required
def delete_record(request, pk):
    customer_record = get_accessible_record_or_redirect(request, pk)
    user = customer_record.user

    customer_record.delete()
    user.delete()

    messages.success(request, 'Registro eliminado correctamente.')
    return redirect('home')


# NOTIFICACIONES

@login_required(login_url='login')
def notificaciones(request):
    if user_has_admin_role(request.user):
        return notificaciones_admin(request)
    if user_has_organizer_role(request.user):
        return notificaciones_organizador(request)
    return notificaciones_usuario(request)


@admin_required
def notificaciones_admin(request):
    # Vista de notificaciones para Admin con CRUD: crea, filtra y lista.
    busqueda = request.GET.get('buscar', '').strip()
    estado = request.GET.get('estado', '').strip()

    queryset = Notificacion.objects.select_related('receptor').all()

    if busqueda:
        queryset = queryset.filter(titulo__icontains=busqueda)

    if estado == 'leidas':
        queryset = queryset.filter(leida=True)
    elif estado == 'no_leidas':
        queryset = queryset.filter(leida=False)

    # Procesa formulario POST para crear notificacion
    if request.method == 'POST':
        form = NotificacionForm(request.POST, created_by=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notificacion creada correctamente.')
            return redirect('notificaciones')
        messages.error(request, 'Revise los datos de la notificacion.')
    else:
        form = NotificacionForm(created_by=request.user)

    return render(request, 'notificaciones_admin.html', {
        'notificaciones': queryset,
        'users': User.objects.filter(is_active=True),
        'busqueda': busqueda,
        'estado': estado,
        'role_label': get_role_label(get_user_role(request.user)),
        'form': form,
        'tipos': Notificacion.TIPO_CHOICES,
    })


@login_required(login_url='login')
def notificaciones_organizador(request):
    # Vista de notificaciones para Organizador con filtros y marcar leída.
    filtro = request.GET.get('filtro', 'todas')
    queryset = Notificacion.objects.para_usuario(request.user)

    if filtro == 'no_leidas':
        queryset = queryset.filter(leida=False)
    elif filtro == 'leidas':
        queryset = queryset.filter(leida=True)

    return render(request, 'notificaciones_organizador.html', {
        'notificaciones': queryset,
        'filtro': filtro,
        'role_label': get_role_label(ROLE_ORGANIZADOR),
    })


@login_required(login_url='login')
def notificaciones_usuario(request):
    # Vista de notificaciones para Residente con filtros por estado.
    filtro = request.GET.get('filtro', 'todas')
    queryset = Notificacion.objects.para_usuario(request.user)

    if filtro == 'no_leidas':
        queryset = queryset.filter(leida=False)
    elif filtro == 'leidas':
        queryset = queryset.filter(leida=True)

    return render(request, 'notificaciones_residente.html', {
        'notificaciones': queryset,
        'filtro': filtro,
        'role_label': get_role_label(ROLE_RESIDENTE),
        'can_manage_notifications': False,
    })


@admin_required
def notificacion_crear(request):
    # Muestra formulario para crear notificaciones; solo Admin/Organizador disponen de esta vista.
    if request.method == 'POST':
        form = NotificacionForm(request.POST, created_by=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notificacion creada correctamente.')
            return redirect('notificaciones')
        messages.error(request, 'Revise los datos de la notificacion.')
    else:
        form = NotificacionForm(created_by=request.user)

    return render(request, 'notificaciones.html', {
        'role': get_user_role(request.user),
        'role_label': get_role_label(get_user_role(request.user)),
        'can_manage_notifications': True,
        'form': form,
        'tipos': Notificacion.TIPO_CHOICES,
        'total': Notificacion.objects.count(),
        'no_leidas': Notificacion.objects.filter(leida=False).count(),
    })


@admin_required
def notificacion_editar(request, pk):
    # Permite editar una notificacion existente; protegido por admin_required.
    notificacion = get_object_or_404(Notificacion, pk=pk)

    if request.method == 'POST':
        form = NotificacionForm(request.POST, instance=notificacion, created_by=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notificacion actualizada correctamente.')
            return redirect('notificaciones')
        messages.error(request, 'Revise los datos de la notificacion.')
    else:
        form = NotificacionForm(instance=notificacion, created_by=request.user)

    return render(request, 'notificaciones.html', {
        'role': get_user_role(request.user),
        'role_label': get_role_label(get_user_role(request.user)),
        'can_manage_notifications': True,
        'form': form,
        'notificacion': notificacion,
        'tipos': Notificacion.TIPO_CHOICES,
        'total': Notificacion.objects.count(),
        'no_leidas': Notificacion.objects.filter(leida=False).count(),
    })


@require_POST
@admin_required
def notificacion_eliminar(request, pk):
    # Elimina una notificacion; requiere POST y rol de gestion.
    notificacion = get_object_or_404(Notificacion, pk=pk)
    notificacion.delete()
    messages.success(request, 'Notificacion eliminada correctamente.')
    return redirect('notificaciones')


@login_required(login_url='login')
def notificacion_detalle(request, pk):
    can_manage_notifications = user_has_management_role(request.user)

    if can_manage_notifications:
        notificacion = get_object_or_404(Notificacion, pk=pk)
    else:
        notificacion = get_object_or_404(Notificacion, pk=pk)
        if not notificacion.pertenece_a(request.user):
            messages.error(request, 'No tiene permiso para ver esta notificacion.')
            return redirect('notificaciones')

    queryset = Notificacion.objects.para_usuario(request.user)
    role = get_user_role(request.user)

    return render(request, 'notificaciones.html', {
        'role': role,
        'role_label': get_role_label(role),
        'can_manage_notifications': can_manage_notifications,
        'notificacion': notificacion,
        'total': Notificacion.objects.count() if can_manage_notifications else queryset.count(),
        'no_leidas': Notificacion.objects.filter(leida=False).count() if can_manage_notifications else queryset.filter(leida=False).count(),
    })


@require_POST
@login_required(login_url='login')
def notificacion_marcar_leida(request, pk):
    notificacion = get_object_or_404(Notificacion, pk=pk)
    if not notificacion.pertenece_a(request.user):
        messages.error(request, 'No tiene permiso para modificar esta notificacion.')
        return redirect('notificaciones')

    notificacion.marcar_leida()
    messages.success(request, 'Notificacion marcada como leida.')
    return redirect('notificaciones')


@require_POST
@login_required(login_url='login')
def notificaciones_marcar_todas_leidas(request):
    queryset = Notificacion.objects.para_usuario(request.user).filter(leida=False)
    count = queryset.count()
    queryset.update(leida=True, leida_en=timezone.now())
    messages.success(request, f'{count} notificaciones marcadas como leidas.')
    return redirect('notificaciones')
