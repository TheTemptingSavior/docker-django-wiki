from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from wiki.models.article import Article, ArticleRevision

from .serializers import ArticleSerializer, ArticleRevisionSerializer, GroupSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class ArticleViewSet(viewsets.ViewSet):
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
    def list(self, request):
        queryset = ArticleRevision.objects.all()
        serializer = ArticleRevisionSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = ArticleRevision.objects.all()
        article = get_object_or_404(queryset, pk=pk)
        serializer = ArticleRevisionSerializer(article, many=False, context={'request': request})
        return Response(serializer.data)
