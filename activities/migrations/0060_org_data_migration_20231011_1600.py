from django.db import migrations
import logging
from  django.db.utils import IntegrityError

def import_orgs(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Person = apps.get_model('activities', 'Person')
    for person in Person.objects.all():
        if person.org:
            person.orgs.add(person.org)
        else:
            continue
        try:
            person.save()
            logging.info(f"Added {person.org} to {person}")
        except IntegrityError:
            logging.error(f"Issue with {person.org} for {person.name}")

class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0059_auto_20231011_1201'),
    ]

    operations = [
        migrations.RunPython(import_orgs),
    ]