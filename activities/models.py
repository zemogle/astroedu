from django.db import models
from django.contrib.auth.models import User

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page, TranslatableMixin
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.contrib.table_block.blocks import TableBlock
from taggit.models import TaggedItemBase


class ActivityHome(Page):
    pass

class Keyword(TaggedItemBase):
    content_object = ParentalKey('Activity', on_delete=models.CASCADE, related_name='keyword_items')

class Institution(Page):
    description = RichTextField(blank=True, null=True, help_text='Text to appear in Institution page')
    fullname = models.CharField(max_length=255, blank=True, help_text='If set, the full name will be used in some places instead of the name', )
    country = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, null=True, max_length=255, )
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
            ImageChooserPanel('logo'),
            FieldPanel('description'),
            FieldPanel('fullname'),
            FieldPanel('url'),
        ]

class Person(models.Model):
    name = models.CharField(blank=False, max_length=255)
    citable_name = models.CharField(blank=True, max_length=255, help_text='Required for astroEDU activities')
    email = models.EmailField(blank=False, max_length=255)
    institution = models.ForeignKey(Institution, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

@register_snippet
class Category(TranslatableMixin, models.Model):
    title = models.CharField(max_length=255)
    group = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    panels = [
        FieldPanel('title'),
        FieldPanel('code'),
        FieldPanel('group'),
    ]

    def __str__(self):
        return f"{self.title}"

    class Meta:
        unique_together = ('translation_key', 'locale')

class Activity(Page):
    abstract = RichTextField(blank=True, help_text='200 words', verbose_name='Abstract')
    # theme = models.CharField(blank=False, max_length=40, help_text='Use top level AVM metadata')
    keywords = ClusterTaggableManager(through=Keyword, blank=True)

    acknowledgement = models.CharField(blank=True, max_length=255)
    teaser = models.TextField(blank=True, verbose_name='Teaser', help_text='Maximum 2 sentences! Maybe what and how?')

    goals = RichTextField()
    objectives = RichTextField(verbose_name='Learning Objectives', )
    evaluation = StreamField([
        ('richtext', blocks.RichTextBlock()),
        ('htmltext', blocks.RawHTMLBlock()),
        ('table', TableBlock(template="home/partials/table_template.html")),
    ], help_text='If the teacher/educator wants to evaluate the impact of the activity, how can she/he do it?')
    materials = StreamField([
        ('richtext', blocks.RichTextBlock()),
        ('htmltext', blocks.RawHTMLBlock()),
        ('table', TableBlock(template="home/partials/table_template.html")),
    ], blank=True, verbose_name='List of material', help_text='Please indicate costs and/or suppliers if possible')
    background = StreamField([
        ('richtext', blocks.RichTextBlock()),
        ('htmltext', blocks.RawHTMLBlock()),
        ('table', TableBlock(template="home/partials/table_template.html")),
    ], verbose_name='Background Information', )
    fulldesc = StreamField([
        ('richtext', blocks.RichTextBlock()),
        ('htmltext', blocks.RawHTMLBlock()),
        ('table', TableBlock(template="home/partials/table_template.html")),
    ], verbose_name='Full description of the activity')
    curriculum = StreamField([
        ('richtext', blocks.RichTextBlock()),
        ('htmltext', blocks.RawHTMLBlock()),
        ('table', TableBlock(template="home/partials/table_template.html")),
    ], blank=True, verbose_name='Connection to school curriculum', help_text='Please indicate which country')
    additional_information = StreamField([
        ('richtext', blocks.RichTextBlock()),
        ('htmltext', blocks.RawHTMLBlock()),
        ('table', TableBlock(template="home/partials/table_template.html")),
    ], blank=True, help_text='Notes, Tips, Resources, Follow-up, Questions, Safety Requirements, Variations')
    conclusion = RichTextField()

    # version 9
    short_desc_material = RichTextField(blank=True, verbose_name='Short description of Suplementary material')
    further_reading = RichTextField(blank=True, verbose_name='Further reading', default='')
    reference = RichTextField(blank=True, verbose_name='References')

    pdf = models.FileField(upload_to='pdf/', blank=True, null=True, help_text="PDF will be autogenerated after publication. Do not upload one.")

    code = models.CharField(max_length=4, help_text='The 4 digit code that identifies the Activity, in the format "YY##": year, folowed by sequential number.')
    doi = models.CharField(blank=True, max_length=50, verbose_name='DOI', help_text='Digital Object Identifier, in the format XXXX/YYYY. See http://www.doi.org/')

# Meta data
    astronomical_scientific_category = ParentalManyToManyField('activities.Category', related_name='+', limit_choices_to={'group': 'astronomical_categories'}, verbose_name='Astronomical Scientific Categories', blank=True, null=True)

    age = ParentalManyToManyField('activities.Category',limit_choices_to={'group': 'age'}, related_name='age', blank=True, null=True)
    level = ParentalManyToManyField('activities.Category',limit_choices_to={'group': 'level'}, related_name='level+', help_text='Specify at least one of "Age" and "Level". ', verbose_name='Education level', blank=True, null=True)
    time = models.ForeignKey('activities.Category',limit_choices_to={'group': 'time'}, related_name='time+', on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(Category, limit_choices_to={'group': 'group'}, related_name='+', verbose_name='Group or individual activity', null=True, blank=True, on_delete=models.SET_NULL)
    supervised = models.ForeignKey(Category, limit_choices_to={'group': 'supervised'}, related_name='+', verbose_name='Supervised for safety', on_delete=models.SET_NULL,null=True, blank=True)
    cost = models.ForeignKey(Category, limit_choices_to={'group': 'cost'}, null=True, blank=True, verbose_name='Cost per student', on_delete=models.SET_NULL)
    location = models.ForeignKey(Category, limit_choices_to={'group': 'location'}, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    skills = ParentalManyToManyField('activities.Category', limit_choices_to={'group': 'skills'}, related_name='skills+', verbose_name='core skills', blank=True, null=True)
    learning = ParentalManyToManyField('activities.Category', limit_choices_to={'group': 'learning'}, related_name='learning+', verbose_name='type of learning activity', help_text='Enquiry-based learning model', blank=True, null=True)

    original_author = models.CharField(max_length=255,
                    blank=True,
                    null=True,
                    verbose_name='Original Author of the activity (if not the authors listed above')


    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('code'),
            FieldPanel('doi'),
            FieldPanel('pdf'),
            FieldPanel('abstract'),
            FieldPanel('acknowledgement'),
            FieldPanel('teaser'),
        ], heading="Core Information"),
        MultiFieldPanel([
            FieldPanel('goals'),
            FieldPanel('objectives'),
            StreamFieldPanel('evaluation'),
            StreamFieldPanel('materials'),
            StreamFieldPanel('background'),
            StreamFieldPanel('fulldesc'),
            StreamFieldPanel('curriculum'),
            FieldPanel('additional_information'),
            FieldPanel('conclusion'),
            FieldPanel('short_desc_material'),
            FieldPanel('further_reading'),
            FieldPanel('reference'),
        ], heading="Activity Information"),
        MultiFieldPanel([
            FieldPanel('astronomical_scientific_category'),
            FieldPanel('keywords'),
            FieldPanel('age'),
            FieldPanel('level'),
            FieldPanel('time'),
            FieldPanel('group'),
            FieldPanel('supervised'),
            FieldPanel('cost'),
            FieldPanel('location'),
            FieldPanel('skills'),
            FieldPanel('learning'),
        ], heading="Meta data")
    ]

class AuthorInstitution(models.Model):
    activity = models.ForeignKey(Activity, related_name='authors', on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True)

    def display_name(self):
        # there were errors with no existing relations. Now display only relevant data
        display = []
        try:
            display.append(self.author.name)
        except:
            pass
        try:
            display.append(self.institution.name)
        except:
            pass
        return ', '. join(display)

    def __str__(self):
        return self.display_name()
