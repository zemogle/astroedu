# Generated by Django 3.2.12 on 2022-02-22 15:22

from django.db import migrations
import wagtail.fields
import wagtail.documents.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0013_auto_20220222_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='attachments',
            field=wagtail.fields.StreamField([('file', wagtail.documents.blocks.DocumentChooserBlock())], blank=True),
        ),
    ]
