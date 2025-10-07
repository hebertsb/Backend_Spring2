from django.db import models

from core.models import TimeStampedModel

# Create your models here.


from django.db import models

# ======================================
# 🧍 USUARIO
# ======================================
class Usuario(TimeStampedModel):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)
    rubro = models.CharField(max_length=100, blank=True, null=True)
    carnet = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    num_viajes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.email})"


# ======================================
# 🏷️ CATEGORIA
# ======================================
class Categoria(TimeStampedModel):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# ======================================
# 🎯 CAMPAÑA
# ======================================
class Campania(TimeStampedModel):
    descripcion = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo_descuento = models.CharField(max_length=5, choices=[('%', 'Porcentaje'), ('$', 'Monto fijo')])
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.descripcion} ({self.tipo_descuento}{self.monto})"


# ======================================
# 🎟️ CUPON
# ======================================
class Cupon(TimeStampedModel):
    nro_usos = models.PositiveIntegerField(default=0)
    cantidad_max = models.PositiveIntegerField(default=0)
    campania = models.ForeignKey(Campania, on_delete=models.CASCADE, related_name='cupones')

    def __str__(self):
        return f"Cupón #{self.id} ({self.nro_usos}/{self.cantidad_max})"


# ======================================
# 🧾 RESERVA
# ======================================
class Reserva(TimeStampedModel):
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    cupon = models.ForeignKey(Cupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas')

    def __str__(self):
        return f"Reserva #{self.id} - {self.cliente.nombre}"


# ======================================
# 👥 VISITANTE
# ======================================
class Visitante(TimeStampedModel):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nac = models.DateField()
    nacionalidad = models.CharField(max_length=100)
    nro_doc = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    es_titular = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


# ======================================
# 🔗 RESERVA_VISITANTE (intermedia muchos a muchos)
# ======================================
class ReservaVisitante(TimeStampedModel):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='visitantes')
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE, related_name='reservas')

    class Meta:
        unique_together = ('reserva', 'visitante')

    def __str__(self):
        return f"Reserva {self.reserva.id} - {self.visitante.nombre}"


# ======================================
# 🏞️ SERVICIO
# ======================================
class Servicio(TimeStampedModel):
    ESTADOS = [
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ]

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    duracion = models.CharField(max_length=50)
    capacidad_max = models.PositiveIntegerField()
    punto_encuentro = models.CharField(max_length=150)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Activo')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='servicios')
    proveedor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='servicios_proveidos')

    def __str__(self):
        return self.titulo


# ======================================
# 🔗 CAMPAÑA_SERVICIO (intermedia muchos a muchos)
# ======================================
class CampaniaServicio(TimeStampedModel):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='campanias')
    campania = models.ForeignKey(Campania, on_delete=models.CASCADE, related_name='servicios')

    class Meta:
        unique_together = ('servicio', 'campania')

    def __str__(self):
        return f"{self.servicio.titulo} -> {self.campania.descripcion}"


# ======================================
# 💳 PAGO
# ======================================
class Pago(TimeStampedModel):
    METODOS = [
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia'),
        ('Efectivo', 'Efectivo'),
    ]
    ESTADOS = [
        ('Confirmado', 'Confirmado'),
        ('Pendiente', 'Pendiente'),
        ('Fallido', 'Fallido'),
    ]

    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODOS)
    fecha_pago = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS)
    url_stripe = models.URLField(max_length=255, blank=True, null=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagos')

    def __str__(self):
        return f"Pago {self.id} - {self.estado} - {self.monto}"


# ======================================
# 🔁 REGLA_REPROGRAMACION
# ======================================
class ReglaReprogramacion(TimeStampedModel):
    descripcion = models.CharField(max_length=150)
    limite_hora = models.PositiveIntegerField(help_text="Horas antes del evento para permitir reprogramación")
    condiciones = models.TextField()

    def __str__(self):
        return self.descripcion


# ======================================
# 🔄 REPROGRAMACION
# ======================================
class Reprogramacion(TimeStampedModel):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
        ('Rechazada', 'Rechazada'),
    ]
    TIPOS = [
        ('Voluntaria', 'Voluntaria'),
        ('Forzada', 'Forzada'),
    ]

    fecha_solicitud = models.DateField()
    nueva_fecha = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='reprogramaciones')

    def __str__(self):
        return f"Reprogramación {self.id} ({self.estado})"
