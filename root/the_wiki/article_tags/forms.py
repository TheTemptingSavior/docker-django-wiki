from django import forms
from django.utils.translation import gettext
from taggit.models import Tag
from wiki.core.plugins.base import PluginSidebarFormMixin

from .models import TagsOnArticle


class SidebarForm(PluginSidebarFormMixin):
    # new_tag = forms.CharField(required=False)
    add_tag = forms.ModelChoiceField(
        label="Add tags",
        queryset=Tag.objects.order_by("slug").all(),
        required=False,
        help_text="Select a tag to add to this article"
    )
    remove_tag = forms.ModelChoiceField(
        label="Remove tags",
        queryset=None,
        required=False,
        help_text="Select a tag to remove from this article"
    )

    def __init__(self, article, request, *args, **kwargs):
        self.article = article
        self.request = request
        if "instance" not in kwargs:
            # HACK: This should be provided by the `get_form_kwargs` in the `wiki_plugin.py` file
            existing_instance = TagsOnArticle.objects.filter(article=self.article).first()
            kwargs["instance"] = existing_instance if existing_instance else TagsOnArticle(article=self.article)

        super().__init__(*args, **kwargs)

        # Only grab and updated remove tag queryset if our instance has an ID
        if self.instance.id:
            self.fields["remove_tag"].queryset = self.instance.tags.order_by("slug").all()
        else:
            # HACK: We must provide a queryset, so create a query set that will always have 0 entries
            self.fields["remove_tag"].queryset = Tag.objects.filter(name__isnull=True).all()

    def _update_tags(self, instance):
        if self.cleaned_data["add_tag"]:
            instance.tags.add(self.cleaned_data["add_tag"])
        if self.cleaned_data["remove_tag"]:
            instance.tags.remove(self.cleaned_data["remove_tag"])

    def save(self, *args, **kwargs):
        if not self.instance.id:
            tags_on_article = TagsOnArticle(article=self.article)
            tags_on_article.article_revision = self.article.current_revision
            # Must save the article before we can access the tags property
            tags_on_article.save(*args, **kwargs)
            self._update_tags(tags_on_article)
            tags_on_article.save(*args, **kwargs)
            return tags_on_article

        self._update_tags(self.instance)
        return super().save(*args, **kwargs)

    def get_usermessage(self):
        return gettext("Tags for this article have been updated")

    class Meta:
        model = TagsOnArticle
        fields = ("add_tag",)
