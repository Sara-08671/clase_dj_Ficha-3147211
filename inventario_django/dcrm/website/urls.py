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
]
