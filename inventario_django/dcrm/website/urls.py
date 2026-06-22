from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('productos/', views.productos, name='productos'),
    path('categorias/', views.categorias, name='categorias'),
    path('clientes/', views.clientes, name='clientes'),
    path('ventas/', views.ventas, name='ventas'),
    path('record/<int:pk>/', views.customer_records, name='record'),
    path('record/<int:pk>/edit/', views.edit_record, name='edit_record'),
    path('record/<int:pk>/delete/', views.delete_record, name='delete_record'),
    path('agregar-usuario/', views.add_record, name='add_user'),
    path('add_record/', views.add_record, name='add_record'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('notificaciones/admin/', views.notificaciones_admin, name='notificaciones_admin'),
    path('notificaciones/organizador/', views.notificaciones_organizador, name='notificaciones_organizador'),
    path('notificaciones/usuario/', views.notificaciones_usuario, name='notificaciones_usuario'),
    path('notificaciones/crear/', views.notificacion_crear, name='notificacion_crear'),
    path('notificaciones/<int:pk>/editar/', views.notificacion_editar, name='notificacion_editar'),
    path('notificaciones/<int:pk>/eliminar/', views.notificacion_eliminar, name='notificacion_eliminar'),
    path('notificaciones/<int:pk>/detalle/', views.notificacion_detalle, name='notificacion_detalle'),
    path('notificaciones/<int:pk>/leida/', views.notificacion_marcar_leida, name='notificacion_marcar_leida'),
    path('notificaciones/todas-leidas/', views.notificaciones_marcar_todas_leidas, name='notificaciones_marcar_todas_leidas'),
]