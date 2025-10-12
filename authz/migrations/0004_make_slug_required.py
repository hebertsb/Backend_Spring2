from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authz', '0003_populate_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rol',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]
