# Generated by Django 3.2.12 on 2022-02-22 16:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0015_auto_20220222_1628'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authorinstitute',
            name='institution',
        ),
        migrations.AddField(
            model_name='person',
            name='institution',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='activities.institute'),
            preserve_default=False,
        ),
    ]
