from django.db import migrations
from django.contrib.auth.hashers import make_password


def reset_admin_password(apps, schema_editor):
    Admin = apps.get_model('accounts', 'Admin')
    Admin.objects.filter(email='admin@akri.dz').update(
        password=make_password('admin1234')
    )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_seed_admin'),
    ]

    operations = [
        migrations.RunPython(reset_admin_password, migrations.RunPython.noop),
    ]
