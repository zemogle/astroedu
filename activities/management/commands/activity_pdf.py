import sys
import tempfile
import base64
from pathlib import Path

from django.db.models import Q
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files import File
from django.core.files.storage import default_storage
from wagtail.documents.models import Document

from activities.models import Activity


class Command(BaseCommand):
    help = 'Generates PDF for the specified articles'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--code', help='Four digit code (YYnn) of the article, will replace existing PDFs unless used with --new')
        parser.add_argument('--lang', help='Language of the article')
        parser.add_argument('--new', action='store_true', help='Generate PDFs for new activities')
        parser.add_argument('--all', action='store_true', help='(Re-)Generate PDFs for all activities')
        parser.add_argument('--fileonly', action='store_true', help='Just generate the file and not the Document')


    def handle(self, *args, **options):
        if options['new'] and not options['code']:
            versions = Activity.objects.filter(Q(pdf='')|Q(pdf=False), live=True).order_by('-first_published_at')
        elif options['all']:
            versions = Activity.objects.filter(live=True).order_by('-first_published_at')
        elif options['code']:
            try:
                versions = Activity.objects.filter(code=options['code'])
            except Exception as e:
                self.stderr.write(e)
                self.stderr.write(f"Activity {options['code']} not found")
                sys.exit()
        else:
            self.stderr.write("Either select --new or enter --code or both")
            sys.exit()
        if options.get('lang',None):
            try:
                versions = versions.filter(locale__language_code=options['lang'])
            except Exception as e:
                self.stderr.write(e)
                self.stderr.write(f"Activity {options['code']} in {options['lang']} not found")
                sys.exit()
        self.stdout.write(f'Generating PDFs for {len(versions)} activities')
        for version in versions:
            if options['new'] and version.pdf:
                self.stdout.write(f"Skipping {version.master.code} in {version.local.language_code}")
                continue

            self.add_document(version, lang=options['lang'])

    def add_document(self, activity, lang, file_only=False):
        try:
            file_obj = activity.generate_pdf(lang_code=lang)
        except Exception as e:
            self.stderr.write(f"{e}")
            self.stderr.write(f"Failed to create  {activity.code} in {activity.locale.language_code}")
            return

        if file_only:
            filepath = Path('/data/') / filename
            Path(filepath).write_bytes(file_obj)
            return
        filename = f'astroedu-{activity.code}-{activity.locale.language_code}.pdf'
        # try:
        docfile = ContentFile(file_obj)
        if not activity.pdf:
            doc, c = Document.objects.get_or_create(title=f"Activity for {activity.code} in {activity.locale.language_code}")
        doc.file.save(filename, docfile)
        doc.save()
        # except Exception as e:
        #     print(f"Problem with {filename} in {activity}: {e}")
        #     return False
        activity.pdf = doc
        activity.save()
        self.stdout.write(f'Written {filename}')
        return True
