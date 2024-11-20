# Generated by Django 5.1.1 on 2024-11-11 14:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminmod', '0011_studentregistration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentregistration',
            options={'verbose_name': 'Student Registration', 'verbose_name_plural': 'Student Registrations'},
        ),
        migrations.AlterField(
            model_name='studentregistration',
            name='is_approved',
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='studentregistration',
            name='registration_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]