from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.db.models.signals import pre_save
from django.dispatch import receiver

### Modelo de Proveedores
class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)  # Personalización del ID
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

### Modelo de Categorías
class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)  # Personalización del ID
    descripcion = models.CharField(max_length=200, null=False)

    def __str__(self) -> str:
        return f"Id: {self.id_categoria} | Descripcion: {self.descripcion}"

### Modelo de Productos
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)  # Personalización del ID
    titulo = models.CharField(max_length=50, null=False)
    imagen = models.FileField(upload_to='imagenes/productos/')
    descripcion = models.CharField(max_length=200, null=False)
    precio = models.IntegerField(verbose_name='Precio')
    stock = models.PositiveBigIntegerField(default=0, verbose_name='Stock')
    alerta_stock = models.BooleanField(default=False)
    agregado = models.BooleanField(default=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos", db_column='id_categoria')
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de Vencimiento')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="productos", null=True, blank=True, db_column='id_proveedor')

    def __str__(self) -> str:
        return f"Id: {self.id_producto} | Titulo: {self.titulo} | Precio: {self.precio} | Stock: {self.stock}"

    @property
    def esta_vencido(self):
        if self.fecha_vencimiento:
            return date.today() > self.fecha_vencimiento
        return False

    @property
    def proximo_a_vencer(self):
        if self.fecha_vencimiento:
            return date.today() + timedelta(days=30) >= self.fecha_vencimiento
        return False
    

### Modelo de Carrito y CarritoItem
class Carrito(models.Model):
    id_carrito = models.AutoField(primary_key=True)  # Personalización del ID
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="carrito", db_column='usuario_id')
    total = models.DecimalField(null=False, max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"Carrito de {self.usuario.username} - Total: {self.total}"

class Carrito_item(models.Model):
    id_carrito_item = models.AutoField(primary_key=True)  # Personalización del ID
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="items", db_column='id_carrito')
    cantidad = models.IntegerField(default=1)

    def __str__(self) -> str:
        return f"Producto: {self.producto.titulo} - Cantidad: {self.cantidad}"

### Historial de Precios
class HistorialPrecio(models.Model):
    id_historial = models.AutoField(primary_key=True)  # Personalización del ID
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="historial_precios", db_column='id_producto')
    fecha = models.DateTimeField(auto_now_add=True)
    precio = models.IntegerField()

    def __str__(self):
        return f"Producto: {self.producto.titulo} | Fecha: {self.fecha} | Precio: {self.precio}"

# Registrar cambios en el precio de un producto
@receiver(pre_save, sender=Producto)
def registrar_historial_precio(sender, instance, **kwargs):
    if instance.pk:  # Verificar si el producto ya existe en la base de datos
        try:
            producto_anterior = Producto.objects.get(pk=instance.pk)
            if producto_anterior.precio != instance.precio:  # Comprobar cambio en el precio
                HistorialPrecio.objects.create(producto=instance, precio=instance.precio)
        except Producto.DoesNotExist:
            pass  # Si el producto no existe, no hacer nada
        
### Modelo de Dirección de Envío
class DireccionEnvio(models.Model):
    REGION_METROPOLITANA = 'Metropolitana'
    
    REGION_CHOICES = [
        (REGION_METROPOLITANA, 'Región Metropolitana'),
    ]
    
    COMUNA_CHOICES = [
        ('Cerrillos', 'Cerrillos'),
        ('Cerro Navia', 'Cerro Navia'),
        ('Conchalí', 'Conchalí'),
        ('El Bosque', 'El Bosque'),
        ('Estación Central', 'Estación Central'),
        ('Huechuraba', 'Huechuraba'),
        ('Independencia', 'Independencia'),
        ('La Cisterna', 'La Cisterna'),
        ('La Florida', 'La Florida'),
        ('La Granja', 'La Granja'),
        ('La Pintana', 'La Pintana'),
        ('La Reina', 'La Reina'),
        ('Las Condes', 'Las Condes'),
        ('Lo Barnechea', 'Lo Barnechea'),
        ('Lo Espejo', 'Lo Espejo'),
        ('Lo Prado', 'Lo Prado'),
        ('Macul', 'Macul'),
        ('Maipú', 'Maipú'),
        ('Ñuñoa', 'Ñuñoa'),
        ('Pedro Aguirre Cerda', 'Pedro Aguirre Cerda'),
        ('Peñalolén', 'Peñalolén'),
        ('Providencia', 'Providencia'),
        ('Pudahuel', 'Pudahuel'),
        ('Quilicura', 'Quilicura'),
        ('Quinta Normal', 'Quinta Normal'),
        ('Recoleta', 'Recoleta'),
        ('Renca', 'Renca'),
        ('San Joaquín', 'San Joaquín'),
        ('San Miguel', 'San Miguel'),
        ('San Ramón', 'San Ramón'),
        ('Santiago', 'Santiago'),
        ('Vitacura', 'Vitacura'),

    ]

    id_direccion = models.AutoField(primary_key=True)  # Campo autoincremental para el identificador
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="direcciones_envio")
    direccion = models.CharField(max_length=255)
    region = models.CharField(max_length=50, choices=REGION_CHOICES)

    def __str__(self):
        return f"{self.direccion}, {self.region},{self.REGION_CHOICES} ({self.usuario.username})"

    
### Orden de Compra y Detalle de la Orden
class OrdenDeCompra(models.Model):
    id_orden = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ordenes")
    direccion_envio = models.ForeignKey(DireccionEnvio, on_delete=models.CASCADE, related_name="ordenes", null=True, blank=True)  # Permitir valores nulos
    numero_orden = models.CharField(max_length=100, unique=True, editable=False)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default="Pendiente")  # Estado general
    estado_retiro = models.CharField(max_length=50, null=True, blank=True, default="No retirado")  # Para pedidos de retiro
    estado_envio = models.CharField(max_length=50, null=True, blank=True, default="En espera")  # Para pedidos de envío a domicilio
    def __str__(self):
        return f"Orden {self.numero_orden} - {self.usuario.username}"

    def save(self, *args, **kwargs):
        if not self.numero_orden:
            self.numero_orden = f"ORDEN-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super(OrdenDeCompra, self).save(*args, **kwargs)

class DetalleOrden(models.Model):
    id_detalle_orden = models.AutoField(primary_key=True)  # Personalización del ID
    orden = models.ForeignKey(OrdenDeCompra, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(default=now)

    def __str__(self):
        return f"Detalle de {self.producto.titulo} en la orden {self.orden.numero_orden}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    

### Metadata
class Metadata(models.Model):
    id_metadata = models.AutoField(primary_key=True)  # Personalización del ID
    description = models.CharField(max_length=255, null=True)
    keyword = models.TextField()
    correo = models.CharField(max_length=255)
    telefono = models.CharField(max_length=255)
    titulo = models.CharField(max_length=255)

    def __str__(self):
        return self.titulo
### DIRECCIONES

