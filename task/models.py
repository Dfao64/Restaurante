from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    numero_telefono = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'direccion', 'numero_telefono']

    def __str__(self):
        return self.email
    
TIPO_PRODUCTO = [
    ('comida', 'Comida'),
    ('bebida', 'Bebida'),
]

class Producto(models.Model):
    
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPO_PRODUCTO)
    imagen = models.ImageField(upload_to='productos/', null =True, blank=True)

    def __str__(self):
        return self.nombre
    
class Carrito(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.producto.nombre} ({self.cantidad})"

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.carrito.user.email} - {self.producto.nombre} ({self.cantidad})"
    
class Empleado(models.Model):
    TIPO_CHOICES = [
        ('Cocinero', 'Cocinero'),
        ('Domiciliario', 'Domiciliario'),
        ('Cajero', 'Cajero'),
    ]
    nombre_completo = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=255)
    tipo_empleado = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return f"{self.nombre_completo} - {self.tipo_empleado}"
    
class Turno(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.fecha} ({self.hora_inicio} - {self.hora_fin})"
    
class Pedido(models.Model):
    producto_nombre = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    alergias = models.TextField(null=True, blank=True)  
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.producto_nombre} x {self.cantidad}"