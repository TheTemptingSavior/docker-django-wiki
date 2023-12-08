from django import template

from article_tags.models import TagsOnArticle

register = template.Library()


@register.filter
def get_tags(value):
    tag_object = TagsOnArticle.objects.get(article=value)
    if tag_object:
        return tag_object.tags.all()

    return []
