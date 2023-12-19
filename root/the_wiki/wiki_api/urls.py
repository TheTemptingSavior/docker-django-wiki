from django.urls import include, path
from rest_framework import routers

from . import views
from .apps import WikiApiConfig


app_name = WikiApiConfig.name

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'articles', views.ArticleViewSet, basename='article')
router.register(r'article-revisions', views.ArticleRevisionViewSet, basename='articlerevision')

urlpatterns = router.urls
