from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from wiki.models.article import Article, ArticleRevision
from wiki.models.urlpath import URLPath

from .serializers import ArticleSerializer, ArticleRevisionSerializer, GroupSerializer, URLSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class ArticleViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = Article.objects.all()
        serializer = ArticleSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Article.objects.all()
        article = get_object_or_404(queryset, pk=pk)
        serializer = ArticleSerializer(article, many=False, context={'request': request})
        return Response(serializer.data)


class ArticleRevisionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, articles_pk=None):
        queryset = ArticleRevision.objects.filter(article_id=articles_pk).all()
        serializer = ArticleRevisionSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, articles_pk=None, pk=None):
        queryset = ArticleRevision.objects.filter(article_id=articles_pk).all()
        article = get_object_or_404(queryset, pk=pk)
        serializer = ArticleRevisionSerializer(article, many=False, context={'request': request})
        return Response(serializer.data)


class URLViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        queryset = URLPath.objects.all()
        serializer = URLSerializer(
            queryset, many=True, context={'request': request}, fields=['id', 'url', 'article', 'slug', 'level', 'parent']
        )
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = URLPath.objects.all()
        article = get_object_or_404(queryset, pk=pk)
        serializer = URLSerializer(article, many=False, context={'request': request})
        return Response(serializer.data)
