# Generated by Django 5.1.1 on 2024-11-27 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminmod', '0013_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='is_approved',
            field=models.BooleanField(default=None, null=True),
        ),
    ]