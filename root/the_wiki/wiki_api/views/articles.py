from typing import Optional

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import exception_handler
from wiki.models import Article, URLPath, ArticleRevision

from wiki_api.serializers import (
    ArticleSerializer,
    NewArticleSerializer,
    ArticleHTMLSerializer,
    ArticleRevisionSerializer,
    NewRevisionSerializer,
)
from wiki_api.types import CreateArticleBody, CreateArticleBodyPermission, CreateRevisionBody


class ArticleViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Article.objects.order_by("current_revision__title", "modified").all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArticleSerializer
    pagination_class = PageNumberPagination

    def get_serializer(self, *args, **kwargs):
        if "many" in kwargs and kwargs["many"] is True:
            kwargs["fields"] = ["id", "url", "current_revision"]
        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serialized_data: NewArticleSerializer = NewArticleSerializer(data=request.data, context={"request": request})

        if not serialized_data.is_valid():
            return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data: CreateArticleBody = serialized_data.data
        validated_permissions: CreateArticleBodyPermission = validated_data.get(
            "permissions",
            {"group": None, "group_read": True, "group_write": True, "other_read": True, "other_write": True},
        )

        # Find the parent URLPath object - or None if this is a root article
        parent_url: Optional[URLPath] = (
            get_object_or_404(URLPath, pk=validated_data["parent"]) if validated_data["parent"] else None
        )

        try:
            new_urlpath: URLPath = URLPath.create_urlpath(
                parent=parent_url,
                slug=validated_data["slug"],
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
        except IntegrityError as e:
            error = ParseError(detail=f"Failed to create article. Conflicting slug under the same parent")
            response = exception_handler(error, self.kwargs.get("context"))
            response.status_code = 409
            return response
        except Exception as e:
            error = ParseError(detail=f"Failed to create article: {e}")
            response = exception_handler(error, self.kwargs.get("context"))
            response.status_code = 400
            return response

        # Grab the article data we just created and return this instead of the URLPath
        new_article = ArticleSerializer(new_urlpath.article, context={"request": request}).data
        return Response(new_article, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        article = get_object_or_404(Article, pk=pk)

        serialized_data: NewRevisionSerializer = NewRevisionSerializer(data=request.data)
        if not serialized_data.is_valid():
            return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data: CreateRevisionBody = serialized_data.data

        new_revision = ArticleRevision()
        new_revision.article = article
        new_revision.content = validated_data["content"].strip()
        new_revision.title = validated_data.get("title", article.current_revision.title)
        new_revision.user_message = validated_data.get("user_message")
        new_revision.set_from_request(request)

        article.add_revision(new_revision)

        serialized_data = ArticleSerializer(article, context={"request": request}).data
        return Response(serialized_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], name="Get HTML")
    def html(self, request, pk=None, *args, **kwargs):
        article = get_object_or_404(self.queryset, pk=pk)
        serializer = ArticleHTMLSerializer(article, many=False, context={"request": request})
        return Response(serializer.data)


class ArticleRevisionViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    serializer_class = ArticleRevisionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = ArticleRevision.objects.all()
        pk = self.kwargs.get("articles_pk")
        if pk:
            queryset = queryset.filter(article_id=pk)

        return queryset

    def create(self, request, articles_pk=None, *args):
        current_article: Article = get_object_or_404(Article, pk=articles_pk)

        serialized_data: NewRevisionSerializer = NewRevisionSerializer(data=request.data)
        if not serialized_data.is_valid():
            return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data: CreateRevisionBody = serialized_data.data
        new_revision = ArticleRevision(
            article_id=current_article.id,
            content=validated_data["content"],
            user=self.request.user,
            user_message=validated_data.get("user_message", ""),
        )

        current_article.add_revision(new_revision)
        article_data = ArticleSerializer(data=current_article, many=False, context={"request": request})
        return Response(article_data.data, status=status.HTTP_201_CREATED)
