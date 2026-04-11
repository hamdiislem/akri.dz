from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agency_id', models.IntegerField()),
                ('make', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('year', models.IntegerField()),
                ('price_per_day', models.DecimalField(decimal_places=2, max_digits=10)),
                ('seats', models.IntegerField()),
                ('transmission', models.CharField(choices=[('MANUAL', 'MANUAL'), ('AUTOMATIC', 'AUTOMATIC')], default='MANUAL', max_length=20)),
                ('fuel_type', models.CharField(choices=[('PETROL', 'PETROL'), ('DIESEL', 'DIESEL'), ('ELECTRIC', 'ELECTRIC'), ('HYBRID', 'HYBRID')], default='PETROL', max_length=20)),
                ('wilaya', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('images', models.JSONField(default=list)),
                ('available', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
