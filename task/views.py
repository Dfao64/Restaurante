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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.utils.timezone import now, timedelta
from django.utils.timezone import localdate
from django.template.loader import render_to_string
from django.http import HttpResponse
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import render
from .models import Pedido
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum
from datetime import timedelta
from .models import Pedido
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import localdate
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from django.http import HttpResponse
from django.template.defaultfilters import date as date_filter
from reportlab.lib.units import inch

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
                    cliente=request.user,
                    producto_nombre=item.producto.nombre,
                    cantidad=item.cantidad,
                    precio_total=item.producto.precio * item.cantidad,
                    metodo='Recoger en tienda',
                    alergias=alergias,
                    estado='En cocina'
                )
            items.delete()
            carrito.delete()
            pago_exitoso = True  # ✅ Activa el SweetAlert
            form = FormularioPagoTarjeta()  # Limpia el formulario
    else:
        form = FormularioPagoTarjeta()

    return render(request, 'pago_recoger.html', {'form': form, 'pago_exitoso': pago_exitoso})

def pago_domicilio(request):   
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
        form = FormularioPagoDomicilio(request.POST)
        if form.is_valid():
            alergias = form.cleaned_data.get('alergias', '')
            for item in items:
                Pedido.objects.create(
                    cliente=request.user,
                    producto_nombre=item.producto.nombre,
                    cantidad=item.cantidad,
                    precio_total=item.producto.precio * item.cantidad,
                    metodo='Domicilio',
                    direccion=form.cleaned_data['direccion'],
                    alergias=alergias,
                    estado='En cocina1'
                )
            items.delete()
            carrito.delete()
            pago_exitoso = True  # ✅ Activa el SweetAlert
            form = FormularioPagoDomicilio()  # Limpia el formulario
    else:
        form = FormularioPagoDomicilio()

    return render(request, 'pago_domicilio.html', {'form': form, 'pago_exitoso': pago_exitoso})

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

@login_required
@user_passes_test(is_admin)
def pedidos_en_cocina(request):
    # Filtrar pedidos para recoger
    pedidos_para_recoger = Pedido.objects.filter(metodo='Recoger en tienda', estado__in=['En cocina', 'Listo para recoger']).order_by('cliente')

    # Filtrar pedidos a domicilio
    pedidos_domicilio = Pedido.objects.filter(metodo='Domicilio', estado='En cocina1').order_by('cliente')

    # Agrupar los pedidos por cliente para cada tipo
    pedidos_para_recoger_por_cliente = {}
    for pedido in pedidos_para_recoger:
        pedidos_para_recoger_por_cliente.setdefault(pedido.cliente, []).append(pedido)

    pedidos_domicilio_por_cliente = {}
    for pedido in pedidos_domicilio:
        pedidos_domicilio_por_cliente.setdefault(pedido.cliente, []).append(pedido)

    # Renderizamos el template con ambos filtros
    return render(request, 'pedidos_en_cocina.html', {
        'pedidos_para_recoger_por_cliente': pedidos_para_recoger_por_cliente,
        'pedidos_domicilio_por_cliente': pedidos_domicilio_por_cliente
    })

    
    
@login_required
@user_passes_test(is_admin)   
def marcar_listo_para_recoger(request, cliente_id):
    if request.method == 'POST':
        cliente = get_object_or_404(get_user_model(), id=cliente_id)
        pedidos = Pedido.objects.filter(cliente=cliente, estado='En cocina').update(estado='Listo para recoger')
    return redirect('pedidos_en_cocina')

@login_required
@user_passes_test(is_admin)
def marcar_entregado(request, cliente_id):
    Pedido.objects.filter(cliente=cliente_id, estado='Listo para recoger').update(estado='Entregado')
    return redirect('pedidos_en_cocina')

def mis_pedidos(request):
    pedidos_activos = Pedido.objects.filter(cliente=request.user).exclude(estado='Entregado')
    historial_pedidos = Pedido.objects.filter(cliente=request.user, estado='Entregado')
    return render(request, 'mis_pedidos.html', {
        'pedidos_activos': pedidos_activos,
        'historial_pedidos': historial_pedidos
    })

