# Generated by Django 3.2.12 on 2022-05-27 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0034_alter_activity_theme'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='pdf',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='rtf',
        ),
    ]
