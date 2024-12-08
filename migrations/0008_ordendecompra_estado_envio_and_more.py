# Generated by Django 5.1.3 on 2024-12-07 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitio', '0007_detalleorden_fecha_creacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordendecompra',
            name='estado_envio',
            field=models.CharField(blank=True, default='En espera', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='ordendecompra',
            name='estado_retiro',
            field=models.CharField(blank=True, default='No retirado', max_length=50, null=True),
        ),
    ]
