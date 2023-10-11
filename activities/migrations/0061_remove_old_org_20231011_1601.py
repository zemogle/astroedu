from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0060_org_data_migration_20231011_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='org',
        ),
    ]
