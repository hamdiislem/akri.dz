from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='client', name='driver_license', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='client', name='age', field=models.IntegerField(blank=True, null=True)),
        migrations.AddField(model_name='client', name='gender', field=models.CharField(blank=True, max_length=10)),
        migrations.AddField(model_name='client', name='marital_status', field=models.CharField(blank=True, max_length=20)),
        migrations.AddField(model_name='client', name='family_size', field=models.IntegerField(blank=True, null=True)),
        migrations.AddField(model_name='agency', name='address', field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name='agency', name='description', field=models.TextField(blank=True)),
    ]
