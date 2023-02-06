# Generated by Django 3.2.17 on 2023-02-03 14:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0044_auto_20230203_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='org',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='activities.organization'),
        ),
    ]