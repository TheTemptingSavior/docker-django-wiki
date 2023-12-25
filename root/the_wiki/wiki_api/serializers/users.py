from django.contrib.auth.models import User
from rest_framework import serializers

from wiki_api.apps import WikiApiConfig
from wiki_api.serializers import DynamicFieldsModelSerializer
from wiki_api.serializers.groups import GroupSerializer


USER_MINIMAL_FIELDS = ["id", "username", "url"]


class UserSerializer(DynamicFieldsModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name=f'{WikiApiConfig.name}:user-detail')

    class Meta:
        model = User
        exclude = ["password"]
        extra_kwargs = {'url': {'view_name': f'{WikiApiConfig.name}:user-detail'}}
