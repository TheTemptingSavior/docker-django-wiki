from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from wiki.plugins.attachments.models import Attachment, AttachmentRevision

from wiki_api.serializers import AttachmentSerializer, AttachmentRevisionSerializer


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
