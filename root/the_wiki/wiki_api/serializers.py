from django.contrib.auth.models import Group, User
from rest_framework import serializers
from wiki.models.article import Article, ArticleRevision


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']
        extra_kwargs = {'url': {'view_name': 'wiki_api:user-detail'}}


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
        extra_kwargs = {'url': {'view_name': 'wiki_api:group-detail'}}


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'wiki_api:article-detail'}}


class ArticleRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRevision
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'wiki_api:articlerevision-detail'}}
