# Generated by Django 5.2.1 on 2025-05-11 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_empleado'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleado',
            name='telefono',
            field=models.CharField(default=0, max_length=20, unique=True),
            preserve_default=False,
        ),
    ]