@login_required
@user_passes_test(is_admin)
def pedidos_domicilio(request):
    pedidos = Pedido.objects.filter(metodo='Domicilio',estado__in=['En cocina1', 'Enviado'])

    pedidos_por_cliente = {}
    for pedido in pedidos:
        if pedido.cliente not in pedidos_por_cliente:
            pedidos_por_cliente[pedido.cliente] = []
        pedidos_por_cliente[pedido.cliente].append(pedido)
        
    return render(request, 'pedidos_domicilio.html', {
        'pedidos_por_cliente': pedidos_por_cliente
    })

@login_required
@user_passes_test(is_admin)
def marcar_enviado(request, cliente_id):
    if request.method == 'POST':
        cliente = get_object_or_404(get_user_model(), id=cliente_id)
        pedidos = Pedido.objects.filter(cliente=cliente, estado='En cocina1').update(estado='Enviado')
    return redirect('pedidos_en_cocina')    

@login_required
@user_passes_test(is_admin)
def dashboard_admin(request):
    hoy = localdate()
    manana = hoy + timedelta(days=1)
    hace_7_dias = hoy - timedelta(days=7)

    # Ventas del día (rango desde hoy hasta mañana)
    ventas_diarias = (
        Pedido.objects
        .filter(fecha__gte=hoy, fecha__lt=manana)
        .aggregate(total=Sum('precio_total'))['total'] or 0
    )

    # Ventas de la semana (últimos 7 días)
    ventas_semanales = (
        Pedido.objects
        .filter(fecha__gte=hace_7_dias, fecha__lt=manana)
        .aggregate(total=Sum('precio_total'))['total'] or 0
    )

    # Platos más vendidos
    platos_populares = list(
        Pedido.objects
        .values('producto_nombre')
        .annotate(total_vendidos=Sum('cantidad'))
        .order_by('-total_vendidos')[:5]
    )

    context = {
        'ventas_diarias': ventas_diarias,
        'ventas_semanales': ventas_semanales,
        'platos_populares': platos_populares,
    }

    return render(request, 'dashboard_admin.html', context)

@login_required
@user_passes_test(is_admin)
def descargar_reporte_pdf(request):
    hoy = localdate()
    manana = hoy + timedelta(days=1)
    hace_7_dias = hoy - timedelta(days=7)
    
    ventas_diarias = (
        Pedido.objects
        .filter(fecha__gte=hoy, fecha__lt=manana)
        .aggregate(total=Sum('precio_total'))['total'] or 0
    )
    
    ventas_semanales = (
        Pedido.objects
        .filter(fecha__gte=hace_7_dias, fecha__lt=manana)
        .aggregate(total=Sum('precio_total'))['total'] or 0
    )
    
    platos_populares = list(
        Pedido.objects
        .values('producto_nombre')
        .annotate(total_vendidos=Sum('cantidad'))
        .order_by('-total_vendidos')[:5]
    )
    
    # Crear la respuesta del PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{hoy}.pdf"'
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []

    # Agregar un título al PDF
    title_style = ParagraphStyle(name="Title", fontSize=16, alignment=1, spaceAfter=12, fontName="Helvetica-Bold")
    title = Paragraph(f"Reporte de ventas - {hoy}", title_style)
    story.append(title)

    # Agregar la información de ventas diarias y semanales
    info_style = getSampleStyleSheet()['Normal']
    info_paragraph = Paragraph(f"<b>Ventas del día:</b> ${ventas_diarias} <br /><b>Ventas semanales:</b> ${ventas_semanales}", info_style)
    story.append(info_paragraph)

    # Agregar los platos populares
    story.append(Paragraph("<b>Platos más vendidos:</b>", info_style))
    
    # Preparar los datos para la tabla
    data = [['Producto', 'Cantidad vendida']]  # Cabecera de la tabla
    for plato in platos_populares:
        data.append([plato['producto_nombre'], plato['total_vendidos']])
    
    # Crear la tabla
    table = Table(data, colWidths=[4*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('SIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    # Agregar la tabla al PDF
    story.append(table)

    # Crear el documento
    doc.build(story)
    
    return response