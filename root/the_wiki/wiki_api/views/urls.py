from rest_framework import mixins, viewsets, permissions
from rest_framework.response import Response
from wiki.models import URLPath

from wiki_api.serializers import URLSerializer


class URLViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = URLPath.objects.all()
    serializer_class = URLSerializer

    def list(self, request, *args, **kwargs):
        """
        Override the list method so that we can reduce the number of fields that are returned.
        """
        queryset = URLPath.objects.all()
        serializer = URLSerializer(
            queryset,
            many=True,
            context={'request': request},
            fields=['id', 'url', 'article', 'slug', 'level', 'parent']
        )
        return Response(serializer.data)
