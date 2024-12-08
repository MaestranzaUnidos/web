from .models import Producto

def productos_con_historial(request):
    productos_con_historial = Producto.objects.filter(historial_precios__isnull=False).distinct()
    return {'productos_con_historial': productos_con_historial}
