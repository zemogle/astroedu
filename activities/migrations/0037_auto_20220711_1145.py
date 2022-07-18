# Generated by Django 3.2.12 on 2022-07-11 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0036_activity_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='cost',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.cost', verbose_name='Cost per student'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.group', verbose_name='Group or individual activity'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.location'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='supervised',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.supervised', verbose_name='Supervised for safety'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='time',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='activities.time'),
        ),
    ]
