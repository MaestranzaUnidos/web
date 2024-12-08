from django.db import transaction
from sitio.models import Carrito, OrdenDeCompra, DetalleOrden

def procesar_compra(usuario, direccion_envio):
    with transaction.atomic():
        carrito = Carrito.objects.get(usuario=usuario)
        if carrito.items.exists():
            orden = OrdenDeCompra.objects.create(
                usuario=usuario,
                direccion_envio=direccion_envio,
                total=carrito.total
            )
            for item in carrito.items.all():
                DetalleOrden.objects.create(
                    orden=orden,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio
                )
                item.producto.stock -= item.cantidad
                item.producto.save()
            carrito.items.all().delete()
            carrito.total = 0
            carrito.save()
