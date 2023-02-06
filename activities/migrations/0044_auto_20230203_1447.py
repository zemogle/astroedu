# Generated by Django 3.2.17 on 2023-02-03 14:47

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import uuid
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0069_log_entry_jsonfield'),
        ('activities', '0043_auto_20230202_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='countries',
            field=django_countries.fields.CountryField(blank=True, help_text='Activity originally developed in', max_length=746, multiple=True),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('translation_key', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(max_length=255)),
                ('fullname', models.CharField(blank=True, help_text='If set, the full name will be used in some places instead of the name', max_length=255)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField(blank=True, max_length=255, null=True)),
                ('about', wagtail.fields.RichTextField(blank=True)),
                ('locale', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailcore.locale')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('translation_key', 'locale')},
            },
        ),
    ]