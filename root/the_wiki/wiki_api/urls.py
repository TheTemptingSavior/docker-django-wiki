from django.urls import include, path
from rest_framework import routers

from . import views
from .apps import WikiApiConfig


app_name = WikiApiConfig.name

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = router.urls
