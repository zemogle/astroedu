# Generated by Django 3.2.12 on 2022-05-06 12:21

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0032_activity_rtf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='conclusion',
            field=wagtail.core.fields.RichTextField(blank=True),
        ),
    ]
