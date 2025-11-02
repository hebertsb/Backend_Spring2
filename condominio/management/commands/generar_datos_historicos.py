"""
Comando Django para generar datos históricos sintéticos de prueba para reportes.
Genera datos realistas con patrones de temporadas, tendencias y variabilidad.

Uso: 
    python manage.py generar_datos_historicos
    python manage.py generar_datos_historicos --meses=12 --cantidad=50
    python manage.py generar_datos_historicos --limpiar  # Limpia datos anteriores
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import random
import string

from condominio.models import (
    Usuario, Servicio, Paquete, Reserva, Pago, 
    Categoria, Visitante, ReservaVisitante, ReservaServicio
)
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Genera datos históricos sintéticos de prueba para reportes (últimos 12 meses)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--meses',
            type=int,
            default=12,
            help='Número de meses hacia atrás para generar datos (default: 12)'
        )
        parser.add_argument(
            '--cantidad',
            type=int,
            default=50,
            help='Cantidad de reservas a generar por mes (default: 50)'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina datos de prueba existentes antes de generar nuevos'
        )

    def handle(self, *args, **options):
        meses = options['meses']
        cantidad_por_mes = options['cantidad']
        limpiar = options.get('limpiar', False)
        
        self.stdout.write(self.style.SUCCESS(f'=' * 80))
        self.stdout.write(self.style.SUCCESS(f'🚀 GENERADOR DE DATOS SINTÉTICOS PARA REPORTES'))
        self.stdout.write(self.style.SUCCESS(f'=' * 80))
        
        if limpiar:
            self.stdout.write(self.style.WARNING('\n🗑️  Limpiando datos de prueba existentes...'))
            self._limpiar_datos()
            self.stdout.write(self.style.SUCCESS('✅ Datos anteriores eliminados\n'))
        
        self.stdout.write(f'\n📊 Configuración:')
        self.stdout.write(f'   - Meses: {meses}')
        self.stdout.write(f'   - Reservas por mes: {cantidad_por_mes}')
        self.stdout.write(f'   - Total estimado: {meses * cantidad_por_mes} reservas\n')
        
        # Crear datos base
        self.stdout.write(self.style.WARNING('📦 Creando datos base...'))
        categorias = self._crear_categorias()
        servicios = self._crear_servicios(categorias)
        paquetes = self._crear_paquetes(servicios)
        usuarios = self._crear_usuarios()
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Datos base creados:\n'
            f'   - {len(categorias)} categorías\n'
            f'   - {len(servicios)} servicios\n'
            f'   - {len(paquetes)} paquetes\n'
            f'   - {len(usuarios)} usuarios\n'
        ))
        
        # Generar reservas históricas con patrones realistas
        self.stdout.write(self.style.WARNING('🔄 Generando reservas históricas...'))
        total_reservas = self._generar_reservas_historicas(
            meses, cantidad_por_mes, servicios, paquetes, usuarios
        )
        
        self.stdout.write(self.style.SUCCESS(f'\n' + '=' * 80))
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ ¡GENERACIÓN COMPLETADA EXITOSAMENTE!\n\n'
                f'📈 Resumen:\n'
                f'   - {total_reservas} reservas creadas\n'
                f'   - {len(servicios)} servicios disponibles\n'
                f'   - {len(paquetes)} paquetes disponibles\n'
                f'   - {len(usuarios)} clientes registrados\n'
                f'   - Período: últimos {meses} meses\n\n'
                f'🎯 Próximos pasos:\n'
                f'   1. Probar endpoints: /api/reportes/ventas/, /api/reportes/voz/\n'
                f'   2. Usar Postman para hacer consultas\n'
                f'   3. Verificar datos en Django Admin\n'
            )
        )
        self.stdout.write(self.style.SUCCESS('=' * 80))
    
    def _limpiar_datos(self):
        """Limpia datos de prueba generados previamente."""
        # Eliminar solo usuarios de prueba (cliente_*)
        usuarios_prueba = Usuario.objects.filter(user__username__startswith='cliente_')
        
        # Obtener IDs antes de eliminar
        ids_usuarios = list(usuarios_prueba.values_list('id', flat=True))
        
        # Eliminar reservas de estos usuarios
        Reserva.objects.filter(cliente_id__in=ids_usuarios).delete()
        
        # Eliminar usuarios de prueba y sus users de Django
        for usuario in usuarios_prueba:
            if usuario.user:
                usuario.user.delete()  # Esto eliminará el Usuario por CASCADE
        
        # Eliminar paquetes de prueba
        paquetes_prueba = [
            'Paquete Bolivia Completo', 'Aventura Andina', 'Cultural Express',
            'Naturaleza Extrema', 'Bolivia Express', 'Salar y Lago', 'Salar y Altiplano',
            'Ciudades Coloniales', 'Bolivia Premium', 'Weekend en Bolivia', 
            'Mochilero Bolivia', 'Valle Central', 'Sucre Colonial Premium',
            'Ruta del Vino Tarijeño', 'Misiones Jesuíticas', 'Ruta de la Plata'
        ]
        Paquete.objects.filter(nombre__in=paquetes_prueba).delete()
        
        # Eliminar servicios de prueba (ampliada la lista)
        servicios_prueba = [
            'Salar de Uyuni', 'Lago Titicaca', 'Yungas Adventure',
            'Misiones Tour', 'Trekking Cordillera', 'Valle de la Luna',
            'Isla del Sol', 'Parque Madidi', 'Ciudad de Potosí',
            'Teleférico La Paz', 'Carnaval Oruro', 'Sucre Colonial',
            'Cementerio de Trenes', 'Parque Amboró', 'Samaipata',
            'Valle Sagrado', 'Dinosaurios Park', 'Pampas del Yacuma',
            'Ruta del Vino', 'Valle de la Concepción'
        ]
        Servicio.objects.filter(titulo__in=servicios_prueba).delete()
        
        self.stdout.write('   ✓ Reservas eliminadas')
        self.stdout.write('   ✓ Usuarios de prueba eliminados')
        self.stdout.write('   ✓ Servicios de prueba eliminados')
        self.stdout.write('   ✓ Paquetes de prueba eliminados')
    
    def _crear_categorias(self):
        """Crea categorías de servicios turísticos."""
        categorias_data = [
            "Aventura",
            "Cultural",
            "Naturaleza",
            "Histórico",
            "Gastronómico",
            "Urbano",
        ]
        
        categorias = []
        for nombre in categorias_data:
            cat, _ = Categoria.objects.get_or_create(nombre=nombre)
            categorias.append(cat)
        
        return categorias
    
    def _crear_servicios(self, categorias):
        """Crea servicios turísticos variados con asignación de departamentos."""
        hoy = timezone.now().date()
        
        # Formato: (titulo, desc, precio, capacidad, categoria, departamento, ciudad)
        servicios_data = [
            # La Paz - Aventura y Cultural
            ("Yungas Adventure", "Descenso extremo en bicicleta", 420, 12, categorias[0], 
             "La Paz", "La Paz"),
            ("Lago Titicaca", "Visita a islas flotantes y templos", 280, 25, categorias[1],
             "La Paz", "Copacabana"),
            ("Valle de la Luna", "Paisajes lunares únicos", 180, 20, categorias[2],
             "La Paz", "La Paz"),
            ("Teleférico La Paz", "Vista panorámica de la ciudad", 50, 50, categorias[5],
             "La Paz", "La Paz"),
            ("Isla del Sol", "Tour de un día en el lago sagrado", 240, 30, categorias[1],
             "La Paz", "Copacabana"),
            
            # Potosí - Histórico y Cultural
            ("Salar de Uyuni", "Tour de 3 días al salar más grande del mundo", 350, 20, categorias[0],
             "Potosí", "Uyuni"),
            ("Ciudad de Potosí", "Minas coloniales y museo", 220, 22, categorias[3],
             "Potosí", "Potosí"),
            ("Cementerio de Trenes", "Visita al cementerio de trenes histórico", 80, 30, categorias[3],
             "Potosí", "Uyuni"),
            
            # Santa Cruz - Naturaleza y Aventura
            ("Parque Amboró", "Expedición al parque nacional", 450, 15, categorias[2],
             "Santa Cruz", "Santa Cruz de la Sierra"),
            ("Samaipata", "Fuerte precolombino y naturaleza", 200, 25, categorias[1],
             "Santa Cruz", "Samaipata"),
            ("Misiones Tour", "Recorrido por misiones jesuíticas", 310, 18, categorias[1],
             "Santa Cruz", "San José de Chiquitos"),
            
            # Cochabamba - Trekking y Naturaleza
            ("Trekking Cordillera", "Caminata de alta montaña", 500, 15, categorias[0],
             "Cochabamba", "Cochabamba"),
            ("Valle Sagrado", "Tour por el valle fértil", 190, 20, categorias[2],
             "Cochabamba", "Cochabamba"),
            
            # Chuquisaca - Colonial e Histórico
            ("Sucre Colonial", "City tour por la capital histórica", 150, 30, categorias[1],
             "Chuquisaca", "Sucre"),
            ("Dinosaurios Park", "Visita al parque de huellas de dinosaurios", 120, 40, categorias[3],
             "Chuquisaca", "Sucre"),
            
            # Oruro - Cultural
            ("Carnaval Oruro", "Experiencia del carnaval más grande", 800, 100, categorias[3],
             "Oruro", "Oruro"),
            
            # Beni - Naturaleza Amazónica
            ("Parque Madidi", "Expedición a la selva amazónica", 650, 10, categorias[2],
             "Beni", "Trinidad"),
            ("Pampas del Yacuma", "Safari fotográfico en las pampas", 550, 12, categorias[2],
             "Beni", "Rurrenabaque"),
            
            # Tarija - Gastronomía y Viñedos
            ("Ruta del Vino", "Tour por viñedos tarijeños", 280, 20, categorias[4],
             "Tarija", "Tarija"),
            ("Valle de la Concepción", "Degustación y paisajes", 320, 18, categorias[4],
             "Tarija", "Tarija"),
        ]
        
        servicios = []
        for titulo, desc, precio, capacidad, cat, depto, ciudad in servicios_data:
            servicio, created = Servicio.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'descripcion': desc,
                    'duracion': f'{random.randint(1, 5)} días',
                    'capacidad_max': capacidad,
                    'punto_encuentro': 'Plaza Principal / Hotel',
                    'estado': 'Activo',
                    'categoria': cat,
                    'precio_usd': Decimal(str(precio)),
                    'imagen_url': f'https://picsum.photos/seed/{titulo}/800/600',
                    'departamento': depto,
                    'ciudad': ciudad
                }
            )
            
            # Actualizar servicios existentes con los nuevos campos
            if not created and (not servicio.departamento or not servicio.ciudad):
                servicio.departamento = depto
                servicio.ciudad = ciudad
                servicio.save()
            
            servicios.append(servicio)
        
        return servicios
    
    def _crear_paquetes(self, servicios):
        """Crea paquetes turísticos combinados con asignación de departamentos."""
        hoy = timezone.now().date()
        
        # Formato: (nombre, desc, precio, dias, destacado, departamento, ciudad, tipo_destino)
        paquetes_data = [
            # La Paz - Cultura y Naturaleza
            ("Aventura Andina", "Paquete de aventura extrema", 850, 5, True,
             "La Paz", "La Paz", "Cultural"),
            ("Cultural Express", "Lo mejor de la cultura boliviana", 600, 3, True,
             "La Paz", "La Paz", "Cultural"),
            ("Bolivia Express", "Recorrido rápido por lo esencial", 450, 2, True,
             "La Paz", "La Paz", "Cultural"),
            
            # Santa Cruz - Naturaleza y Cultura
            ("Naturaleza Extrema", "Expedición por parques nacionales", 1500, 10, True,
             "Santa Cruz", "Santa Cruz de la Sierra", "Natural"),
            ("Misiones Jesuíticas", "Tour completo por las misiones", 980, 6, True,
             "Santa Cruz", "Santa Cruz de la Sierra", "Cultural"),
            
            # Potosí - Salar y Altiplano
            ("Salar y Altiplano", "Experiencia completa Uyuni", 1280, 7, True,
             "Potosí", "Uyuni", "Natural"),
            ("Ruta de la Plata", "Historia minera de Potosí", 540, 3, True,
             "Potosí", "Potosí", "Cultural"),
            
            # Cochabamba - Naturaleza y Gastronomía
            ("Valle Central", "Naturaleza y gastronomía cochabambina", 720, 4, True,
             "Cochabamba", "Cochabamba", "Rural"),
            
            # Chuquisaca - Colonial
            ("Ciudades Coloniales", "Sucre, Potosí y La Paz", 720, 6, True,
             "Chuquisaca", "Sucre", "Cultural"),
            ("Sucre Colonial Premium", "Experiencia colonial de lujo", 890, 4, True,
             "Chuquisaca", "Sucre", "Cultural"),
            
            # Tarija - Viñedos
            ("Weekend en Bolivia", "Fin de semana intenso", 380, 2, True,
             "Tarija", "Tarija", "Rural"),
            ("Ruta del Vino Tarijeño", "Tour enológico completo", 1150, 5, True,
             "Tarija", "Tarija", "Rural"),
            
            # Multi-departamental - Tours completos
            ("Paquete Bolivia Completo", "Tour completo por Bolivia", 1200, 7, True,
             "Multi-departamental", "Varias ciudades", "Cultural"),
            ("Bolivia Premium", "Experiencia de lujo", 2500, 14, True,
             "Multi-departamental", "Varias ciudades", "Cultural"),
            ("Mochilero Bolivia", "Paquete económico para viajeros", 520, 7, True,
             "Multi-departamental", "Varias ciudades", "Aventura"),
        ]
        
        paquetes = []
        for nombre, desc, precio, dias, destacado, depto, ciudad, tipo_dest in paquetes_data:
            paquete, created = Paquete.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': desc,
                    'duracion': f'{dias} días',
                    'precio_base': Decimal(str(precio)),
                    'cupos_disponibles': random.randint(20, 50),
                    'cupos_ocupados': 0,
                    'fecha_inicio': hoy - timedelta(days=365),
                    'fecha_fin': hoy + timedelta(days=180),
                    'estado': 'Activo',
                    'punto_salida': 'Terminal de buses / Aeropuerto',
                    'destacado': destacado and random.random() > 0.5,
                    'imagen_principal': f'https://picsum.photos/seed/{nombre}/1200/800',
                    'es_personalizado': False,
                    'departamento': depto,
                    'ciudad': ciudad,
                    'tipo_destino': tipo_dest
                }
            )
            
            # Actualizar paquetes existentes con los nuevos campos
            if not created and (not paquete.departamento or not paquete.ciudad or not paquete.tipo_destino):
                paquete.departamento = depto
                paquete.ciudad = ciudad
                paquete.tipo_destino = tipo_dest
                paquete.save()
            
            paquetes.append(paquete)
        
        return paquetes
    
    def _crear_usuarios(self):
        """Crea usuarios de prueba con perfiles variados."""
        nombres = [
            "Juan Pérez", "María García", "Carlos López", "Ana Martínez", 
            "Pedro Rodríguez", "Laura Fernández", "Diego Sánchez", "Sofía Torres",
            "Luis Ramírez", "Carmen Flores", "Miguel Ángel Cruz", "Valentina Ruiz",
            "Fernando Castro", "Isabella Morales", "Roberto Gutiérrez", "Camila Reyes",
            "Jorge Herrera", "Lucía Mendoza", "Andrés Silva", "Victoria Vega",
            "Gabriel Ortiz", "Daniela Romero", "Ricardo Vargas", "Natalia Jiménez",
            "Sebastián Molina", "Paula Castillo", "Martín Núñez", "Andrea Muñoz",
        ]
        
        paises = ["Bolivia", "Argentina", "Perú", "Chile", "Brasil", "Colombia", "España", "México"]
        
        usuarios = []
        for i, nombre in enumerate(nombres):
            username = f"cliente_{i+1:03d}"
            email = f"{username}@example.com"
            
            # Crear o obtener user de Django
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email, 
                    'first_name': nombre.split()[0],
                    'last_name': nombre.split()[-1]
                }
            )
            
            # Crear perfil Usuario
            usuario, created = Usuario.objects.get_or_create(
                user=user,
                defaults={
                    'nombre': nombre,
                    'telefono': f'+591 7{random.randint(1000000, 9999999)}',
                    'num_viajes': random.randint(0, 15),
                    'pais': random.choice(paises),
                    'genero': random.choice(['M', 'F']),
                }
            )
            usuarios.append(usuario)
        
        return usuarios
    
    def _generar_reservas_historicas(self, meses, cantidad_por_mes, servicios, paquetes, usuarios):
        """Genera reservas históricas con patrones realistas."""
        total_reservas = 0
        estados_reserva = ['PENDIENTE', 'CONFIRMADA', 'PAGADA', 'COMPLETADA', 'CANCELADA']
        metodos_pago = ['Tarjeta', 'Transferencia', 'Efectivo']
        
        hoy = timezone.now().date()
        
        # Definir temporadas altas y bajas (más reservas en meses de vacación)
        meses_alta = [1, 2, 6, 7, 8, 12]  # Enero, Febrero, Junio-Agosto, Diciembre
        
        for mes in range(meses):
            fecha_base = hoy - timedelta(days=30 * mes)
            mes_numero = fecha_base.month
            
            # Ajustar cantidad según temporada
            multiplicador = 1.5 if mes_numero in meses_alta else 1.0
            cantidad_mes = int(cantidad_por_mes * multiplicador)
            
            for _ in range(cantidad_mes):
                # Aleatorizar fecha dentro del mes
                try:
                    dia_random = random.randint(1, 28)
                    fecha_reserva = fecha_base.replace(day=dia_random)
                except ValueError:
                    fecha_reserva = fecha_base
                
                # Decidir si es reserva de servicio o paquete (60% paquetes, 40% servicios)
                es_paquete = random.random() < 0.6
                usuario = random.choice(usuarios)
                
                if es_paquete:
                    paquete = random.choice(paquetes)
                    # Variación de precio ±10%
                    variacion = Decimal(str(random.uniform(0.9, 1.1)))
                    total = paquete.precio_base * variacion
                    servicio = None
                else:
                    servicio = random.choice(servicios)
                    paquete = None
                    # Variación de precio ±15%
                    variacion = Decimal(str(random.uniform(0.85, 1.15)))
                    total = servicio.precio_usd * variacion
                
                # Convertir a BOB (1 USD = 6.96 BOB aproximado)
                total_bob = (total * Decimal('6.96')).quantize(Decimal('0.01'))
                
                # Estado de la reserva (más probabilidad de PAGADA/COMPLETADA en el pasado)
                if mes > 2:  # Reservas más antiguas
                    estado = random.choices(
                        estados_reserva, 
                        weights=[3, 8, 35, 45, 9]  # Más completadas
                    )[0]
                else:  # Reservas recientes
                    estado = random.choices(
                        estados_reserva, 
                        weights=[15, 25, 35, 15, 10]
                    )[0]
                
                # Crear reserva
                reserva = Reserva.objects.create(
                    fecha=fecha_reserva,
                    fecha_inicio=timezone.make_aware(
                        timezone.datetime.combine(
                            fecha_reserva + timedelta(days=random.randint(1, 30)), 
                            timezone.datetime.min.time()
                        )
                    ),
                    estado=estado,
                    total=total_bob,
                    moneda='BOB',
                    cliente=usuario,
                    servicio=servicio,
                    paquete=paquete
                )
                
                # Crear pago si está pagada o completada
                if estado in ['PAGADA', 'COMPLETADA']:
                    metodo = random.choices(
                        metodos_pago,
                        weights=[60, 30, 10]  # 60% tarjeta, 30% transferencia, 10% efectivo
                    )[0]
                    
                    Pago.objects.create(
                        monto=total_bob,
                        metodo=metodo,
                        fecha_pago=fecha_reserva,
                        estado='Confirmado',
                        reserva=reserva,
                        url_stripe=f'https://stripe.com/payment/{random.randint(100000, 999999)}' if metodo == 'Tarjeta' else None
                    )
                
                # Crear visitantes aleatorios (1-5 personas)
                num_visitantes = random.randint(1, 5)
                apellidos = ["García", "López", "Martínez", "Pérez", "Rodríguez", "González", "Fernández"]
                
                for v in range(num_visitantes):
                    visitante = Visitante.objects.create(
                        nombre=f"{random.choice(['Juan', 'María', 'Pedro', 'Ana', 'Luis', 'Carmen'])}",
                        apellido=random.choice(apellidos),
                        fecha_nac=timezone.now().date() - timedelta(days=random.randint(7000, 25000)),
                        nacionalidad=random.choice(["Bolivia", "Argentina", "Perú", "Chile"]),
                        nro_doc=f"CI-{random.randint(1000000, 9999999)}",
                        es_titular=(v == 0)
                    )
                    ReservaVisitante.objects.create(reserva=reserva, visitante=visitante)
                
                total_reservas += 1
                
                # Mostrar progreso cada 50 reservas
                if total_reservas % 50 == 0:
                    self.stdout.write(f'   ✓ {total_reservas} reservas creadas...')
        
        return total_reservas
