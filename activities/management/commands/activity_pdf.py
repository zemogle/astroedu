import sys
import tempfile
import base64

from django.db.models import Q
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from activities.models import Activity


class Command(BaseCommand):
    help = 'Generates PDF for the specified articles'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--code', help='Four digit code (YYnn) of the article, will replace existing PDFs unless used with --new')
        parser.add_argument('--lang', help='Language of the article')
        parser.add_argument('--new', action='store_true', help='Generate PDFs for new activities')
        parser.add_argument('--all', action='store_true', help='(Re-)Generate PDFs for all activities')


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
                self.stdout.write(f"Skipping {version.master.code} in {version.language_code}")
                continue
            try:
                file_obj = version.generate_pdf()
            except Exception as e:
                self.stderr.write(f"{e}")
                self.stderr.write(f"Failed to create  {version.code} in {version.locale.language_code}")
                continue
            filename = f'astroedu-{version.code}-{version.locale.language_code}.pdf'
            version.pdf.delete(save=False)
            version.pdf.save(filename, ContentFile(file_obj))
            version.save()
            self.stdout.write(f'Written {filename}')
