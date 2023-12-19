from django.contrib.auth.models import Group, User
from rest_framework import serializers
from rest_framework.reverse import reverse, reverse_lazy
from wiki.models.article import Article, ArticleRevision
from wiki.models.urlpath import URLPath

from .apps import WikiApiConfig


class ParameterisedHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    lookup_fields = (('pk', 'pk'),)

    def __init__(self, *args, **kwargs):
        self.lookup_fields = kwargs.pop('lookup_fields', self.lookup_fields)
        super(ParameterisedHyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        kwargs = {}
        for model_field, url_param in self.lookup_fields:
            attr = obj
            for field in model_field.split('.'):
                attr = getattr(attr, field)
            kwargs[url_param] = attr
        return reverse(view_name, kwargs=kwargs, request=request, format=format)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'groups']
        extra_kwargs = {'url': {'view_name': f'{WikiApiConfig.name}:user-detail'}}


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
        extra_kwargs = {'url': {'view_name': f'{WikiApiConfig.name}:group-detail'}}


class ArticleRevisionSerializer(DynamicFieldsModelSerializer):
    url = ParameterisedHyperlinkedIdentityField(
        view_name=f'{WikiApiConfig.name}:articlerevisions-detail',
        lookup_fields=(('article.id', 'articles_pk'), ('id', 'pk')),
        read_only=True
    )

    class Meta:
        model = ArticleRevision
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': f'{WikiApiConfig.name}:articlerevisions-detail'}}


class ArticleSerializer(DynamicFieldsModelSerializer):
    owner = UserSerializer(read_only=True, fields=['id', 'url', 'username'])
    current_revision = ArticleRevisionSerializer(
        read_only=True, allow_null=True, fields=['id', 'url', 'title', 'revision_number', 'previous_revision']
    )

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


class ArticleHTMLSerializer(serializers.ModelSerializer):
    html = serializers.SerializerMethodField()

    def get_html(self, obj: Article):
        return obj.render(user=self.context["request"].user)

    class Meta:
        model = Article
        fields = ["html"]


class URLSerializer(DynamicFieldsModelSerializer):
    article = ArticleSerializer(read_only=True, fields=['id', 'url', 'created', 'modified'])
    url = serializers.HyperlinkedIdentityField(view_name=f'{WikiApiConfig.name}:urlpaths-detail')
    parent_url = serializers.SerializerMethodField()

    def get_parent_url(self, obj):
        if obj.parent:
            return reverse_lazy(
                f'{WikiApiConfig.name}:urlpaths-detail', kwargs={'pk': obj.parent.id}, request=self.context["request"]
            )
        return None

    class Meta:
        model = URLPath
        fields = '__all__'
        extra_kwargs = {
            'url': {'view_name': f'{WikiApiConfig.name}:urlpaths-detail'},
        }
