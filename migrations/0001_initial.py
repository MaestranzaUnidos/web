# Generated by Django 5.0.6 on 2024-10-07 21:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id_categoria', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id_metadata', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=255, null=True)),
                ('keyword', models.TextField()),
                ('correo', models.CharField(max_length=255)),
                ('telefono', models.CharField(max_length=255)),
                ('titulo', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id_proveedor', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.CharField(max_length=200)),
                ('telefono', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id_carrito', models.AutoField(primary_key=True, serialize=False)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('usuario', models.OneToOneField(db_column='usuario_id', on_delete=django.db.models.deletion.CASCADE, related_name='carrito', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrdenDeCompra',
            fields=[
                ('id_orden', models.AutoField(primary_key=True, serialize=False)),
                ('numero_orden', models.CharField(editable=False, max_length=100, unique=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(default='Pendiente', max_length=50)),
                ('usuario', models.ForeignKey(db_column='usuario_id', on_delete=django.db.models.deletion.CASCADE, related_name='ordenes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id_producto', models.AutoField(primary_key=True, serialize=False)),
                ('titulo', models.CharField(max_length=50)),
                ('imagen', models.FileField(upload_to='imagenes/productos/')),
                ('descripcion', models.CharField(max_length=200)),
                ('precio', models.IntegerField(verbose_name='Precio')),
                ('stock', models.PositiveBigIntegerField(default=0, verbose_name='Stock')),
                ('alerta_stock', models.BooleanField(default=False)),
                ('agregado', models.BooleanField(default=False)),
                ('fecha_vencimiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')),
                ('categoria', models.ForeignKey(db_column='id_categoria', on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='sitio.categoria')),
                ('proveedor', models.ForeignKey(blank=True, db_column='id_proveedor', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='sitio.proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='HistorialPrecio',
            fields=[
                ('id_historial', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('precio', models.IntegerField()),
                ('producto', models.ForeignKey(db_column='id_producto', on_delete=django.db.models.deletion.CASCADE, related_name='historial_precios', to='sitio.producto')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleOrden',
            fields=[
                ('id_detalle_orden', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.PositiveIntegerField()),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('orden', models.ForeignKey(db_column='id_orden', on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='sitio.ordendecompra')),
                ('producto', models.ForeignKey(db_column='id_producto', on_delete=django.db.models.deletion.CASCADE, to='sitio.producto')),
            ],
        ),
        migrations.CreateModel(
            name='Carrito_item',
            fields=[
                ('id_carrito_item', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.IntegerField(default=1)),
                ('carrito', models.ForeignKey(db_column='id_carrito', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='sitio.carrito')),
                ('producto', models.ForeignKey(db_column='id_producto', on_delete=django.db.models.deletion.CASCADE, to='sitio.producto')),
            ],
        ),
    ]
