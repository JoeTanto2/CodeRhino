# Generated by Django 3.2.7 on 2021-11-11 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_alter_customuser_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_pic',
            field=models.ImageField(blank=True, default='pictures/default-pic.png', upload_to=''),
        ),
    ]