from rest_framework import mixins, viewsets, permissions
from rest_framework.response import Response
from wiki.models import URLPath

from wiki_api.serializers import URLSerializer


class URLViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = URLPath.objects.all()
    serializer_class = URLSerializer

    def get_serializer(self, *args, **kwargs):
        if "many" in kwargs and kwargs["many"] is True:
            kwargs["fields"] = ["id", "url", "article", "slug", "level", "parent", "path"]

        return super().get_serializer(*args, **kwargs)
