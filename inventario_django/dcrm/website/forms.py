from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re
from .models import Record, Notificacion, Notificacion
import re


# ==============================
# MÓDULO NOTIFICACIONES
# ==============================

# NotificacionForm: Formulario con validaciones de seguridad
# - validación clean_titulo: filtra caracteres no permitidos usando regex
# - validación clean_mensaje: previene inyección XSS filtrando caracteres especiales
class NotificacionForm(forms.ModelForm):
    titulo = forms.CharField(
        label='Título',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la notificación'})
    )
    mensaje = forms.CharField(
        label='Mensaje',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Mensaje de la notificación', 'rows': 4})
    )

    class Meta:
        model = Notificacion
        fields = ('titulo', 'mensaje')

    # Validación: solo permite letras, números y símbolos básicos en el título
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo', '')
        if not re.match(r'^[a-zA-Z0-9\s\-_.,!?]+$', titulo):
            raise forms.ValidationError('El título contiene caracteres no permitidos. Solo se permiten letras, números y símbolos básicos (espacio, guion, guion bajo, punto, coma, signo de interrogación y exclamación).')
        return titulo

    # Validación: filtra caracteres XSS peligrosos del mensaje
    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje', '')
        clean_msg = re.sub(r'[<>"\'\\;(){}]', '', mensaje)
        if clean_msg != mensaje:
            raise forms.ValidationError('El mensaje contiene caracteres especiales no permitidos.')
        return mensaje


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nombre',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )
    email = forms.EmailField(
        label='Correo electronico',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electronico'})
    )
    phone = forms.CharField(
        label='Telefono',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefono'})
    )
    Address = forms.CharField(
        label='Direccion',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Direccion'})
    )
    city = forms.CharField(
        label='Ciudad',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'})
    )
    state = forms.CharField(
        label='Estado',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado'})
    )
    zipcode = forms.CharField(
        label='Codigo postal',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Codigo postal'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['password1'].label = 'Contrasena'
        self.fields['password2'].label = 'Confirmar contrasena'
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contrasena'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contrasena'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        username = user.username

        if commit:
            user.save()
            user = User.objects.get(username=username)
            Record.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data.get('phone', ''),
                Address=self.cleaned_data.get('Address', ''),
                city=self.cleaned_data.get('city', ''),
                state=self.cleaned_data.get('state', ''),
                zipcode=self.cleaned_data.get('zipcode', ''),
            )

        return user


class AddRecordForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Nombre', 'class': 'form-control'}), label='Nombre')
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Apellido', 'class': 'form-control'}), label='Apellido')
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Correo', 'class': 'form-control'}), label='Correo electronico')
    phone = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Numero de telefono', 'class': 'form-control'}), label='Telefono')
    Address = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Direccion', 'class': 'form-control'}), label='Direccion')
    city = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Ciudad', 'class': 'form-control'}), label='Ciudad')
    state = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Estado', 'class': 'form-control'}), label='Estado')
    zipcode = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Codigo postal', 'class': 'form-control'}), label='Codigo postal')

    class Meta:
        model = Record
        exclude = ['user']


class NotificacionForm(forms.ModelForm):
    titulo = forms.CharField(
        label='Titulo',
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titulo de la notificacion'})
    )
    mensaje = forms.CharField(
        label='Mensaje',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Mensaje', 'rows': 5})
    )
    receptor = forms.ModelChoiceField(
        label='Destinatario',
        queryset=User.objects.filter(is_active=True).order_by('username'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Notificacion
        fields = ['tipo', 'titulo', 'mensaje', 'receptor']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo', '').strip()
        if not re.match(r'^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s.,:;()\-]{3,80}$', titulo):
            raise forms.ValidationError('El titulo solo permite letras, numeros, espacios, puntos, comas, dos puntos, punto y coma, parentesis y guion.')
        return titulo

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje', '').strip()
        if not re.match(r'^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s.,;:()\-/]{10,500}$', mensaje):
            raise forms.ValidationError('El mensaje debe tener entre 10 y 500 caracteres y usar solo letras, numeros, espacios, puntos, comas, punto y coma, dos puntos, parentesis, guion y barra.')
        return mensaje

    def clean_receptor(self):
        receptor = self.cleaned_data.get('receptor')
        if receptor and not re.match(r'^[A-Za-z0-9_.-]{3,30}$', receptor.username):
            raise forms.ValidationError('El destinatario seleccionado no cumple con las reglas de seguridad del sistema.')
        return receptor

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.created_by and instance.creador_id is None:
            instance.creador = self.created_by
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, created_by=None, **kwargs):
        self.created_by = created_by
        super().__init__(*args, **kwargs)
        self.fields['receptor'].empty_label = 'Notificacion global para todos'

