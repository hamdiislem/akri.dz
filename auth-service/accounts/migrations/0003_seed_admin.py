from django.db import migrations
from django.contrib.auth.hashers import make_password


def seed_admin(apps, schema_editor):
    Admin = apps.get_model('accounts', 'Admin')
    obj = Admin.objects.filter(email='admin@akri.dz').first()
    hashed = make_password('admin1234')
    if obj:
        obj.password = hashed
        obj.save()
    else:
        Admin.objects.create(email='admin@akri.dz', password=hashed)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_client_profile_fields'),
    ]

    operations = [
        migrations.RunPython(seed_admin, migrations.RunPython.noop),
    ]
