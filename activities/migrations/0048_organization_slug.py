# Generated by Django 3.2.17 on 2023-02-03 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0047_organization_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='slug',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]