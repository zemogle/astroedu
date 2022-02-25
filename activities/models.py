from django import forms
from django.db import models
from django.contrib.auth.models import User

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel, \
    InlinePanel, PageChooserPanel
from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page, TranslatableMixin,  Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.contrib.table_block.blocks import TableBlock
from taggit.models import TaggedItemBase
from wagtail.documents.models import Document

from activities import utils

class BodyBlock(blocks.StreamBlock):
    richtext = blocks.RichTextBlock()
    htmltext = blocks.RawHTMLBlock()
    table =  TableBlock(template="home/partials/table_template.html")

class ActivityHome(Page):
    pass

class Keyword(TaggedItemBase):
    content_object = ParentalKey('Activity', on_delete=models.CASCADE, related_name='keyword_items')

@register_snippet
class Category(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Location(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Skills(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Level(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Learning(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Group(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Supervised(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Cost(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Age(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Time(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Institute(models.Model):
    name = models.CharField(blank=False, max_length=255)
    fullname = models.CharField(max_length=255, blank=True, help_text='If set, the full name will be used in some places instead of the name', )
    country = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, null=True, max_length=255 )

    def __str__(self):
        return self.name

@register_snippet
class Person(models.Model):
    name = models.CharField(blank=False, max_length=255)
    citable_name = models.CharField(blank=True, max_length=255, help_text='Required for astroEDU activities')
    email = models.EmailField(blank=False, max_length=255)
    institution = models.ForeignKey(Institute, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} at {self.institution}"

class AuthorInstitute(Orderable, models.Model):
    activity = ParentalKey('activities.Activity', related_name='author_institute', on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)

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

    class Meta:
        verbose_name = "author"

    panels = [
        SnippetChooserPanel('author'),
    ]

    def __str__(self):
        return self.display_name()


class Activity(Page):
    abstract = RichTextField(blank=True, help_text='200 words', verbose_name='Abstract')
    # theme = models.CharField(blank=False, max_length=40, help_text='Use top level AVM metadata')
    keywords = ClusterTaggableManager(through=Keyword, blank=True)

    acknowledgement = models.CharField(blank=True, max_length=255)
    teaser = models.TextField(blank=True, verbose_name='Teaser', help_text='Maximum 2 sentences! Maybe what and how?')

    goals = RichTextField()
    objectives = RichTextField(verbose_name='Learning Objectives', )
    evaluation = StreamField(BodyBlock, help_text='If the teacher/educator wants to evaluate the impact of the activity, how can she/he do it?')
    materials = StreamField(BodyBlock, blank=True, verbose_name='List of material', help_text='Please indicate costs and/or suppliers if possible')
    background = StreamField(BodyBlock, verbose_name='Background Information', )
    fulldesc = StreamField(BodyBlock, verbose_name='Full description of the activity')
    curriculum = StreamField(BodyBlock, blank=True, verbose_name='Connection to school curriculum', help_text='Please indicate which country')
    additional_information = StreamField(BodyBlock, blank=True, help_text='Notes, Tips, Resources, Follow-up, Questions, Safety Requirements, Variations')
    conclusion = RichTextField()

    short_desc_material = RichTextField(blank=True, verbose_name='Short description of Suplementary material')
    further_reading = RichTextField(blank=True, verbose_name='Further reading', default='')
    reference = RichTextField(blank=True, verbose_name='References')

    pdf = models.FileField(upload_to='pdf/', blank=True, null=True, help_text="PDF will be autogenerated after publication. Do not upload one.")

    code = models.CharField(max_length=4, help_text='The 4 digit code that identifies the Activity, in the format "YY##": year, folowed by sequential number.')
    doi = models.CharField(blank=True, max_length=50, verbose_name='DOI', help_text='Digital Object Identifier, in the format XXXX/YYYY. See http://www.doi.org/')

# Meta data
    astro_category = ParentalManyToManyField(Category, blank=True, verbose_name='Astronomical Scientific Categories')

    age = ParentalManyToManyField('activities.Age',blank=True)
    level = ParentalManyToManyField(Level, help_text='Specify at least one of "Age" and "Level". ', verbose_name='Education level', blank=True)
    time = models.ForeignKey(Time, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, verbose_name='Group or individual activity')
    supervised = models.ForeignKey(Supervised, on_delete=models.SET_NULL, null=True, verbose_name='Supervised for safety')
    cost = models.ForeignKey(Cost, on_delete=models.SET_NULL, null=True, verbose_name='Cost per student')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    skills = ParentalManyToManyField(Skills, blank=True, verbose_name='core skills')
    learning = ParentalManyToManyField(Learning, blank=True, verbose_name='type of learning activity', help_text='Enquiry-based learning model')

    featured = models.BooleanField(default=False, help_text="Feature on homepage")

    original_author = models.CharField(max_length=255,
                    blank=True,
                    null=True,
                    help_text='Original Author of the activity (if not the authors listed above')

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('featured'),
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
            StreamFieldPanel('additional_information'),
            FieldPanel('conclusion'),
            FieldPanel('short_desc_material'),
            FieldPanel('further_reading'),
            FieldPanel('reference'),
            InlinePanel('attachment_documents', label="Attachment(s)"),
        ], heading="Activity Information"),
        MultiFieldPanel([
            FieldPanel('astro_category', widget=forms.CheckboxSelectMultiple),
            FieldPanel('location', widget=forms.Select),
            FieldPanel('keywords'),
            FieldPanel('age', widget=forms.CheckboxSelectMultiple),
            FieldPanel('level', widget=forms.CheckboxSelectMultiple),
            FieldPanel('time', widget=forms.Select),
            FieldPanel('group', widget=forms.Select),
            FieldPanel('supervised', widget=forms.Select),
            FieldPanel('cost', widget=forms.Select),
            FieldPanel('skills', widget=forms.CheckboxSelectMultiple),
            FieldPanel('learning', widget=forms.CheckboxSelectMultiple),
            InlinePanel('author_institute', label="Author(s)"),
        ], heading="Meta data")
    ]

    def age_range(self):
        age_ranges = [obj.name for obj in self.age.all()]
        return utils.beautify_age_range(age_ranges)

    def levels_joined(self):
        levels = [obj.name for obj in self.level.all()]
        return ', '.join(levels)

    def skills_joined(self):
        skills = [obj.name for obj in self.skills.all()]
        return ', '.join(skills)

    def learning_joined(self):
        learning = [obj.name for obj in self.learning.all()]
        return ', '.join(learning)

    def categories_joined(self):
        astro_category = [obj.name for obj in self.astro_category.all()]
        return ', '.join(astro_category)

    @property
    def author_list(self):
        result = []
        for item in self.author_institute.all():
            result.append(item.display_name())
        return '; '.join(result)

    def citable_author_list(self):
        result = []
        for item in self.author_institute.all():
            result.append(item.author.citable_name)
        return '; '.join(result)

    def get_context(self, request):
        context = super().get_context(request)
        context['sections']  = [
                {'code':'goals', 'text':'Goals', 'content':self.goals,'stream':False},
                {'code':'objectives','text':'Learning Objectives','content': self.objectives, 'stream':False},
                {'code':'background', 'text':'Background', 'content':self.background,'stream':True},
                {'code':'fulldesc', 'text':'Full Description', 'content':self.fulldesc,'stream':True},
                {'code':'evaluation', 'text':'Evaluation', 'content':self.evaluation,'stream':True},
                {'code':'curriculum', 'text':'Curriculum', 'content':self.curriculum,'stream':True},
                {'code':'additional_information', 'text':'Additional Information', 'content':self.additional_information,'stream':True},
                {'code':'conclusion', 'text':'Conclusion', 'content':self.conclusion,'stream':False},
        ]
        context['meta'] = [
                {'code':'astro_category', 'text': 'Category', 'content':self.categories_joined()},
                {'code':'location', 'text': 'Location', 'content':self.location},
                {'code':'age', 'text': 'Age', 'content':self.age_range()},
                {'code':'level', 'text': 'Level', 'content':self.levels_joined()},
                {'code':'time', 'text': 'Time', 'content':self.time},
                {'code':'group', 'text': 'Group', 'content':self.group},
                {'code':'supervised', 'text': 'Supervised', 'content':self.supervised},
                {'code':'cost', 'text': 'Cost', 'content':self.cost},
                {'code':'skills', 'text': 'Skills', 'content':self.skills_joined()},
                {'code':'learning', 'text': 'Learning', 'content':self.learning_joined()},
        ]
        return context

class Attachment(Orderable):
    page = ParentalKey(Activity, on_delete=models.CASCADE, related_name='attachment_documents')
    document =  models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='attachments'
    )

    panels = [
        DocumentChooserPanel('document'),
    ]

class CollectionIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

class Collection(Page):
    description = RichTextField(blank=True, verbose_name='brief description', )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        ImageChooserPanel('image'),
        InlinePanel('activity_pages', label="Activity Pages")
    ]

    @property
    def code(self):
        return self.slug

    @property
    def main_visual(self):
        return self.image.file if self.image else None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
#        tasks.make_thumbnail.delay(self)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('collections:detail', args=[self.slug])

class CollectionPage(Orderable):
    page = ParentalKey(Collection, on_delete=models.CASCADE, related_name='activity_pages')
    activity = models.ForeignKey(Activity, related_name='+', on_delete=models.SET_NULL, null=True)

    panels = [
        PageChooserPanel('activity'),
    ]
