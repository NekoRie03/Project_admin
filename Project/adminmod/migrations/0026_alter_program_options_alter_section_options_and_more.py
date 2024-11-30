# Generated by Django 5.1.1 on 2024-11-30 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminmod', '0025_alter_program_options_alter_program_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='program',
            options={'ordering': ['name'], 'verbose_name': 'Program', 'verbose_name_plural': 'Programs'},
        ),
        migrations.AlterModelOptions(
            name='section',
            options={'ordering': ['program', 'name'], 'verbose_name': 'Section', 'verbose_name_plural': 'Sections'},
        ),
        migrations.AlterModelOptions(
            name='violation',
            options={'ordering': ['-severity', 'name'], 'verbose_name': 'Violation', 'verbose_name_plural': 'Violations'},
        ),
        migrations.AlterUniqueTogether(
            name='program',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='section',
            unique_together={('name', 'program')},
        ),
        migrations.RemoveField(
            model_name='violation',
            name='corresponding_penalty',
        ),
        migrations.RemoveField(
            model_name='violation',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='violation',
            name='prohibited_act',
        ),
        migrations.RemoveField(
            model_name='violation',
            name='severity_level',
        ),
        migrations.AddField(
            model_name='sanction',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='violation',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='violation',
            name='severity',
            field=models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=20),
        ),
        migrations.AlterField(
            model_name='program',
            name='code',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.RemoveField(
            model_name='program',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='section',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='section',
            name='year_level',
        ),
    ]
