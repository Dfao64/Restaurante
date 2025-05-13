"""
URL configuration for restaurante project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from task import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login.as_view(), name='login'),
    path('vista_cliente/', views.vista_cliente, name='vista_cliente'),
    path('vista_administrador/', views.vista_administrador, name='vista_administrador'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('logout/', views.signout, name='logout'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('crear_producto/', views.crear_producto, name='crear_producto'),
    path('editar_producto/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('eliminar_producto/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('catalogo_cliente/', views.catalogo_cliente, name='catalogo_cliente'),
    path('agregar_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito_compras/', views.ver_carrito, name='carrito_compras'),
    path('pago_recoger/', views.pago_recoger, name='pago_recoger'),
    path('pago_domicilio/', views.pago_domicilio, name='pago_domicilio'),
    path('lista_empleado/', views.lista_empleado, name='lista_empleado'),
    path('crear_empleado/', views.crear_empleado, name='crear_empleado'),
    path('editar_empleado/<int:pk>/', views.editar_empleado, name='editar_empleado'),
    path('eliminar_empleado/<int:pk>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('asignar_turno/<int:empleado_id>/', views.asignar_turno, name='asignar_turno'),
    path('ver_turnos/<int:empleado_id>/', views.ver_turnos, name='ver_turnos'),
    path('eliminar_turno/<int:turno_id>/', views.eliminar_turno, name='eliminar_turno'),
    path('editar_turno/<int:turno_id>/', views.editar_turno, name='editar_turno'),
    path('pedidos_en_cocina/', views.pedidos_en_cocina, name='pedidos_en_cocina'),
    path('marcar_listo_para_recoger/<int:cliente_id>/', views.marcar_listo_para_recoger, name='marcar_listo_para_recoger'),
    path('marcar_entregado/<int:cliente_id>/', views.marcar_entregado, name='marcar_entregado'),
    path('mis_pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedidos_domicilio/', views.pedidos_domicilio, name='pedidos_domicilio'),
    path('marcar_enviado/<int:cliente_id>/', views.marcar_enviado, name='marcar_enviado'),
    path('dashboard_admin/', views.dashboard_admin, name='dashboard_admin'),
    path('descargar_reporte_pdf/', views.descargar_reporte_pdf, name='descargar_reporte_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)