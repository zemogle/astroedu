import json
import os
import re
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.core.management.base import CommandError, BaseCommand
from django.utils.crypto import get_random_string
from io import BytesIO
from wagtail.contrib.redirects.models import Redirect
from wagtail.core.models import Page, Site, Locale
from wagtail.core.rich_text import RichText
from wagtail.images.models import Image
from wagtail.users.models import UserProfile
import markdown
from bs4 import BeautifulSoup

from activities.models import Activity, Institution, Category, ActivityHome
from home.models import *

import logging

logger = logging.getLogger(__name__)

published_flag = {'false':False,'true':True}
flag = {'0':False,'1':True}

class Command(BaseCommand):
    """
    Add all activities and other content into wagtail
    """

    help = 'Add all activities and other content into wagtail'

    # def add_arguments(self, parser):
        # parser.add_argument("-f", "--full", dest='full', action='store_true', help="full website")

    def handle(self, *args, **options):
        codes = [lang for lang in settings.LANGUAGES[0]]
        for code in codes:
            l, c = Locale.objects.get_or_create(language_code=code)
            self.metainfo = self.process_meta()
            self.process_activity(lang=code)

    def process_meta(self):
        oldpages = parse_fixture(filename='import_content/activities.json')
        activity, trans, oldmeta = join_activites(oldpages)
        for id, meta in oldmeta.items():
            cat = Category(group=meta['group'], title=meta['title'], code=meta['code'])
            cat.save()
            meta['newid'] = cat.id
        return oldmeta

    def get_categories(self, categories):
        cids = [self.metainfo.get(c)['newid'] for c in categories if self.metainfo.get(c, None)]
        return Category.objects.filter(id__in=cids)

    def process_activity(self, lang):
        old_pages = parse_fixture(filename='import_content/activities.json')
        activitypages, trans, meta = join_activites(old_pages)
        self.stderr.write("Processing Activities - {} in {}".format(len(activitypages), lang))
        activityhome = ActivityHome(title="Activities")
        homepage = HomePage.objects.get(locale__language_code=lang)
        homepage.add_child(instance=activityhome)
        homepage.save()
        for key, fi in activitypages.items():
            if fi['language_code'] != lang or fi['code'] == '0000':
                continue
            newactivity  = Activity(
                title = fi['title'],
                abstract = RichText(markdown.markdown(fi['abstract'])),
                fulldesc = html_or_rich(fi['fulldesc']),
                goals = RichText(markdown.markdown(fi['goals'])),
                objectives = RichText(markdown.markdown(fi['objectives'])),
                teaser = fi['teaser'],
                acknowledgement = fi['acknowledgement'],
                evaluation = html_or_rich(fi['evaluation']),
                materials = html_or_rich(fi['materials']),
                background = html_or_rich(fi['background']),
                curriculum = html_or_rich(fi['curriculum']),
                additional_information = html_or_rich(fi['additional_information']),
                conclusion = RichText(markdown.markdown(fi['conclusion'])),
                short_desc_material = RichText(markdown.markdown(fi['short_desc_material'])),
                further_reading = RichText(markdown.markdown(fi['further_reading'])),
                reference = RichText(markdown.markdown(fi['reference'])),
                code = fi['code'],
                doi = fi['doi'],
                first_published_at = fi['creation_date'],
                live = fi['published'],
                latest_revision_created_at = fi['modification_date'],
                go_live_at = fi["release_date"],
                slug = fi['slug']
            )
            # newactivity.save()
            # try:
            activityhome.add_child(instance=newactivity)
            activityhome.save()
            self.stdout.write(f"Saved {newactivity.title}")
            newactivity.astronomical_scientific_category.add(*list(self.get_categories(fi['astronomical_scientific_category'])))
            newactivity.age.add(*list(self.get_categories(fi['age'])))
            newactivity.level.add(*list(self.get_categories(fi['level'])))
            newactivity.skills.add(*list(self.get_categories(fi['skills'])))
            newactivity.learning.add(*list(self.get_categories(fi['learning'])))
            newactivity.keywords.add(*[x.strip() for x in fi['keywords'].split(',')])
            newactivity.time = Category.objects.get(id=list(self.get_categories([fi['time']]))[0].id)
            newactivity.group = Category.objects.get(id=list(self.get_categories([fi['group']]))[0].id)
            newactivity.supervised = Category.objects.get(id=list(self.get_categories([fi['supervised']]))[0].id)
            newactivity.cost = Category.objects.get(id=list(self.get_categories([fi['cost']]))[0].id)
            newactivity.location = Category.objects.get(id=list(self.get_categories([fi['location']]))[0].id)
            newactivity.save()

            self.stdout.write(f"Saved Categories for {newactivity.title}")
            # except Exception as e:
            # self.stderr.write("Failed because {}".format(e))

def parse_fixture(filename):
    with open(filename,'r') as f:
        old_pages = json.load(f)

    return old_pages

def join_activites(old_pages):
    activities = {}
    trans = {}
    metadata = {}
    for p in old_pages:
        if p['model'] == "activities.activity":
            activities[p['pk']] = p['fields']
        elif p['model'] == "activities.activitytranslation":
            trans[p['fields']['master']] = p['fields']
        elif p['model'] == "activities.metadataoption":
            metadata[p['pk']] = p['fields']
    for k,v in activities.items():
        if trans.get(k):
            activities[k] = {**activities[k], **trans[k]}
    return activities, trans, metadata


def html_or_rich(mdcontent):
    content = replace_images_with_embeds(markdown.markdown(mdcontent, extensions=['tables']))
    if not content:
        return [('htmltext', '')]
    elif content.find("<table") != -1 :
        return [('htmltext', content)]
    else:
        return [('richtext', RichText(content))]

def image_replace(value):
    new_start = 0
    result = ''
    for m in re.finditer(r'src="(.*?)".*?>', value):
        new_src = m.group(1)
        # Only replace image src if URL not DIVIO cloud hosting
        if new_src.startswith('https://astroedu-'):
            path = urlparse(new_src).path
        else:
            path = new_src.replace("http://astroedu.iau.org/",'').replace('media/','')
        imgid = import_image(path)
        if imgid:
            result += value[new_start:m.start()] + '<embed id="%s" embedtype="image" format="left" alt=""/>' % imgid
        new_start = m.end()
    result += value[new_start:]
    return value

def replace_images_with_embeds(content):
    soup = BeautifulSoup(content, 'lxml')
    for img in soup.find_all("img"):
        if img['src'].startswith('https://astroedu-'):
            path = urlparse(img['src']).path
        else:
            path = img['src'].replace("http://astroedu.iau.org/",'').replace('media/','')
        imgid = import_image(path)
        if imgid:
            embed = soup.new_tag('embed')
            embed['format'] = 'fullwidth'
            embed['id'] = imgid
            embed['embedtype'] = 'image'
            embed['alt'] = path
            img.parent.insert_after(embed)
            img.decompose() # remove the unused img
            print(f'Replaced img with {imgid}')
    return soup.prettify()

def import_image(filename):
    filename = filename.strip("/").replace('%20',' ')
    name = filename.split('/')[-1]
    if default_storage.exists(filename):
        image = Image(file=ImageFile(file=default_storage.open(filename), name=name), title=name.rsplit('.',1)[0])
        image.save()
        return image.id
    else:
        return False
