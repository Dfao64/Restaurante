from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Producto, Empleado, Turno
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from datetime import date

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nombre = forms.CharField(max_length=255, required=True)
    direccion = forms.CharField(max_length=255, required=True)
    numero_telefono = forms.CharField(max_length=20, required=True)

    class Meta:
        model = CustomUser
        fields = ('nombre', 'email', 'direccion', 'numero_telefono', 'password1', 'password2')
        widgets = {
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CustomAuthenticationForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        self.user = None

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(self.request, email=email, password=password)

        if user is None:
            raise forms.ValidationError(
                _("Por favor, introduzca un email y clave correctos."),
                code='invalid_login',
            )
        if not user.is_active:
            raise forms.ValidationError(
                _("Tu cuenta no ha sido activada. Revisa tu correo electrónico."),
                code='inactive',
            )

        self.user = user
        return self.cleaned_data

    def get_user(self):
        return self.user

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'tipo', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = '__all__'
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['fecha', 'hora_inicio', 'hora_fin']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class FormularioPagoTarjeta(forms.Form):
    nombre_titular = forms.CharField(
        max_length=100,
        label='Nombre del titular',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero_tarjeta = forms.CharField(
        max_length=16,
        min_length=16,
        label='Número de tarjeta',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234123412341234',
            'pattern': '[0-9]{16}',
            'title': 'Debe contener 16 dígitos'
        })
    )
    fecha_expiracion = forms.DateField(
        label='Fecha de expiración',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    cvv = forms.CharField(
        max_length=3,
        min_length=3,
        label='CVV',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'pattern': '[0-9]{3}',
            'title': 'Debe contener 3 dígitos'
        })
    )
    alergias = forms.CharField(
        label='¿Tiene alguna alergia?', 
        required=False, 
        widget=forms.Textarea(attrs={
            'rows': 2, 
            'class': 'form-control'
        })
    )
    propina = forms.BooleanField(
        required=False,
        label='¿Desea incluir una propina del 10%?',
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_numero_tarjeta(self):
        numero_tarjeta = self.cleaned_data.get('numero_tarjeta')
        if not numero_tarjeta.isdigit():
            raise forms.ValidationError('El número de tarjeta debe contener solo dígitos.')
        return numero_tarjeta
    
    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv')
        if not cvv.isdigit():
            raise forms.ValidationError('El CVV debe contener solo dígitos.')
        return cvv
    
    def clean_fecha_expiracion(self):
        fecha = self.cleaned_data.get('fecha_expiracion')
        if fecha < date.today():
            raise forms.ValidationError("La tarjeta está expirada.")
        return fecha
    
class FormularioPagoDomicilio(forms.Form):
    nombre_titular = forms.CharField(
        max_length=100,
        label='Nombre del titular',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero_tarjeta = forms.CharField(
        max_length=16,
        min_length=16,
        label='Número de tarjeta',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    fecha_expiracion = forms.DateField(
        label='Fecha de expiración (MM/AA)',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    cvv = forms.CharField(
        max_length=3,
        min_length=3,
        label='CVV',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    direccion = forms.CharField(
        max_length=255,
        label='Dirección de entrega',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    alergias = forms.CharField(
        required=False,
        label='¿Tiene alguna alergia?',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional'})
    )
    propina = forms.BooleanField(
        required=False,
        label='¿Desea incluir una propina del 10%?',
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    
    def clean_numero_tarjeta(self):
        numero_tarjeta = self.cleaned_data.get('numero_tarjeta')
        if not numero_tarjeta.isdigit():
            raise forms.ValidationError('El número de tarjeta debe contener solo dígitos.')
        return numero_tarjeta

    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv')
        if not cvv.isdigit():
            raise forms.ValidationError('El CVV debe contener solo dígitos.')
        return cvv