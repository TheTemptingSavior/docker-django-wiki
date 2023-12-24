from django.contrib.auth.models import User

from wiki_api.apps import WikiApiConfig
from wiki_api.serializers import DynamicFieldsModelSerializer
from wiki_api.serializers.groups import GroupSerializer


class UserSerializer(DynamicFieldsModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'groups']
        extra_kwargs = {'url': {'view_name': f'{WikiApiConfig.name}:user-detail'}}
