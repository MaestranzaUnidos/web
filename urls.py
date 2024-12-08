from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "SITIO"  # Nombre del namespace

urlpatterns = [
    path('categorias/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    # Compras por fecha 
    path('compras_por_fecha/', views.compras_por_fecha, name='compras_por_fecha'),
    # Registro y autenticación de usuarios
    path('registrarse/', views.register, name="register"),  # Registro de usuarios
    path('logout/', views.logged_out, name='logout'),  # Cierre de sesión

    # Proveedores
    path('proveedores/', views.proveedores_productos, name='proveedores_productos'),  # Listado de proveedores
    path('proveedores_productos/', views.proveedores_productos, name='proveedores_productos'),

    # Gestión de productos
    path('', views.producto_index, name="producto_index"),  # Página de inicio / listado de productos
    path('producto/agregar', views.producto_create, name="producto_create"),  # Crear nuevo producto
    path('producto/<int:producto_id>/', views.producto_show, name="producto_show"),  # Detalle de un producto
    path('producto/<int:producto_id>/editar/', views.producto_edit, name="producto_edit"),  # Editar un producto
    path('producto/<int:producto_id>/eliminar/', views.producto_delete, name="producto_delete"),  # Eliminar un producto
    path('producto/buscador/', views.producto_search, name="producto_search"),  # Buscar productos
    path('categoria/<int:categoria_id>/productos/', views.productos_por_categoria, name="productos_por_categoria"),  # Filtrar productos por categoría
    path('producto_list/', views.producto_list, name='producto_list'),  # Listado de productos
    path('informe-inventario/', views.generar_informe_inventario, name='informe_inventario'),  # Informe de inventario
    path('historial_precios/<int:producto_id>/', views.historial_precios, name='historial_precios'),
    path('mis_pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('actualizar_estado/<int:id_orden>/', views.actualizar_estado, name='actualizar_estado'),
    path('detalle_pedido/<int:id_pedido>/', views.detalle_pedido, name='detalle_pedido'),
    
    # Gestión del carrito de compras
    path('carrito/', views.carrito_index, name="carrito_index"),  # Ver el carrito
    path('carrito/agregar/', views.carrito_save, name="carrito_save"),  # Agregar producto al carrito
    path('carrito/clean/', views.carrito_clean, name="carrito_clean"),  # Vaciar carrito
    path('carrito/<int:item_id>/update/', views.update_item_quantity, name="update_item_quantity"),  # Actualizar cantidad de ítem
    path('item_carrito/<int:item_carrito_id>/eliminar/', views.item_carrito_delete, name="item_carrito_delete"),  # Eliminar un ítem del carrito
    path('carrito/seleccionar_envio/', views.seleccionar_envio, name='seleccionar_envio'),
    
    # Proceso de pago con Transbank y confirmación de compra
    path('pago/iniciar/<int:orden_id>/', views.iniciar_pago, name='iniciar_pago'),  # Iniciar proceso de pago con el ID de la orden
    path('pago/retorno/', views.pago_retorno, name='pago_retorno'),  # Retorno de la pasarela de pago
    path('pago/confirmar/', views.confirmar_compra, name='confirmar_compra'),  # Confirmación de compra (dirección de envío)
]
