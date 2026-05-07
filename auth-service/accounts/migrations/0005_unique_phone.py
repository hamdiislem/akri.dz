from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_reset_admin_password'),
    ]

    operations = [
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
