# Generated by Django 3.2.17 on 2023-02-08 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0053_organization_logo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('fullname', models.CharField(blank=True, help_text='If set, the full name will be used in some places instead of the name', max_length=255)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField(blank=True, max_length=255, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='person',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='activities.institute'),
        ),
    ]
