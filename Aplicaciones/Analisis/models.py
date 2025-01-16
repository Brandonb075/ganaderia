from django.db import models

# Create your models here.


class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploaded_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Vendedor(models.Model):
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    correo = models.EmailField(null=True, blank=True)
    finca = models.ForeignKey('Finca', related_name='vendedores', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Finca(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    tamano = models.DecimalField(max_digits=10, decimal_places=2)  # Tamaño en hectáreas
    propietario = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.nombre