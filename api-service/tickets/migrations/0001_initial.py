from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_id', models.IntegerField()),
                ('sender_role', models.CharField(max_length=10)),
                ('subject', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('reported_id', models.IntegerField(blank=True, null=True)),
                ('reported_role', models.CharField(blank=True, max_length=10)),
                ('status', models.CharField(
                    choices=[('OPEN', 'Ouvert'), ('IN_PROGRESS', 'En cours'), ('RESOLVED', 'Résolu')],
                    default='OPEN', max_length=20,
                )),
                ('admin_response', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
