# Generated by Django 3.2.7 on 2021-10-19 17:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_servers_textchannels'),
    ]

    operations = [
        migrations.CreateModel(
            name='JoinServerRequests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('response', models.BooleanField(default=False)),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('server_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.servers')),
            ],
        ),
    ]
