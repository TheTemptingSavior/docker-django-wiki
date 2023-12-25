from wiki.plugins.attachments.models import AttachmentRevision, Attachment

from wiki_api.apps import WikiApiConfig
from wiki_api.serializers import DynamicFieldsModelSerializer, ParameterisedHyperlinkedIdentityField
from wiki_api.serializers.users import UserSerializer, USER_MINIMAL_FIELDS


class AttachmentRevisionSerializer(DynamicFieldsModelSerializer):
    url = ParameterisedHyperlinkedIdentityField(
        view_name=f'{WikiApiConfig.name}:attachmentrevisions-detail',
        lookup_fields=((None, 'articles_pk'), ('attachment.id', 'attachments_pk'), ('id', 'pk')),
        read_only=True
    )
    user = UserSerializer(read_only=True, fields=USER_MINIMAL_FIELDS)

    class Meta:
        model = AttachmentRevision
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': f'{WikiApiConfig.name}:attachmentrevisions-detail'}}


class AttachmentSerializer(DynamicFieldsModelSerializer):
    url = ParameterisedHyperlinkedIdentityField(
        view_name=f'{WikiApiConfig.name}:attachments-detail',
        lookup_fields=(('article.id', 'articles_pk'), ('id', 'pk')),
        read_only=True
    )
    current_revision = AttachmentRevisionSerializer(
        read_only=True, many=False, fields=['id', 'revision_number', 'description', 'url']
    )

    class Meta:
        model = Attachment
        fields = '__all__'
        extra_kwargs = {
            'url': {'view_name': f'{WikiApiConfig.name}:attachments-detail'}
        }
