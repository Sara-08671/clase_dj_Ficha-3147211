from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET, require_POST
from django.core.paginator import Paginator
from django.utils import timezone

from .forms import RegistroForm, AddRecordForm, NotificacionForm
from .models import Record, Notificacion



# PAGINA PRINCIPAL + LOGIN
def home(request):

    # Si ya inició sesión muestra registros
    if request.user.is_authenticated:


        search_id = request.GET.get('search_id', '').strip()


        if search_id:


            if not search_id.isdigit():

                messages.error(
                    request,
                    'Ingrese un ID valido.'
                )

                return redirect('home')



            records = Record.objects.select_related(
                'user'
            ).filter(id=search_id)



            if not records.exists():

                messages.error(
                    request,
                    'El registro no existe.'
                )

                return redirect('home')



        else:


            records_list = Record.objects.select_related(
                'user'
            ).all().order_by('-created_at')


            paginator = Paginator(
                records_list,
                5
            )


            page_number = request.GET.get('page')


            records = paginator.get_page(
                page_number
            )



        return render(
            request,
            'home.html',
            {
                'records': records,
                'search_id': search_id
            }
        )



    # LOGIN DESDE HOME
    if request.method == 'POST':


        username = request.POST.get('username')

        password = request.POST.get('password')



        user = authenticate(
            request,
            username=username,
            password=password
        )



        if user is not None:


            login(
                request,
                user
            )


            messages.success(
                request,
                f'Hola {user.username}, ingreso exitoso.'
            )


            return redirect('home')



        messages.error(
            request,
            'Usuario o contraseña incorrectos.'
        )


        return redirect('home')



    return render(
        request,
        'home.html'
    )




# REGISTRO DE USUARIO
def register_user(request):


    if request.user.is_authenticated:

        return redirect('home')



    if request.method == 'POST':


        form = RegistroForm(
            request.POST
        )



        if form.is_valid():


            form.save()



            messages.success(
                request,
                'Cuenta creada correctamente. Ahora inicia sesión.'
            )



            return redirect('login')



    else:


        form = RegistroForm()



    return render(
        request,
        'register.html',
        {
            'form': form
        }
    )





# LOGIN
def login_user(request):


    if request.method == 'POST':


        email = request.POST.get('email')

        password = request.POST.get('password')



        try:


            user_obj = User.objects.get(
                email=email
            )


            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )



        except User.DoesNotExist:


            user = None





        if user is not None:


            login(
                request,
                user
            )


            messages.success(
                request,
                f'Hola {user.username}, ingreso exitoso.'
            )


            return redirect('home')




        messages.error(
            request,
            'Credenciales invalidas.'
        )


        return redirect('login')



    return render(
        request,
        'login.html'
    )





# CERRAR SESION
def logout_user(request):


    logout(request)



    messages.success(
        request,
        'Sesion cerrada correctamente.'
    )



    return redirect('login')





# PAGINAS PROTEGIDAS

@require_GET
@login_required(login_url='login')
def productos(request):

    return render(
        request,
        'productos.html'
    )



@require_GET
@login_required(login_url='login')
def categorias(request):

    return render(
        request,
        'categorias.html'
    )



@require_GET
@login_required(login_url='login')
def clientes(request):

    return render(
        request,
        'clientes.html'
    )



@require_GET
@login_required(login_url='login')
def ventas(request):

    return render(
        request,
        'ventas.html'
    )





# AGREGAR USUARIO
@login_required(login_url='login')
def add_record(request):


    if request.method == 'POST':


        form = RegistroForm(
            request.POST
        )



        if form.is_valid():


            form.save()



            messages.success(
                request,
                'Usuario agregado exitosamente.'
            )


            return redirect('home')



    else:


        form = RegistroForm()




    return render(
        request,
        'add_record.html',
        {
            'form': form,
            'title':'Agregar usuario'
        }
    )





# VER REGISTRO
@login_required(login_url='login')
def customer_records(request, pk):


    try:


        customer_record = Record.objects.get(
            id=pk
        )



    except Record.DoesNotExist:


        messages.error(
            request,
            'El registro no existe.'
        )


        return redirect('home')



    records = Record.objects.all().order_by('id')


    record_ids = list(
        records.values_list(
            'id',
            flat=True
        )
    )



    current_index = record_ids.index(pk)



    prev_record = records.filter(
        id__lt=pk
    ).last()



    next_record = records.filter(
        id__gt=pk
    ).first()




    return render(
        request,
        'record.html',
        {
            'customer_record': customer_record,
            'prev_record': prev_record,
            'next_record': next_record
        }
    )





# EDITAR
@login_required(login_url='login')
def edit_record(request, pk):


    try:


        customer_record = Record.objects.get(
            id=pk
        )



    except Record.DoesNotExist:


        messages.error(
            request,
            'El registro no existe.'
        )


        return redirect('home')




    if request.method == 'POST':


        form = AddRecordForm(
            request.POST,
            instance=customer_record
        )



        if form.is_valid():


            record = form.save()



            record.user.first_name = record.first_name

            record.user.last_name = record.last_name

            record.user.email = record.email


            record.user.save()



            messages.success(
                request,
                'Registro actualizado correctamente.'
            )



            return redirect(
                'record',
                pk=record.id
            )



    else:


        form = AddRecordForm(
            instance=customer_record
        )



    return render(
        request,
        'record_form.html',
        {
            'form':form,
            'title':'Editar registro',
            'customer_record':customer_record
        }
    )





