from django.utils.translation import gettext as _

from wiki.core.plugins import registry
from wiki.core.plugins.base import BasePlugin

from . import settings
from .forms import SidebarForm
from .models import TagsOnArticle


class ArticleTagsPlugin(BasePlugin):
    slug = settings.SLUG

    sidebar = {
        "headline": _("Tags"),
        "icon_class": "fa-tag",
        "template": "article_tags/sidebar.html",
        "form_class": SidebarForm,
        "get_form_kwargs": (lambda a: {"instance": TagsOnArticle(article=a)})
    }


registry.register(ArticleTagsPlugin)
