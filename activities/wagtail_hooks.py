from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.admin.edit_handlers import FieldPanel
from taggit.models import Tag


class TagsModelAdmin(ModelAdmin):
    Tag.panels = [FieldPanel("name")]  # only show the name field
    model = Tag
    menu_label = "Tags"
    menu_icon = "tag"  # change as required
    menu_order = 100  # will put in 3rd place (000 being 1st, 100 2nd)
    list_display = ["name", "slug"]
    search_fields = ("name",)
    template_name = "admin/index.html"


modeladmin_register(TagsModelAdmin)
