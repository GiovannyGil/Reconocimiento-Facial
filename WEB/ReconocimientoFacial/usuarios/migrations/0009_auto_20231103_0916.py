# Generated by Django 3.2.22 on 2023-11-03 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0008_alter_persona_foto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='persona',
            name='cargo',
        ),
        migrations.AlterField(
            model_name='persona',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='usuarios/'),
        ),
        migrations.DeleteModel(
            name='Cargo',
        ),
    ]
