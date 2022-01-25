# Generated by Django 3.1.12 on 2021-06-23 13:37

from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='astronomical_scientific_category',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, limit_choices_to={'group': 'astronomical_categories'}, null=True, related_name='_activity_astronomical_scientific_category_+', to='activities.Category', verbose_name='Astronomical Scientific Categories'),
        ),
    ]
