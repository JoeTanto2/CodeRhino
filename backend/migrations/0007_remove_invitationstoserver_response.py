# Generated by Django 3.2.7 on 2021-10-21 15:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_auto_20211021_1500'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitationstoserver',
            name='response',
        ),
    ]