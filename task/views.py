from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import CustomAuthenticationForm

def home(request):
    return render(request, "home.html")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False 
            user.save()
            grupo_cliente, created = Group.objects.get_or_create(name='cliente')
            user.groups.add(grupo_cliente)
            
            current_site = get_current_site(request)
            subject = 'Activa tu cuenta'
            message = render_to_string('activacion_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            text_message = strip_tags(message)
            email = EmailMultiAlternatives(subject, text_message, to=[user.email])
            email.attach_alternative(message, "text/html")
            email.send()
            return render(request, 'confirmar_email.html')
            #return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

class login(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = False
    authentication_form = CustomAuthenticationForm
    success_url = reverse_lazy('home')
    
    def get_success_url(self):
        user = self.request.user
        if user.groups.filter(name='administrador').exists():
            return reverse_lazy('vista_administrador')
        elif user.groups.filter(name='cliente').exists():
            return reverse_lazy('vista_cliente')
        return reverse_lazy('home')
    
def is_cliente(user):
    return user.groups.filter(name='cliente').exists()

def is_admin(user):
    return user.groups.filter(name='administrador').exists()

@login_required
@user_passes_test(is_cliente)
def vista_cliente(request):
    return render(request, 'vista_cliente.html') 

@login_required
@user_passes_test(is_admin)
def vista_administrador(request):
    return render(request, 'vista_administrador.html')

def activar_cuenta(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'cuenta_activada.html')
    else:
        return render(request, 'cuenta_no_activada.html')
