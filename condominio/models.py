from django.db import models

from authz.models import Rol
from core.models import TimeStampedModel
from django.contrib.auth.models import User
# Create your models here.


from django.db import models
# ======================================
# 🧍 Rol
# ====================================== 

# ======================================
# 🧍 USUARIO
# ======================================
class Usuario(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nombre = models.CharField(max_length=100)
    rubro = models.CharField(max_length=100, blank=True, null=True)
    num_viajes = models.PositiveIntegerField(default=0)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    # Campos opcionales solicitados por frontend
    telefono = models.CharField(max_length=50, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=5, blank=True, null=True)
    documento_identidad = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre}"
    

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

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    duracion = models.CharField(max_length=50)
    capacidad_max = models.IntegerField()
    punto_encuentro = models.CharField(max_length=255)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Activo')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    proveedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)

    imagen_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL de la imagen representativa del servicio"
    )
    precio_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Precio en dólares del servicio"
    )
    servicios_incluidos = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de servicios incluidos (ej: Guía, Transporte, Hotel)"
    )

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


# ======================================
# 🆘 SOPORTE / TICKETS (CU17)
# Minimal models required for soporte (no relación con Reserva)
# ======================================
class Ticket(TimeStampedModel):
    ESTADOS = [
        ('Abierto', 'Abierto'),
        ('Asignado', 'Asignado'),
        ('Respondido', 'Respondido'),
        ('Cerrado', 'Cerrado'),
    ]

    creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tickets_creados')
    asunto = models.CharField(max_length=150)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Abierto')
    agente = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_asignados')
    prioridad = models.CharField(max_length=10, blank=True, null=True)
    cerrado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.id} - {self.asunto} ({self.estado})"


class TicketMessage(TimeStampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_soporte')
    texto = models.TextField()

    def __str__(self):
        return f"Mensaje #{self.id} - Ticket {self.ticket.id} by {self.autor.nombre}"


class Notificacion(TimeStampedModel):
    TIPOS = [
        ('ticket_nuevo', 'Ticket Nuevo'),
        ('ticket_respondido', 'Ticket Respondido'),
        ('ticket_cerrado', 'Ticket Cerrado'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=50, choices=TIPOS)
    datos = models.JSONField(blank=True, null=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación #{self.id} -> {self.usuario.nombre} ({self.tipo})"


# ======================================
# Bitacora / Log de acciones
# ======================================
class Bitacora(TimeStampedModel):
    """Registro de acciones realizadas en el sistema.
    Guarda referencia al perfil (Usuario) cuando aplica, la accion, descripcion libre,
    y la IP de la máquina que realizó la acción.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='bitacoras')
    accion = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)

    def __str__(self):
        who = self.usuario.nombre if self.usuario else 'Anon'
        return f"{self.created_at.isoformat()} - {who} - {self.accion}"
