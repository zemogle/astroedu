# Generated by Django 3.2.18 on 2023-04-29 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0057_auto_20230429_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
    ]