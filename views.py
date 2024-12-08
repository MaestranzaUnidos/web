from django.contrib.auth.models import User
from sitio.forms import FormProducto, DireccionEnvioForm  # Importar el formulario de Dirección de Envío
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito, Carrito_item, Categoria, Proveedor, OrdenDeCompra, DetalleOrden, DireccionEnvio  # Importar el modelo de Dirección de Envío
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
from sitio.utilidades.compras import procesar_compra
from datetime import datetime
from django.db.models.functions import Cast
from django.db.models import DateField, Prefetch, Sum
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required

""" 
    REGISTRO DE USUARIO
"""
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            usuario_logeado = User.objects.last()
            messages.success(request, "El usuario ha sido registrado exitosamente!")
            
            carrito = Carrito(usuario=usuario_logeado, total=0)
            carrito.save()

            return redirect('SITIO:producto_index')
        else:
            messages.error(request, "No se pudo registrar el usuario, intente nuevamente.")
    return render(request, 'sitio/register.html')

def logged_out(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('SITIO:producto_index')

"""
    PRODUCTOS
"""
def producto_index(request):
    productos = Producto.objects.all().order_by("-id_producto")
    return render(request, "sitio/producto/index.html", {
        'categorias': Categoria.objects.all(),
        'productos_top3': productos[:3],
        'productos': productos[3:10]
    })

def index(request):
    # Obtener los productos más vendidos
    productos_mas_vendidos = Producto.objects.annotate(
        total_vendido=Sum('detalleorden__cantidad')
    ).order_by('-total_vendido')[:3]  # Los 3 más vendidos

    # Otros productos
    productos = Producto.objects.all().exclude(
        id_producto__in=[p.id_producto for p in productos_mas_vendidos]
    )[:6]  # Excluir los ya mostrados

    return render(request, 'sitio/index.html', {
        'productos_top3': productos_mas_vendidos,
        'productos': productos,
    })

"""
    COMPRAS POR FECHA
"""

def compras_por_fecha(request):
    categorias = Categoria.objects.all()
    fecha = request.GET.get('fecha', None)
    ordenes = []
    total_compras = 0  # Inicializamos el total

    if fecha:
        try:
            # Convertir la fecha a formato compatible con la base de datos
            fecha_formateada = datetime.strptime(fecha, "%Y-%m-%d").date()

            # Filtrar órdenes por fecha y estado "Pagado"
            ordenes = OrdenDeCompra.objects.annotate(
                fecha_sin_hora=Cast('fecha_creacion', DateField())
            ).filter(
                fecha_sin_hora=fecha_formateada, estado="Pagado"
            ).prefetch_related(
                Prefetch('detalles', queryset=DetalleOrden.objects.select_related('producto'))
            )

            # Calcular el total de las compras del día
            total_compras = ordenes.aggregate(Sum('total'))['total__sum'] or 0
        except ValueError:
            pass  # Manejar errores de fecha si es necesario

    context = {
        'categorias': categorias,
        'ordenes': ordenes,
        'fecha': fecha,
        'total_compras': total_compras,  # Pasamos el total al contexto
    }
    return render(request, 'sitio/compras_por_fecha.html', context)


def finalizar_compra(request):
    if request.method == "POST":
        direccion_envio_id = request.POST.get("direccion_envio")
        direccion_envio = DireccionEnvio.objects.get(id=direccion_envio_id, usuario=request.user)
        procesar_compra(request.user, direccion_envio)
        return redirect("confirmar_compra")


def producto_list(request):
    productos_agregados = Producto.objects.filter(agregado=True)
    return render(request, "sitio/producto/producto_list.html", {'productos': productos_agregados})

def producto_create(request):
    categorias = Categoria.objects.all()
    if request.method == "POST":
        categoria_del_producto = Categoria.objects.get(id_categoria=request.POST["categoria"])
        form = FormProducto(request.POST, request.FILES, instance=Producto(imagen=request.FILES['imagen'], categoria=categoria_del_producto))
        
        if form.is_valid():
            producto = form.save(commit=False)
            producto.stock = request.POST['stock']
            producto.save()
            messages.success(request, "Producto agregado exitosamente.")
            return redirect("SITIO:producto_index")
        else:
            return render(request, 'sitio/producto/create.html', {
                'categorias': categorias,
                'error_message': 'Ingreso un campo incorrecto, vuelva a intentar'
            })
    else:
        return render(request, 'sitio/producto/create.html', {'categorias': categorias})

def producto_show(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    return render(request, 'sitio/producto/show.html', {
        'categorias': Categoria.objects.all(),
        'producto': producto,
        'categoria_actual': producto.categoria  # Agrega la categoría del producto
    })

def producto_edit(request, producto_id):
    categorias = Categoria.objects.all()
    producto = Producto.objects.get(id_producto=producto_id)

    if request.method == "POST":
        categoria_del_producto = Categoria.objects.get(id_categoria=request.POST["categoria"])
        form = FormProducto(request.POST, request.FILES, instance=producto)

        if form.is_valid():
            producto.titulo = request.POST['titulo']
            producto.categoria = categoria_del_producto
            producto.descripcion = request.POST['descripcion']
            
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']

            producto.stock = int(request.POST['stock'])
            producto.precio = request.POST['precio']
            producto.save()

            messages.success(request, "Producto actualizado correctamente.")
            return redirect("SITIO:producto_index")
        else:
            return render(request, 'sitio/producto/edit.html', {
                'categorias': categorias,
                'producto': producto,
                'error_message': 'Ingreso un campo incorrecto, vuelva a intentar'
            })
    else:
        return render(request, 'sitio/producto/edit.html', {
            'categorias': categorias,
            'producto': producto
        })

def producto_delete(request, producto_id):
    producto = Producto.objects.get(id_producto=producto_id)
    producto.delete()
    return redirect('SITIO:producto_index')

def producto_search(request):
    texto_de_busqueda = request.GET.get("texto", "").strip()  # Asegúrate de manejar búsquedas vacías
    productos = Producto.objects.filter(titulo__icontains=texto_de_busqueda)

    return render(request, 'sitio/producto/search.html', {
        'categorias': Categoria.objects.all(),
        'productos': productos,
        'texto_buscado': texto_de_busqueda,
        'titulo_seccion': 'Productos que contienen',
        'sin_productos': f'No hay productos que coincidan con "{texto_de_busqueda}"'
    })


def productos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
    productos = categoria.productos.all()
    return render(request, 'sitio/producto/search.html', {
        'categorias': Categoria.objects.all(),
        'productos': productos,
        'categoria': categoria.descripcion,
        'titulo_seccion': 'Productos de la categoría',
        'sin_productos': f'No hay producto de la categoría {categoria.descripcion}'
    })

"""
    CARRITO
"""
@login_required
def carrito_index(request):
    categorias = Categoria.objects.all()
    usuario_logeado = request.user
    carrito, created = Carrito.objects.get_or_create(usuario=usuario_logeado)

    items_carrito = carrito.items.all()

    for item in items_carrito:
        item.subtotal = item.producto.precio * item.cantidad

    carrito.total = sum(item.subtotal for item in items_carrito)
    carrito.save()

    return render(request, 'sitio/carrito/index.html', {
        'categorias': categorias,
        'usuario': usuario_logeado,
        'items_carrito': items_carrito,
        'carrito': carrito,
    })

@login_required
def carrito_save(request):
    if request.method == 'POST':
        producto = Producto.objects.get(id_producto=request.POST['producto_id'])

        if producto.stock <= 0:
            messages.error(request, f"El producto {producto.titulo} no tiene stock disponible.")
            return redirect('SITIO:producto_index')

        usuario_logeado = request.user
        carrito, created = Carrito.objects.get_or_create(usuario=usuario_logeado)

        item_carrito, created = Carrito_item.objects.get_or_create(carrito=carrito, producto=producto)

        if created:
            item_carrito.cantidad = 1
        else:
            item_carrito.cantidad += 1

        item_carrito.save()
        carrito.total += producto.precio
        carrito.save()

        messages.success(request, f"El producto {producto.titulo} fue agregado al carrito")
        return redirect('SITIO:carrito_index')
    else:
        return redirect("SITIO:producto_index")

@login_required
def update_item_quantity(request, item_id):
    if request.method == 'POST':
        item_carrito = get_object_or_404(Carrito_item, id_carrito_item=item_id)
        nueva_cantidad = int(request.POST['cantidad'])

        if nueva_cantidad > item_carrito.producto.stock:
            messages.error(request, f"No puedes agregar más de {item_carrito.producto.stock} unidades de {item_carrito.producto.titulo}.")
            return redirect('SITIO:carrito_index')

        item_carrito.cantidad = nueva_cantidad
        item_carrito.save()

        carrito = item_carrito.carrito
        carrito.total = sum(item.producto.precio * item.cantidad for item in carrito.items.all())
        carrito.save()

        messages.success(request, "Cantidad actualizada correctamente.")
        return redirect('SITIO:carrito_index')

"""
    PROCESO DE PAGO
"""
@login_required
def iniciar_pago(request, orden_id):
    usuario_logeado = request.user
    orden = get_object_or_404(OrdenDeCompra, id_orden=orden_id, usuario=usuario_logeado)

    total = float(orden.total)

    if total <= 0:
        messages.error(request, "El total de la compra es inválido. No puedes proceder al pago.")
        return redirect('SITIO:carrito_index')

    # Llamada a la API de Transbank
    url = f"{settings.TRANSBANK['API_BASE_URL']}/transactions"
    headers = {
        "Tbk-Api-Key-Id": settings.TRANSBANK['COMMERCE_CODE'],
        "Tbk-Api-Key-Secret": settings.TRANSBANK['API_KEY'],
        "Content-Type": "application/json"
    }
    body = {
        "buy_order": orden.numero_orden,
        "session_id": f"session_{usuario_logeado.id}",
        "amount": total,
        "return_url": settings.TRANSBANK['RETURN_URL']  # URL de retorno después del pago
    }

    try:
        # Realizar la solicitud POST a la API de Transbank
        response = requests.post(url, json=body, headers=headers)
        response_data = response.json()

        # Verificar la respuesta de la API
        if response.status_code == 200 and 'url' in response_data and 'token' in response_data:
            # Redirigir a la URL de pago de Transbank con el token de sesión
            return redirect(f"{response_data['url']}?token_ws={response_data['token']}")
        else:
            messages.error(request, f"Error en la respuesta de Transbank: {response_data}")
            return redirect('SITIO:carrito_index')

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Ocurrió un error al comunicarse con Transbank: {e}")
        return redirect('SITIO:carrito_index')


from .forms import DireccionEnvioForm
from .models import DireccionEnvio, OrdenDeCompra, Carrito
@login_required
def confirmar_compra(request):
    usuario = request.user
    carrito = Carrito.objects.get(usuario=usuario)

    # Verifica si el carrito tiene productos
    if carrito.items.count() == 0:
        messages.error(request, "No puedes realizar la compra. No tienes productos en el carrito.")
        return redirect('SITIO:carrito_index')

    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            direccion_envio = form.save(commit=False)
            direccion_envio.usuario = usuario
            direccion_envio.save()

            # Crear la orden de compra
            orden = OrdenDeCompra.objects.create(
                usuario=usuario,
                direccion_envio=direccion_envio,
                total=carrito.total,
                estado="Pendiente"
            )

            # Crear los detalles de la orden y descontar el stock de cada producto
            for item in carrito.items.all():
                producto = item.producto

                if producto.stock < item.cantidad:
                    messages.error(request, f"No hay suficiente stock para {producto.titulo}.")
                    return redirect('SITIO:carrito_index')

                producto.stock -= item.cantidad
                producto.save()

                # Crear detalle de la orden
                DetalleOrden.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=item.cantidad,
                    precio_unitario=producto.precio
                )

            # Limpiar el carrito después de la compra
            carrito.items.all().delete()
            carrito.total = 0
            carrito.save()

            return redirect('SITIO:iniciar_pago', orden_id=orden.id_orden)

    else:
        form = DireccionEnvioForm()

    return render(request, 'sitio/confirmar_compra.html', {
        'form': form,
        'carrito': carrito,
    })



@login_required
def pago_retorno(request):
    token_ws = request.GET.get('token_ws')

    if not token_ws:
        return redirect('SITIO:producto_index')  # Redirige si no hay token

    # Confirmar la transacción en Transbank
    url = f"{settings.TRANSBANK['API_BASE_URL']}/transactions/{token_ws}"
    headers = {
        "Tbk-Api-Key-Id": settings.TRANSBANK['COMMERCE_CODE'],
        "Tbk-Api-Key-Secret": settings.TRANSBANK['API_KEY'],
        "Content-Type": "application/json"
    }

    response = requests.put(url, headers=headers)
    response_data = response.json()

    if response.status_code == 200 and response_data['status'] == 'AUTHORIZED':
        usuario = request.user
        try:
            carrito = Carrito.objects.get(usuario=usuario)
        except Carrito.DoesNotExist:
            messages.error(request, "No se encontró un carrito asociado a esta transacción.")
            return redirect('SITIO:carrito_index')  # O redirige a una página de error

        # Limpiar el carrito después del pago
        carrito.items.all().delete()
        carrito.total = 0
        carrito.save()

        # Actualizar el estado de la orden a "Pagado"
        orden = OrdenDeCompra.objects.get(numero_orden=response_data['buy_order'])
        orden.estado = "Pagado"
        orden.save()

        # Mostrar la página de retorno del pago
        return render(request, 'sitio/retorno_pago.html', {
            'usuario': usuario,
            'orden': orden,
            'response_data': response_data
        })

    messages.error(request, "Hubo un problema con el pago.")
    return redirect('SITIO:carrito_index')


@login_required
def carrito_clean(request):
    usuario_logeado = request.user
    carrito = Carrito.objects.get(usuario=usuario_logeado)
    carrito.items.all().delete()
    carrito.total = 0
    carrito.save()

    messages.success(request, "Carrito limpiado correctamente.")
    return redirect('SITIO:carrito_index')

@login_required
def item_carrito_delete(request, item_carrito_id):
    item_carrito = get_object_or_404(Carrito_item, id_carrito_item=item_carrito_id)
    carrito = item_carrito.carrito

    carrito.total -= item_carrito.producto.precio * item_carrito.cantidad
    item_carrito.delete()
    carrito.save()

    messages.success(request, "Producto eliminado del carrito.")
    return redirect("SITIO:carrito_index")

"""
    INFORME E HISTORIAL
"""
@login_required
def generar_informe_inventario(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.all()
    productos_bajo_stock = productos.filter(stock__lte=20)
    
    context = {
        'categorias': categorias,
        'productos': productos,
        'productos_bajo_stock': productos_bajo_stock,
    }
    return render(request, 'sitio/informe_inventario.html', context)

@login_required
def historial_precios(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    historial_precios = producto.historial_precios.all().order_by('-fecha')
    categorias = Categoria.objects.all()  # Obtiene todas las categorías para incluirlas en el contexto
    return render(request, 'sitio/historial_precios.html', {
        'producto': producto,
        'historial_precios': historial_precios,
        'categorias': categorias,  # Agrega las categorías al contexto
    })

def proveedores_productos(request):
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.prefetch_related('productos').all()

    context = {
        'categorias': categorias,  # Agregar categorías al contexto
        'proveedores' :proveedores,
    }
    return render(request, 'sitio/proveedores_productos.html', context)

#### seleccionar envio


@login_required
def seleccionar_envio(request):
    usuario = request.user
    carrito = Carrito.objects.get(usuario=usuario)

    # Verifica si el carrito tiene productos
    if carrito.items.count() == 0:
        messages.error(request, "No puedes proceder sin productos en el carrito.")
        return redirect('SITIO:carrito_index')

    if request.method == 'POST':
        opcion_envio = request.POST.get('opcion_envio')

        if opcion_envio == 'retiro':
            # Crear la orden para retiro en tienda sin dirección de envío
            orden = OrdenDeCompra.objects.create(
                usuario=usuario,
                direccion_envio=None,  # Retiro en tienda no necesita dirección
                total=carrito.total,
                estado="Pendiente"
            )

            # Descontar stock y crear detalles de la orden
            for item in carrito.items.all():
                producto = item.producto
                producto.stock -= item.cantidad
                producto.save()

                DetalleOrden.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=item.cantidad,
                    precio_unitario=producto.precio
                )

            # Limpiar carrito
            carrito.items.all().delete()
            carrito.total = 0
            carrito.save()

            # Redirigir al proceso de pago de Transbank
            return redirect('SITIO:iniciar_pago', orden_id=orden.id_orden)

        elif opcion_envio == 'despacho':
            return redirect('SITIO:confirmar_compra')

    return render(request, 'sitio/seleccionar_envio.html', {'carrito': carrito})

@login_required
def mis_pedidos(request):
    categorias = Categoria.objects.all()
    if request.user.is_superuser:
        # Si el usuario es superusuario, mostrar todos los pedidos
        pedidos_retiro = OrdenDeCompra.objects.filter(direccion_envio__isnull=True)
        pedidos_envio = OrdenDeCompra.objects.filter(direccion_envio__isnull=False)
    else:
        # Si no es superusuario, mostrar solo los pedidos del usuario autenticado
        pedidos_retiro = OrdenDeCompra.objects.filter(usuario=request.user, direccion_envio__isnull=True)
        pedidos_envio = OrdenDeCompra.objects.filter(usuario=request.user, direccion_envio__isnull=False)

    context = {
        'pedidos_retiro': pedidos_retiro,
        'pedidos_envio': pedidos_envio,
        'categorias': categorias,  # Agregar categorías al contexto
    }
    return render(request, 'sitio/mis_pedidos.html', context)

@staff_member_required
def actualizar_estado(request, id_orden):
    # Obtener la orden correspondiente
    orden = get_object_or_404(OrdenDeCompra, id_orden=id_orden)
    
    if request.method == 'POST':
        # Verificar si es un pedido para "Retiro en Tienda" o "Envío a Domicilio"
        if orden.direccion_envio is None:  # Pedido para Retiro en Tienda
            nuevo_estado = request.POST.get('estado_retiro')  # Campo del formulario
            if nuevo_estado:
                orden.estado_retiro = nuevo_estado
                orden.save()
                messages.success(request, "El estado del pedido para retiro en tienda se actualizó correctamente.")
        else:  # Pedido para Envío a Domicilio
            nuevo_estado_envio = request.POST.get('estado_envio')  # Campo del formulario
            if nuevo_estado_envio:
                orden.estado_envio = nuevo_estado_envio
                orden.save()
                messages.success(request, "El estado del pedido para envío a domicilio se actualizó correctamente.")
        
        # Redirigir a 'mis_pedidos' después de actualizar
        return redirect('SITIO:mis_pedidos')
    # Renderizar el formulario para actualizar el estado
    return render(request, 'sitio/actualizar_estado.html', {'orden': orden})
    
def detalle_pedido(request, id_pedido):
    pedido = get_object_or_404(OrdenDeCompra, id_orden=id_pedido)
    productos_ordenados = DetalleOrden.objects.filter(orden=pedido)
    return render(request, 'sitio/detalle_pedido.html', {
        'pedido': pedido,
        'productos_ordenados': productos_ordenados
    })