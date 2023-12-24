from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from wiki.plugins.attachments.models import Attachment, AttachmentRevision

from wiki_api.serializers import AttachmentSerializer, AttachmentRevisionSerializer


class AttachmentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttachmentSerializer

    def get_queryset(self):
        queryset = Attachment.objects.all()
        article_id = self.kwargs.get("articles_pk")
        if article_id:
            queryset = queryset.filter(article_id=article_id)

        return queryset

    @action(detail=True, methods=['GET'], name='Download')
    def download(self, request, articles_pk=None, pk=None):
        # TODO: Implement a download for the current revision of the attachment
        return Response([])


class AttachmentRevisionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttachmentRevisionSerializer

    def get_queryset(self):
        queryset = AttachmentRevision.objects.all()
        attachment_id = self.kwargs.get("attachments_pk")
        if attachment_id:
            queryset = queryset.filter(attachment_id=attachment_id)

        return queryset
