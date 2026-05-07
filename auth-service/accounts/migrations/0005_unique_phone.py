from django.db import migrations, models


def deduplicate_phones(apps, schema_editor):
    """Append _{id} to duplicate phone numbers so the unique index can be created."""
    for ModelName in ('Client', 'Agency'):
        Model = apps.get_model('accounts', ModelName)
        seen = {}
        for obj in Model.objects.order_by('id'):
            phone = (obj.phone or '').strip()
            if not phone:
                continue
            if phone in seen:
                obj.phone = f"{phone}_{obj.id}"
                obj.save(update_fields=['phone'])
            else:
                seen[phone] = obj.id


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_reset_admin_password'),
    ]

    operations = [
        migrations.RunPython(deduplicate_phones, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='agency',
            name='phone',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
