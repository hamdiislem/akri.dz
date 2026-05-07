from django.db import migrations
from django.contrib.auth.hashers import make_password


def seed_admin(apps, schema_editor):
    Admin = apps.get_model('accounts', 'Admin')
    if not Admin.objects.filter(email='admin@akri.dz').exists():
        Admin.objects.create(
            email='admin@akri.dz',
            password=make_password('Admin@2025'),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_client_profile_fields'),
    ]

    operations = [
        migrations.RunPython(seed_admin, migrations.RunPython.noop),
    ]
