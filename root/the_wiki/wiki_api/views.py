from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from typing import Optional
from wiki.models.article import Article, ArticleRevision
from wiki.models.urlpath import URLPath
from wiki.plugins.attachments.models import Attachment, AttachmentRevision

from .serializers import (
    ArticleSerializer,
    ArticleHTMLSerializer,
    ArticleRevisionSerializer,
    AttachmentSerializer,
    GroupSerializer,
    NewArticleSerializer,
    URLSerializer,
    UserSerializer,
    NewRevisionSerializer, AttachmentRevisionSerializer
)
from .types import CreateArticleBody, CreateArticleBodyPermission, CreateRevisionBody


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

    def create(self, request):
        serialized_data: NewArticleSerializer = NewArticleSerializer(data=request.data)

        if not serialized_data.is_valid():
            return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data: CreateArticleBody = serialized_data.data
        validated_permissions: CreateArticleBodyPermission = validated_data.get(
            "permissions",
            {"group": None, "group_read": True, "group_write": True, "other_read": True, "other_write": True}
        )

        # Find the parent URLPath object - or None if this is a root article
        parent_url: Optional[URLPath] = (
            get_object_or_404(URLPath, pk=validated_data["parent"])
            if validated_data["parent"] else None
        )

        # May or may not have been provided a slug - and it could also be empty
        if "slug" in validated_data:
            slug: str = slugify(validated_data["title"]) if not validated_data["slug"] else validated_data["slug"]
        else:
            slug: str = slugify(validated_data["title"])

        new_urlpath: URLPath = URLPath.create_urlpath(
            parent=parent_url,
            slug=slug,
            title=validated_data["title"],
            article_kwargs={
                "owner": request.user,
                "group": validated_permissions["group"],
                "group_read": validated_permissions["group_read"],
                "group_write": validated_permissions["group_write"],
                "other_read": validated_permissions["other_read"],
                "other_write": validated_permissions["other_write"],
            },
            request=request,
            article_w_permissions=None,
            content=validated_data["content"],
            user_message=validated_data["summary"],
            user=request.user,
            ip_address=None,
        )

        # Grab the article data we just created and return this instead of the URLPath
        new_article = ArticleSerializer(new_urlpath.article, context={"request": request}).data
        return Response(new_article, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        # TODO: Should create a new revision on an article
        pass

    @action(detail=True, methods=["GET"], name="Get HTML")
    def html(self, request, pk=None, *args, **kwargs):
        article = get_object_or_404(Article.objects.all(), pk=pk)
        serializer = ArticleHTMLSerializer(article, many=False, context={"request": request})
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

    def create(self, request, articles_pk=None):
        current_article: Article = get_object_or_404(Article, pk=articles_pk)

        serialized_data: NewRevisionSerializer = NewRevisionSerializer(data=request.data)
        if not serialized_data.is_valid():
            return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data: CreateRevisionBody = serialized_data.data
        new_revision = ArticleRevision(
            article_id=current_article.id,
            content=validated_data["content"],
            user=self.request.user,
            user_message=validated_data.get("user_message", "")
        )

        current_article.add_revision(new_revision)
        article_data = ArticleSerializer(data=current_article, many=False, context={"request": request})
        return Response(article_data.data, status=status.HTTP_201_CREATED)


class AttachmentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, articles_pk=None):
        queryset = Attachment.objects.filter(article_id=articles_pk).all()
        serializer = AttachmentSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, articles_pk=None, pk=None):
        queryset = Attachment.objects.filter(article_id=articles_pk).all()
        article = get_object_or_404(queryset, pk=pk)
        serializer = AttachmentSerializer(article, many=False, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['GET'], name='Download')
    def download(self, request, articles_pk=None, pk=None):
        # TODO: Implement a download for the current revision of the attachment
        return Response([])


class AttachmentRevisionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, articles_pk=None, attachments_pk=None):
        queryset = AttachmentRevision.objects.filter(attachment_id=attachments_pk).all()
        serializer = AttachmentRevisionSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, articles_pk=None, attachments_pk=None, pk=None):
        queryset = AttachmentRevision.objects.filter(attachment_id=attachments_pk).all()
        attachment = get_object_or_404(queryset, pk=pk)
        serializer = AttachmentRevisionSerializer(attachment, many=False, context={'request': request})
        return Response(serializer.data)


class URLViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = URLPath.objects.all()
        serializer = URLSerializer(
            queryset,
            many=True,
            context={'request': request},
            fields=['id', 'url', 'article', 'slug', 'level', 'parent']
        )
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = URLPath.objects.all()
        article = get_object_or_404(queryset, pk=pk)
        serializer = URLSerializer(article, many=False, context={'request': request})
        return Response(serializer.data)
