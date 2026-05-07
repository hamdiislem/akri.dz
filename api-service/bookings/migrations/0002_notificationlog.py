from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=50)),
                ('booking_id', models.IntegerField()),
                ('client_id', models.IntegerField(blank=True, null=True)),
                ('agency_id', models.IntegerField(blank=True, null=True)),
                ('car', models.CharField(blank=True, max_length=200)),
                ('total_price', models.CharField(blank=True, max_length=50)),
                ('start_date', models.CharField(blank=True, max_length=20)),
                ('end_date', models.CharField(blank=True, max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
