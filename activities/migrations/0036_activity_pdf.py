# Generated by Django 3.2.12 on 2022-05-27 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0012_uploadeddocument'),
        ('activities', '0035_auto_20220527_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='pdf',
            field=models.ForeignKey(blank=True, help_text='PDF will be autogenerated after publication. Do not upload one.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtaildocs.document'),
        ),
    ]