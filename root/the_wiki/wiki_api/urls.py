from django.urls import path, include
from rest_framework_nested import routers

from . import views
from .apps import WikiApiConfig


app_name = WikiApiConfig.name

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
# Basename is a required argument here because these viewsets inherit the default ViewSet class - not a model specific
# one
router.register(r'articles', views.ArticleViewSet, basename='articles')
router.register(r'urls', views.URLViewSet, basename='urlpaths')

articles_router = routers.NestedDefaultRouter(router, r'articles', lookup='articles')
articles_router.register(r'revisions', views.ArticleRevisionViewSet, basename='articlerevisions')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(articles_router.urls)),
]
