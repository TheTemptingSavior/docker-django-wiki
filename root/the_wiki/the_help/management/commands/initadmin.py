import os

from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Create a default admin user"

    def handle(self, *args, **options):
        username = os.environ.get("WIKI_ADMIN_USERNAME")
        password = os.environ.get("WIKI_ADMIN_PASSWORD")

        existing_admin = User.objects.filter(username=username).first()
        if existing_admin:
            self.stdout.write("Admin user already exists. Exiting!")
            return

        new_admin = User(username=username)
        new_admin.set_password(password)
        new_admin.is_superuser = True
        new_admin.is_staff = True
        new_admin.is_active = True
        new_admin.save()
        self.stdout.write("New admin user created!")
