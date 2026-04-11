from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=20)),
                ('wilaya', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('VERIFIED', 'VERIFIED'), ('BANNED', 'BANNED')], default='VERIFIED', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agency_name', models.CharField(max_length=255)),
                ('owner_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=20)),
                ('wilaya', models.CharField(max_length=100)),
                ('rc_number', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('VERIFIED', 'VERIFIED'), ('BANNED', 'BANNED')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name_plural': 'Agencies'},
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
