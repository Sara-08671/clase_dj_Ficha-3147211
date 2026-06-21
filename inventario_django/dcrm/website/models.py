from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User

# Modelo Registro: almacena información adicional de los usuarios
# Relacionado uno a uno con el modelo User de Django
class Record(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=58)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=20)
    Address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=20)

    #metodo para mostrar el nomnre compelto dek cliente y es tipo de encapsulado privado
    #se utiliza el metodo __str__ para devolver una representacion en forma de cadena del objeto
    def __str__(self) -> str:
        return (f"{self.first_name} {self.last_name}")

# Modelo Categoria: representa las categorías de productos
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

# Modelo Producto: representa los productos del inventario
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

# Modelo Cliente: representa los clientes del sistema
class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

# Modelo Venta: representa las ventas realizadas
class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='ventas')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Venta {self.id} - {self.cliente.nombre}"


class NotificacionManager(models.Manager):
    def para_usuario(self, user):
        return self.get_queryset().filter(
            Q(receptor__isnull=True) | Q(receptor=user)
        )


class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('info', 'Informativa'),
        ('aviso', 'Aviso'),
        ('alerta', 'Alerta'),
        ('recordatorio', 'Recordatorio'),
    ]

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='info'
    )
    titulo = models.CharField(max_length=80)
    mensaje = models.TextField()
    receptor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    creador = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='notificaciones_creadas',
        editable=False
    )
    leida = models.BooleanField(default=False)
    leida_en = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = NotificacionManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        destino = self.receptor.username if self.receptor else 'Todos'
        return f"{self.titulo} ({destino})"

    def es_global(self):
        return self.receptor is None

    def pertenece_a(self, user):
        return self.receptor is None or self.receptor_id == user.id

    def marcar_leida(self):
        if not self.leida:
            self.leida = True
            self.leida_en = timezone.now()
            self.save(update_fields=['leida', 'leida_en', 'updated_at'])

