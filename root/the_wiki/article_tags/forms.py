from django import forms
from django.utils.translation import gettext
from taggit.models import Tag
from wiki.core.plugins.base import PluginSidebarFormMixin

from .models import TagsOnArticle


class SidebarForm(PluginSidebarFormMixin):
    # new_tag = forms.CharField(required=False)
    add_tag = forms.ModelChoiceField(label="Add tags", queryset=Tag.objects.order_by("slug").all())
    remove_tag = forms.ModelChoiceField(label="Remove tags", queryset=None)

    def __init__(self, article, request, *args, **kwargs):
        self.article = article
        self.request = request
        if "instance" not in kwargs:
            # HACK: This should be provided by the `get_form_kwargs` in the `wiki_plugin.py` file
            existing_instance = TagsOnArticle.objects.filter(article=self.article).first()
            kwargs["instance"] = existing_instance if existing_instance else TagsOnArticle(article=self.article)

        super().__init__(*args, **kwargs)
        self.fields["add_tag"].required = False
        self.fields["remove_tag"].queryset = self.instance.tags.order_by("slug").all()

    def _update_tags(self, instance):
        if self.cleaned_data["add_tag"]:
            instance.tags.add(self.cleaned_data["add_tag"])
        if self.cleaned_data["remove_tag"]:
            instance.tags.remove(self.cleaned_data["remove_tag"])

    def save(self, *args, **kwargs):
        # TODO: Probably need some fancy logic here to handle first saving the new tag then adding it to our form
        if not self.instance.id:
            tags_on_article = TagsOnArticle(article=self.article)
            tags_on_article.article_revision = self.article.current_revision
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
