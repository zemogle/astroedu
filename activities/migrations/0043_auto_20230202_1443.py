# Generated by Django 3.2.17 on 2023-02-02 14:43

from django.db import migrations
import django_countries.fields
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0042_alter_activity_curriculum'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='countries',
            field=django_countries.fields.CountryField(blank=True, max_length=746, multiple=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='category',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='activities.SciCategory', verbose_name='Scientific Categories'),
        ),
    ]