# ELIMINAR
@require_POST
@login_required(login_url='login')
def delete_record(request, pk):


    try:


        customer_record = Record.objects.get(
            id=pk
        )



    except Record.DoesNotExist:


        messages.error(
            request,
            'El registro no existe.'
        )


        return redirect('home')



    user = customer_record.user



    customer_record.delete()


    user.delete()



    messages.success(
        request,
        'Registro eliminado correctamente.'
    )



    return redirect('home')

def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debe iniciar sesion como administrador.')
            return redirect('login')
        if not request.user.is_superuser:
            messages.error(request, 'No tiene permisos de administrador.')
            return redirect('notificaciones')
        return view_func(request, *args, **kwargs)

    return wrapper


def paginate_queryset(request, queryset, per_page=6):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@login_required(login_url='login')
def notificaciones(request):
    if request.user.is_superuser:
        return notificaciones_admin(request)
    return notificaciones_usuario(request)


@admin_required
def notificaciones_admin(request):
    busqueda = request.GET.get('busqueda', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    estado = request.GET.get('estado', '').strip()

    queryset = Notificacion.objects.select_related('receptor', 'creador').all()

    if busqueda:
        queryset = queryset.filter(titulo__icontains=busqueda)

    if tipo:
        queryset = queryset.filter(tipo=tipo)

    if estado == 'leidas':
        queryset = queryset.filter(leida=True)
    elif estado == 'no_leidas':
        queryset = queryset.filter(leida=False)

    page = paginate_queryset(request, queryset)
    context = {
        'role': 'admin',
        'page': page,
        'busqueda': busqueda,
        'tipo': tipo,
        'estado': estado,
        'tipos': Notificacion.TIPO_CHOICES,
        'total': Notificacion.objects.count(),
        'no_leidas': Notificacion.objects.filter(leida=False).count(),
    }
    return render(request, 'notificaciones.html', context)


@login_required(login_url='login')
def notificaciones_usuario(request):
    queryset = Notificacion.objects.para_usuario(request.user).select_related('receptor', 'creador')
    page = paginate_queryset(request, queryset)
    context = {
        'role': 'usuario',
        'page': page,
        'total': queryset.count(),
        'no_leidas': queryset.filter(leida=False).count(),
    }
    return render(request, 'notificaciones.html', context)


@admin_required
def notificacion_crear(request):
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
        'role': 'admin',
        'form': form,
        'tipos': Notificacion.TIPO_CHOICES,
        'total': Notificacion.objects.count(),
        'no_leidas': Notificacion.objects.filter(leida=False).count(),
    })


@admin_required
def notificacion_editar(request, pk):
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
        'role': 'admin',
        'form': form,
        'notificacion': notificacion,
        'tipos': Notificacion.TIPO_CHOICES,
        'total': Notificacion.objects.count(),
        'no_leidas': Notificacion.objects.filter(leida=False).count(),
    })


@require_POST
@admin_required
def notificacion_eliminar(request, pk):
    notificacion = get_object_or_404(Notificacion, pk=pk)
    notificacion.delete()
    messages.success(request, 'Notificacion eliminada correctamente.')
    return redirect('notificaciones')


@login_required(login_url='login')
def notificacion_detalle(request, pk):
    if request.user.is_superuser:
        notificacion = get_object_or_404(Notificacion, pk=pk)
    else:
        notificacion = get_object_or_404(Notificacion, pk=pk)
        if not notificacion.pertenece_a(request.user):
            messages.error(request, 'No tiene permiso para ver esta notificacion.')
            return redirect('notificaciones')

    return render(request, 'notificaciones.html', {
        'role': 'admin' if request.user.is_superuser else 'usuario',
        'notificacion': notificacion,
        'total': Notificacion.objects.count() if request.user.is_superuser else Notificacion.objects.para_usuario(request.user).count(),
        'no_leidas': Notificacion.objects.filter(leida=False).count() if request.user.is_superuser else Notificacion.objects.para_usuario(request.user).filter(leida=False).count(),
    })


@login_required(login_url='login')
def notificacion_marcar_leida(request, pk):
    notificacion = get_object_or_404(Notificacion, pk=pk)
    if not notificacion.pertenece_a(request.user):
        messages.error(request, 'No tiene permiso para modificar esta notificacion.')
        return redirect('notificaciones')

    notificacion.marcar_leida()
    messages.success(request, 'Notificacion marcada como leida.')
    return redirect('notificaciones')


@login_required(login_url='login')
def notificaciones_marcar_todas_leidas(request):
    queryset = Notificacion.objects.para_usuario(request.user).filter(leida=False)
    count = queryset.count()
    queryset.update(leida=True, leida_en=timezone.now())
    messages.success(request, f'{count} notificaciones marcadas como leidas.')
    return redirect('notificaciones')