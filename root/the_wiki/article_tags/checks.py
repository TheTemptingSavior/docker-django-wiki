from django.apps import apps
from django.core.checks import Error


class Tags:
    required_installed_apps = "required_installed_apps"


def check_for_required_installed_apps(app_configs, **kwargs):
    errors = []
    if not apps.is_installed("taggit"):
        errors.append(Error("needs taggit in INSTALLED_APPS"))
    if not apps.is_installed("taggit_helpers"):
        errors.append(Error("needs taggit_helpers in INSTALLED_APPS"))
    return errors
