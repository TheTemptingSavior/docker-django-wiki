from rest_framework import serializers
from rest_framework.reverse import reverse_lazy
from wiki.models import URLPath

from wiki_api.apps import WikiApiConfig
from wiki_api.serializers import DynamicFieldsModelSerializer
from wiki_api.serializers.articles import ArticleSerializer


class URLSerializer(DynamicFieldsModelSerializer):
    article = ArticleSerializer(read_only=True, fields=["id", "url", "created", "modified"])
    url = serializers.HyperlinkedIdentityField(view_name=f"{WikiApiConfig.name}:urlpaths-detail")
    parent_url = serializers.SerializerMethodField()

    def get_parent_url(self, obj):
        if obj.parent:
            return reverse_lazy(
                f"{WikiApiConfig.name}:urlpaths-detail", kwargs={"pk": obj.parent.id}, request=self.context["request"]
            )
        return None

    class Meta:
        model = URLPath
        fields = "__all__"
        extra_kwargs = {
            "url": {"view_name": f"{WikiApiConfig.name}:urlpaths-detail"},
        }
