from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='reported_id',
        ),
        migrations.AddField(
            model_name='ticket',
            name='reported_phone',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
