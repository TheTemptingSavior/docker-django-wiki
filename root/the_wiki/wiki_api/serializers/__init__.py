from rest_framework import serializers
from rest_framework.reverse import reverse


class ParameterisedHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    lookup_fields = (("pk", "pk"),)

    def __init__(self, *args, **kwargs):
        self.lookup_fields = kwargs.pop("lookup_fields", self.lookup_fields)
        super(ParameterisedHyperlinkedIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        kwargs = {}
        for model_field, url_param in self.lookup_fields:
            if not model_field:
                kwargs[url_param] = None
                continue

            attr = obj
            for field in model_field.split("."):
                attr = getattr(attr, field)
            kwargs[url_param] = attr
        return reverse(view_name, kwargs=kwargs, request=request, format=format)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


from .users import UserSerializer  # noqa E402
from .groups import GroupSerializer  # noqa E402
from .attachments import AttachmentSerializer, AttachmentRevisionSerializer  # noqa E402
from .articles import (
    ArticleSerializer,
    ArticleRevisionSerializer,
    ArticleHTMLSerializer,
    NewArticleSerializer,
    NewRevisionSerializer,
)  # noqa E402
from .urls import URLSerializer  # noqa E402

__all__ = [
    # Helper serializers
    "ParameterisedHyperlinkedIdentityField",
    "DynamicFieldsModelSerializer",
    # Primary model serializers
    "GroupSerializer",
    "UserSerializer",  # requires group
    "AttachmentRevisionSerializer",
    "AttachmentSerializer",
    "ArticleRevisionSerializer",
    "ArticleSerializer",  # requires user/attachment/article revision
    "ArticleHTMLSerializer",
    "URLSerializer",  # requires article
    # Request body parsers
    "NewArticleSerializer",
    "NewRevisionSerializer",
]
