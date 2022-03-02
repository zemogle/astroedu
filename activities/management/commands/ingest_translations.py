import json
import os
import re
import sys
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
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
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail.users.models import UserProfile

from wagtail_localize.views.submit_translations import TranslationCreator
from wagtail_localize.models import Translation

import markdown
from bs4 import BeautifulSoup

from activities.models import *
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

    def add_arguments(self, parser):
        parser.add_argument("-l", "--lang", dest='lang', type=str, help="Import language version")
        parser.add_argument("-p", "--people", dest='people', action='store_true', help="Import just people")
        parser.add_argument("-c", "--collections", dest='collections', action='store_true', help="Import just collections")

    def handle(self, *args, **options):
        codes = [lang[0] for lang in settings.LANGUAGES]
        if options['lang'] and options['lang'] in codes:
            code = options['lang']
        else:
            code = 'en'
        old_pages = parse_fixture(filename='import_content/activities.json')

        activitypages, trans, meta, authors, institutes, attach = join_activites(old_pages, lang=code)

        l, c = Locale.objects.get_or_create(language_code=code)
        self.metainfo = self.process_meta(lang=code, metainfo=meta)
        self.process_activity(activitypages=activitypages, attach=attach, lang=code, authors=authors)

    def process_meta(self, lang, metainfo):
        group = {'time':Time,
                'supervised':Supervised,
                'skills':Skills,
                'location':Location,
                'level':Level,
                'learning':Learning,
                'group':Group,
                'cost':Cost,
                'categories':Category,
                'age':Age}
        # Translate old category IDs in new category iDs
        for id, meta in metainfo.items():
            try:
                obj, c = group[meta['group']].objects.get_or_create(name=meta['title'],locale__language_code='en')
            except KeyError as e:
                print(f"{e}")
                continue
            meta['newid'] = obj.id
        return metainfo

    def get_categories(self, categories, obj):
        cids = []
        for c in categories:
            if self.metainfo.get(c, None):
                try:
                    cid = self.metainfo.get(c)['newid']
                except:
                    continue
                cids.append(cid)
        return obj.objects.filter(id__in=cids)

    def process_activity(self, activitypages, attach, lang, authors):
        passed = []
        self.stdout.write("Processing Activities - {} in {}".format(len(activitypages), lang))
        locales = Locale.objects.filter(language_code=lang)
        user = User.objects.get(username='admin')
        tc = TranslationCreator(user=user, target_locales=locales)

        for count,(key, fi) in enumerate(activitypages.items()):
            print(f"Ingesting {count}")
            if fi['code'] == '1754' or fi['code'] == '0000':
                continue
            if not fi.get('language_code', None) or fi['language_code'] != lang or fi['code'] == '0000':
                passed.append(fi['code'])
                continue

            self.stdout.write(f"Updating {fi['code']} - {fi['title']}")
            activity  = Activity.objects.get(code = fi['code'], locale__language_code='en')
            tc.create_translations(instance=activity)
            key = activity.translation_key
            tr = Translation.objects.get(source__object_id=key)
            
            tr.enabled = False
            tr.save()
            print(f"Found and disabled translation")

            newactivity = Activity.objects.get(code=fi['code'], locale__language_code=lang)

            newactivity.title = fi['title']
            newactivity.abstract = RichText(markdown.markdown(fi['abstract']))
            newactivity.fulldesc = html_or_rich(fi['fulldesc'], 'fulldesc')
            newactivity.goals = RichText(markdown.markdown(fi['goals']))
            newactivity.objectives = RichText(markdown.markdown(fi['objectives']))
            newactivity.teaser = fi['teaser']
            newactivity.acknowledgement = fi['acknowledgement']
            newactivity.evaluation = html_or_rich(fi['evaluation'], 'eval')
            newactivity.materials = html_or_rich(fi['materials'], 'material')
            newactivity.background = html_or_rich(fi['background'], 'bg')
            newactivity.curriculum = html_or_rich(fi['curriculum'], 'curric')
            newactivity.additional_information = html_or_rich(fi['additional_information'])
            newactivity.conclusion = RichText(markdown.markdown(fi['conclusion']))
            newactivity.short_desc_material = RichText(markdown.markdown(fi['short_desc_material']))
            newactivity.further_reading = RichText(markdown.markdown(fi['further_reading']))
            newactivity.reference = RichText(markdown.markdown(fi['reference']))

            newactivity.save()

        print(f"Passed on {passed}")


