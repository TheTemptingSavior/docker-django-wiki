from django.db import models
from taggit.managers import TaggableManager
from taggit.models import Tag, GenericTaggedItemBase
from wiki.models.pluginbase import SimplePlugin


# Create your models here.
class TagsOnArticle(SimplePlugin):
    tags = TaggableManager()
