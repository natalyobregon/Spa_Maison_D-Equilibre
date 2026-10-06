from django.db import models
from django.utils import timezone
<<<<<<< HEAD
=======
from adminApp.models import Terapia
>>>>>>> 319e90c77a57cae8a1f0d1eafa3ec41119082ca8

class Terapeuta(models.Model):
    nombre = models.CharField(max_length=100)
    profesion = models.CharField(max_length=150)
    correo = models.EmailField(unique=True, max_length=191)
    foto = models.ImageField(upload_to="terapeutas/fotos/", null=True, blank=True)
    certificado = models.FileField(upload_to="terapeutas/certificados/", null=True, blank=True)
<<<<<<< HEAD
=======
    terapias = models.ManyToManyField(
        Terapia,
        related_name='terapeutas',
        blank=True,
        verbose_name='Terapias que realiza',
    )
>>>>>>> 319e90c77a57cae8a1f0d1eafa3ec41119082ca8

    class Meta:
        db_table = 'terapeutas' #esto es para renombrar la tabla en php admin.

    def __str__(self):
        return self.nombre