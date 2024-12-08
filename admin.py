from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Categoria)
admin.site.register(Carrito)
admin.site.register(Carrito_item)

from django.contrib import admin
from .models import Proveedor, Producto

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono', 'email')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'precio', 'stock', 'fecha_vencimiento', 'proveedor', 'categoria')
    list_filter = ('categoria', 'proveedor', 'fecha_vencimiento')
    search_fields = ('titulo', 'descripcion')
