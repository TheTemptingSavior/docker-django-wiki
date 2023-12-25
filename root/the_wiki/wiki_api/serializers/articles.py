from django.contrib.sites.shortcuts import get_current_site
from django.utils.text import slugify
from rest_framework import serializers
from wiki.models import ArticleRevision, Article, URLPath

from wiki_api.apps import WikiApiConfig
from wiki_api.serializers import DynamicFieldsModelSerializer, ParameterisedHyperlinkedIdentityField
from wiki_api.serializers.attachments import AttachmentSerializer
from wiki_api.serializers.groups import GroupSerializer
from wiki_api.serializers.users import UserSerializer, USER_MINIMAL_FIELDS


class ArticleRevisionSerializer(DynamicFieldsModelSerializer):
    url = ParameterisedHyperlinkedIdentityField(
        view_name=f'{WikiApiConfig.name}:articlerevisions-detail',
        lookup_fields=(('article.id', 'articles_pk'), ('id', 'pk')),
        read_only=True
    )
    user = UserSerializer(read_only=True, fields=USER_MINIMAL_FIELDS)

    class Meta:
        model = ArticleRevision
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': f'{WikiApiConfig.name}:articlerevisions-detail'}}


class ArticleSerializer(DynamicFieldsModelSerializer):
    owner = UserSerializer(read_only=True, fields=USER_MINIMAL_FIELDS)
    group = GroupSerializer(read_only=True)
    current_revision = ArticleRevisionSerializer(
        read_only=True, allow_null=True, fields=['id', 'url', 'title', 'revision_number', 'previous_revision']
    )
    attachments = AttachmentSerializer(
        read_only=True, many=True, fields=['id', 'url', 'original_filename', 'current_revision'], allow_null=True
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
            'attachments',
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


class PermissionSerializer(serializers.Serializer):
    group = serializers.CharField(allow_blank=True, allow_null=True)
    group_read = serializers.BooleanField(default=True)
    group_write = serializers.BooleanField(default=True)
    other_read = serializers.BooleanField(default=True)
    other_write = serializers.BooleanField(default=True)


class NewArticleSerializer(serializers.Serializer):
    parent = serializers.IntegerField(allow_null=True)
    title = serializers.CharField(max_length=200, allow_null=False, allow_blank=False, required=True)
    slug = serializers.SlugField(allow_unicode=False, required=False, allow_blank=True, allow_null=True, max_length=50)
    content = serializers.CharField(allow_blank=True)
    summary = serializers.CharField(required=False, max_length=255)
    permissions = PermissionSerializer(required=False)

    def validate(self, data):
        if not data.get("slug"):
            data["slug"] = slugify(data["title"])

        existing = (
            URLPath.objects
            .filter(
                parent_id=data["parent"], slug=data["slug"], site=get_current_site(self.context.get("request"))
            )
            .count()
        )
        if existing:
            raise serializers.ValidationError("Article with this slug already exists under this parent URL.")

        return data


class NewRevisionSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, allow_blank=False)
    content = serializers.CharField(allow_blank=True, allow_null=True)
    user_message = serializers.CharField(max_length=255, allow_blank=True, required=False)

