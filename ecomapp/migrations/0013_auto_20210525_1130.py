# Generated by Django 2.2.8 on 2021-05-25 06:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0012_profile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='user',
            new_name='userprofile',
        ),
    ]
