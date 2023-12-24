from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from wiki.plugins.attachments.models import Attachment, AttachmentRevision

from wiki_api.renderers import PassthroughRenderer
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

    @action(detail=True, methods=['GET'], name='Download', renderer_classes=[PassthroughRenderer])
    def download(self, request, articles_pk=None, pk=None):
        attachment = get_object_or_404(Attachment, pk=pk)
        if not attachment.current_revision:
            return Response({"error": "Attachment has no current revision"}, status=status.HTTP_404_NOT_FOUND)

        instance = attachment.current_revision.file

        response = FileResponse(instance.open("rb"), content_type="application/octet-stream")
        response["Content-Length"] = instance.size
        response["Content-Disposition"] = f"attachment; filename={attachment.original_filename}"

        return response


class AttachmentRevisionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttachmentRevisionSerializer

    def get_queryset(self):
        queryset = AttachmentRevision.objects.all()
        attachment_id = self.kwargs.get("attachments_pk")
        if attachment_id:
            queryset = queryset.filter(attachment_id=attachment_id)

        return queryset

    @action(detail=True, methods=['GET'], name='Download', renderer_classes=[PassthroughRenderer])
    def download(self, request, articles_pk=None, attachments_pk=None, pk=None):
        attachment = get_object_or_404(Attachment, pk=attachments_pk)
        revision = get_object_or_404(AttachmentRevision, pk=pk)

        instance = revision.file

        response = FileResponse(instance.open("rb"), content_type="application/octet-stream")
        response["Content-Length"] = instance.size
        response["Content-Disposition"] = f"attachment; filename={attachment.original_filename}"

        return response
