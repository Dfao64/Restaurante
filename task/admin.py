from django.contrib import admin
from .models import CustomUser, Producto, Carrito, Pedido, Turno, Empleado

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Producto)
admin.site.register(Carrito)
admin.site.register(Pedido)
admin.site.register(Turno)
admin.site.register(Empleado)