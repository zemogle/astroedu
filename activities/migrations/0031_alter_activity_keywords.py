# Generated by Django 3.2.12 on 2022-03-04 13:38

from django.db import migrations
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('activities', '0030_auto_20220303_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='keywords',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='activities.Keyword', to='taggit.Tag', verbose_name='Keywords'),
        ),
    ]
