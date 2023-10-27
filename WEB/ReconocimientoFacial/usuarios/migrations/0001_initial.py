# Generated by Django 3.2.22 on 2023-10-25 20:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nombre', models.TextField(max_length=20)),
                ('descripcion', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'cargo',
                'verbose_name_plural': 'cargos',
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nombres', models.TextField(max_length=30)),
                ('apellidos', models.TextField(max_length=30)),
                ('foto', models.FileField(upload_to='usuarios/')),
                ('contacto', models.IntegerField()),
                ('cargo', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='usuarios.cargo')),
            ],
        ),
    ]