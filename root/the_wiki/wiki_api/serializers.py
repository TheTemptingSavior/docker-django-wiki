from django.contrib.auth.models import Group, User
from rest_framework import serializers
from rest_framework.reverse import reverse
from wiki.models.article import Article, ArticleRevision

from .apps import WikiApiConfig


class ParameterisedHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    lookup_fields = (('pk', 'pk'),)

    def __init__(self, *args, **kwargs):
        self.lookup_fields = kwargs.pop('lookup_fields', self.lookup_fields)
        super(ParameterisedHyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        print(f"obj={obj} type={type(obj)}")
        print(f"view_name={view_name}")
        print(f"request={request}")
        print(f"format={format}")
        kwargs = {}
        for model_field, url_param in self.lookup_fields:
            attr = obj
            for field in model_field.split('.'):
                attr = getattr(attr, field)
            kwargs[url_param] = attr
        print(f"kwargs={kwargs}")
        return reverse(view_name, kwargs=kwargs, request=request, format=format)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']
        extra_kwargs = {'url': {'view_name': f'{WikiApiConfig.name}:user-detail'}}


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
        extra_kwargs = {'url': {'view_name': f'{WikiApiConfig.name}:group-detail'}}


class ArticleRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRevision
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': f'{WikiApiConfig.name}:articlerevisions-detail'}}


class ArticleRevisionSerializerMinimal(serializers.ModelSerializer):
    url = ParameterisedHyperlinkedIdentityField(
        view_name=f'{WikiApiConfig.name}:articlerevisions-detail',
        lookup_fields=(('article.id', 'articles_pk'), ('id', 'pk')),
        read_only=True
    )

    class Meta:
        model = ArticleRevision
        fields = ['id', 'title', 'url', 'revision_number', 'previous_revision']
        extra_kwargs = {
            'url': {'view_name': f'{WikiApiConfig.name}:articlerevisions-detail'}
        }


class ArticleSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    current_revision = ArticleRevisionSerializerMinimal(read_only=True, allow_null=True)

    class Meta:
        model = Article
        fields = [
            'id',
            'url',
            'created',
            'modified',
            'group_read',
            'group_write',
            'other_read',
            'other_write',
            'owner',
            'group',
            'current_revision',
        ]
        extra_kwargs = {
            'url': {'view_name': f'{WikiApiConfig.name}:articles-detail'},
        }
