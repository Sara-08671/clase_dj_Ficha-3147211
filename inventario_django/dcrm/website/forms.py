from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Record


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
