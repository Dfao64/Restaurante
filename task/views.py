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
from django.contrib.auth import get_user_model, logout
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import CustomAuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito, ItemCarrito, Empleado, Turno, Pedido
from .forms import ProductoForm, EmpleadoForm, TurnoForm, FormularioPagoTarjeta, FormularioPagoDomicilio
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse

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

def enviar_email_recuperacion(request, user):
    current_site = get_current_site(request)
    subject = 'Recuperación de contraseña'
    message = render_to_string('password_reset_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    text_message = strip_tags(message)
    email = EmailMultiAlternatives(subject, text_message, to=[user.email])
    email.attach_alternative(message, "text/html")
    email.send()
    
def signout(request):
    logout(request)
    return redirect('home')

@login_required
@user_passes_test(is_admin)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')  
    else:
        form = ProductoForm()
    return render(request, 'crear_producto.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'lista_productos.html', {'productos': productos})

@login_required
@user_passes_test(is_admin)
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'editar_producto.html', {'form': form, 'producto': producto})

@login_required
@user_passes_test(is_admin)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return render(request, 'eliminar_producto.html', {'producto': producto})

def catalogo_cliente(request):
    productos = Producto.objects.all()
    return render(request, 'catalogo_cliente.html', {'productos': productos})

def agregar_al_carrito(request, producto_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
    
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(user=request.user)
    
    item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    if not created:
        item.cantidad += 1
    item.save()

    return JsonResponse({'message': 'Producto agregado con éxito'})

def ver_carrito(request):
    try:
        carrito = Carrito.objects.get(user=request.user)
    except Carrito.DoesNotExist:
        carrito = None
        items = []
        total = 0
    else:
        items = ItemCarrito.objects.filter(carrito=carrito)
        total = sum([item.producto.precio * item.cantidad for item in items])

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')

        try:
            item = ItemCarrito.objects.get(id=item_id)
        except ItemCarrito.DoesNotExist:
            return redirect('carrito_compras')  # Redirigir si el producto no existe.

        if action == 'eliminar':
            item.delete()

        elif action == 'disminuir' and item.cantidad > 1:
            item.cantidad -= 1
            item.save()

        elif action == 'agregar':
            item.cantidad += 1
            item.save()

        return redirect('carrito_compras')  # Redirigir después de la acción.

    return render(request, 'carrito_compras.html', {'items': items, 'total': total})

def pago_recoger(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        carrito = Carrito.objects.get(user=request.user)
        items = ItemCarrito.objects.filter(carrito=carrito)
    except Carrito.DoesNotExist:
        messages.error(request, 'El carrito está vacío.')
        return redirect('catalogo_cliente')

    if not items.exists():
        messages.error(request, 'El carrito está vacío.')
        return redirect('catalogo_cliente')

    pago_exitoso = False

    if request.method == 'POST':
        form = FormularioPagoTarjeta(request.POST)
        if form.is_valid():
            alergias = form.cleaned_data.get('alergias', '')
            for item in items:
                Pedido.objects.create(
                    producto_nombre=item.producto.nombre,
                    cantidad=item.cantidad,
                    precio_total=item.producto.precio * item.cantidad,
                    metodo='Recoger en tienda',
                    alergias=alergias
                )
            items.delete()
            carrito.delete()
            pago_exitoso = True  # ✅ Activa el SweetAlert
            form = FormularioPagoTarjeta()  # Limpia el formulario
    else:
        form = FormularioPagoTarjeta()

    return render(request, 'pago_recoger.html', {'form': form, 'pago_exitoso': pago_exitoso})

def pago_domicilio(request):
    # Lógica para procesar un pedido de domicilio
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        carrito = Carrito.objects.get(user=request.user)
        items = ItemCarrito.objects.filter(carrito=carrito)
    except Carrito.DoesNotExist:
        messages.error(request, 'El carrito está vacío.')
        return redirect('catalogo_cliente')

    if not items.exists():
        messages.error(request, 'El carrito está vacío.')
        return redirect('catalogo_cliente')

    if request.method == 'POST':
        form = FormularioPagoDomicilio(request.POST)
        if form.is_valid():
            for item in items:
                Pedido.objects.create(
                    producto_nombre=item.producto.nombre,
                    cantidad=item.cantidad,
                    precio_total=item.producto.precio * item.cantidad,
                    metodo='Domicilio',
                    direccion=form.cleaned_data['direccion'],
                    alergias=form.cleaned_data.get('alergias', '')
                )
            items.delete()
            carrito.delete()
            return render(request, 'pago_domicilio.html', {'form': form, 'pago_exitoso': True})  # Aquí indicamos que se mostrará la alerta
    else:
        form = FormularioPagoDomicilio()

    return render(request, 'pago_domicilio.html', {'form': form})

def lista_empleado(request):
    empleados = Empleado.objects.all()
    return render(request, 'lista_empleados.html', {'empleados': empleados})

def crear_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_empleado')
    else:
        form = EmpleadoForm()
    return render(request, 'crear_empleado.html', {'form': form})

def editar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('lista_empleado')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'editar_empleado.html', {'form': form, 'empleado': empleado})

def eliminar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        return redirect('lista_empleado')
    return render(request, 'eliminar_empleado.html', {'empleado': empleado})

def asignar_turno(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.empleado = empleado
            turno.save()
            return redirect(reverse('ver_turnos', kwargs={'empleado_id': empleado_id}))
    else:
        form = TurnoForm()
    return render(request, 'asignar_turno.html', {'form': form, 'empleado': empleado})

def ver_turnos(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    turnos = Turno.objects.filter(empleado=empleado)
    return render(request, 'ver_turnos.html', {'empleado': empleado, 'turnos': turnos})

def eliminar_turno(request, turno_id):
    turno = get_object_or_404(Turno, pk=turno_id)
    if request.method == 'POST':
        empleado_id = turno.empleado.id
        turno.delete()
        return redirect('ver_turnos', empleado_id=empleado_id)
    return render(request, 'eliminar_turno.html', {'turno': turno})

def editar_turno(request, turno_id):
    turno = get_object_or_404(Turno, pk=turno_id)
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            return redirect('ver_turnos', empleado_id=turno.empleado.id)
    else:
        form = TurnoForm(instance=turno)

    return render(request, 'editar_turno.html', {'form': form, 'turno': turno, 'empleado': turno.empleado})