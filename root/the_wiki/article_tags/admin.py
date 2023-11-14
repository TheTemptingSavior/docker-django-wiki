from django.contrib import admin
from taggit_helpers.admin import TaggitCounter, TaggitStackedInline

from .models import TagsOnArticle


@admin.register(TagsOnArticle)
class TagsOnArticleAdmin(TaggitCounter, admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('article',)}),
    )
    inlines = [TaggitStackedInline]
    list_display = ("article", "taggit_counter")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
