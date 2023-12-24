from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from wiki.models import URLPath

from wiki_api.serializers import URLSerializer


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