def parse_fixture(filename):
    with open(filename,'r') as f:
        content = json.load(f)

    return content

def join_activites(old_pages, lang):
    activities = {}
    trans = {}
    metadata = {}
    authors = {}
    institutes = {}
    attach = {}
    for p in old_pages:
        if p['model'] == "activities.activity":
            activities[p['pk']] = p['fields']
        elif p['model'] == "activities.activitytranslation":
            if p['fields']["language_code"] == lang:
                trans[p['fields']['master']] = p['fields']
        elif p['model'] == "activities.metadataoption":
            metadata[p['pk']] = p['fields']
        elif p['model'] == "activities.authorinstitution":
            if authors.get(p['fields']['activity'], None):
                authors[p['fields']['activity']].append(p['fields']['author'])
            else:
                authors[p['fields']['activity']] = [p['fields']['author']]
            # Institute ID by author ID
            institutes[p['fields']['author']] = p['fields']['institution']
        elif p['model'] == "activities.attachment":
            if attach.get(p['fields']['hostmodel'], None):
                attach[p['fields']['hostmodel']].append(p['fields'])
            else:
                attach[p['fields']['hostmodel']] = [p['fields']]
    for k,v in activities.items():
        if trans.get(k):
            activities[k] = {**activities[k], **trans[k]}
    return activities, trans, metadata, authors, institutes, attach


def ingest_collections(oldpages):
    collection = {}
    collectionindex = CollectionIndexPage.objects.get(locale__language_code='en')
    for p in oldpages:
        if p['model'] == "activities.collection":
            collection[p['pk']] = {'trans':'', 'fields':p['fields']}
        if p['model'] == "activities.collectiontranslation":
            collection[p['fields']['master']]['trans'] = p['fields']
    for k, c in collection.items():
        try:
            coll = Collection.objects.get(title = c['trans']['title'])
            created = False
        except:
            created = True
            coll = Collection(title = c['trans']['title'])
        r = import_image(filename=c['fields']['image'])
        coll.description = c['trans']['description']
        if r:
            coll.image = Image.objects.get(id=r)
            print(f"Adding image {r}")
        if created:
            collectionindex.add_child(instance=coll)
        else:
            coll.save()
        print(f"Saved collection {coll.title}")
    return

def html_or_rich(mdcontent, code=None):
    content = replace_images_with_embeds(markdown.markdown(mdcontent, extensions=['tables']), code)
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

def replace_images_with_embeds(content, code=None):
    soup = BeautifulSoup(content, 'html.parser')
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
            if img.parent == soup:
                soup.insert(0,embed)
                img.decompose()
            else:
                try:
                    img.parent.insert_after(embed)
                    img.decompose() # remove the unused img
                    # print(f'Replaced img with {imgid}')
                except Exception as e:
                    sys.stderr.write(str(e))
                    sys.stderr.write(str(embed)+"\n")
                    sys.stderr.write(str(code)+"\n")
                    raise
    return soup.prettify()

def import_image(filename):
    filename = filename.strip("/").replace('%20',' ')
    name = filename.split('/')[-1]
    if default_storage.exists(filename):
        imfile = ImageFile(file=default_storage.open(filename), name=name)
        image, c = Image.objects.get_or_create(file=imfile, title=name.rsplit('.',1)[0])
        image.save()
        return image.id
    else:
        return False

def import_attachments(activity, filename):
    filename = filename.strip("/").replace('%20',' ')
    name = filename.split('/')[-1]
    if default_storage.exists(filename):
        try:
            docfile = File(file=default_storage.open(filename),name=name)
            doc, c = Document.objects.get_or_create(file=docfile, title=name.rsplit('.',1)[0])
            doc.save()
        except Exception as e:
            print(f"Problem with {filename} in {activity}: {e}")
            return False
        obj, c = Attachment.objects.get_or_create(page=activity, document=doc)
        return True
    else:
        return False
