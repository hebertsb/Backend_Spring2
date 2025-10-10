# condominio/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command
from django.apps import apps


@receiver(post_migrate)
def cargar_datos_iniciales(sender, **kwargs):
    """
    Carga automáticamente los datos iniciales del fixture después de ejecutar migrate.
    Solo se ejecuta cuando se migran los modelos de la app 'condominio'.
    """
    if sender.name == 'condominio':
        Categoria = apps.get_model('condominio', 'Categoria')  
        if not Categoria.objects.exists():
            try:
                print("📦 Cargando datos iniciales para CONDOMINIO...")
                call_command('loaddata', 'condominio/fixtures/datos_iniciales.json')
                print("✅ Datos iniciales de CONDOMINIO cargados correctamente.")
            except Exception as e:
               print(f"⚠️ Error al cargar fixtures de condominio: {e}")
