from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

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
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }

class CustomAuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        self.user = None

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
