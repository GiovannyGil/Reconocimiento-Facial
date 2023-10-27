from django.db import models

# Create your models here.

class Cargo(models.Model):

    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=20, blank=False, null=False)
    descripcion = models.TextField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = ("cargo")
        verbose_name_plural = ("cargos")

    def __str__(self):
        return self.nombre


class Persona(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombres = models.CharField(max_length=30 ,blank=False, null=False)
    apellidos = models.CharField(max_length=30 ,blank=False, null=False)
    documento =  models.IntegerField(blank=False, null=False, unique=True, default=0)

    foto = models.ImageField(upload_to="usuarios/", blank=False, null=False)
    contacto = models.IntegerField(blank=False, null=False)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, null=False, blank=False, default=1) # el default = 0 -> aprendiz/practicante
    
    class Meta:
        verbose_name = ("persona")
        verbose_name_plural = ("personas")

    def __str__(self):
        return self.apellidos