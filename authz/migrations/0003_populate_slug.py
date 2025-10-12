from django.db import migrations
from django.utils.text import slugify


def populate_slug(apps, schema_editor):
    Rol = apps.get_model('authz', 'Rol')
    for r in Rol.objects.all():
        if not r.slug:
            r.slug = slugify(r.nombre)[:100]
            r.save()


class Migration(migrations.Migration):

    dependencies = [
        ('authz', '0002_rol_descripcion_rol_slug_userrole'),
    ]

    operations = [
        migrations.RunPython(populate_slug, reverse_code=migrations.RunPython.noop),
    ]
