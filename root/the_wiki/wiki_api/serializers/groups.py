from django.contrib.auth.models import Group
from rest_framework import serializers

from wiki_api.apps import WikiApiConfig


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "url", "name"]
        extra_kwargs = {"url": {"view_name": f"{WikiApiConfig.name}:group-detail"}}
