from django.urls import path, reverse

from wagtail.admin.menu import MenuItem
from wagtail import hooks

from .views import index


@hooks.register('register_admin_urls')
def register_tag_url():
    return [
        path('tagsinspector/', index, name='tagslist'),
    ]

@hooks.register('register_admin_menu_item')
def register_tag_menu_item():
    return MenuItem('Tags', reverse('tagslist'), icon_name='tag')
