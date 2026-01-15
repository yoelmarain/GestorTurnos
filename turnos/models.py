from django.db import models

# Create your models here.
class Cliente(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return self.nombre_cliente
    
class Servicio(models.Model):
    nombre_servicio = models.CharField(max_length=100)
    duracion_minutos = models.IntegerField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nombre_servicio


class Profesional(models.Model):
    nombre_profesional = models.CharField(max_length=100)
    especialidad = models.ManyToManyField( Servicio, related_name="profesionales")

    def __str__(self):
        return self.nombre_profesional


class Turno(models.Model):
    fecha_turno = models.DateTimeField()
    estado = models.CharField(max_length=50)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="turnos")
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name="turnos")
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name="turnos")

    class Meta:
        unique_together = ('fecha_turno', 'profesional')    
   
    def __str__(self):
        return f"Turno de {self.cliente.nombre_cliente} con {self.profesional.nombre_profesional} el {self.fecha_turno}"