# Generated by Django 5.2.1 on 2025-05-11 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0011_pedido_cliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='estado',
            field=models.CharField(choices=[('En cocina', 'En cocina'), ('En reparto', 'En reparto'), ('Entregado', 'Entregado'), ('Enviado', 'Enviado'), ('En reparto', 'En reparto')], default='En cocina', max_length=20),
        ),
    ]
