# Generated by Django 5.1.1 on 2024-11-29 08:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminmod', '0016_violation_sanction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='violation',
            name='student',
        ),
        migrations.DeleteModel(
            name='Sanction',
        ),
        migrations.DeleteModel(
            name='Violation',
        ),
    ]
