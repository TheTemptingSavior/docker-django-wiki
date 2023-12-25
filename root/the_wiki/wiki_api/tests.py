from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status


from the_wiki.settings import WIKI_API_ENABLED


class APITest(TestCase):
    admin_username = "admin"
    admin_password = "admin"

    def setUp(self):
        self.assertTrue(WIKI_API_ENABLED, "Wiki API not enabled. Failing tests")
        self.client = Client(headers={"Content-Type": "application/json", "Accept": "application/json"})
        self.user = User.objects.create_superuser(username=self.admin_username, password=self.admin_password)


class APIUserTest(APITest):
    default_user_keys = {
        "id",
        "url",
        "username",
        "email",
        "groups",
        "is_active",
        "last_name",
        "is_staff",
        "user_permissions",
        "first_name",
        "last_name",
        "is_superuser",
        "date_joined",
        "last_login",
    }

    # ###
    # ### Begin tests for GET '/api/users'
    # ###

    def test_user_list(self):
        """List all the users"""
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        # Issue a GET request.
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        assert "count" in response.data and response.data["count"] == 1
        assert "previous" in response.data and response.data["previous"] is None
        assert "next" in response.data and response.data["next"] is None
        assert len(response.data["results"]) == 1

        user = response.data["results"][0]
        self.assertEqual(set(user.keys()), self.default_user_keys)

    def test_user_list_not_logged_in(self):
        """Cannot list users without logging in"""
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_trailing_slash(self):
        """Redirect when missing a trailing slash"""
        response = self.client.get("/api/users", follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    # ###
    # ### Begin tests for POST '/api/users'
    # ###

    def test_user_create(self):
        """Create a user"""
        user_data = {"username": "test-user-1", "email": "test-user-1@example.com", "password": "helloworld"}
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))

        response = self.client.post("/api/users/", data=user_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(set(response.data.keys()), self.default_user_keys)

        self.assertIsNotNone(User.objects.get(pk=response.data["id"]))

    def test_user_create_not_logged_in(self):
        """Cannot create a user without logging in"""
        user_data = {"username": "test-user-1", "email": "test-user-1@example.com", "password": "helloworld"}
        response = self.client.post("/api/users/", data=user_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_create_trailing_slash(self):
        """Error on user create without a trailing slash"""
        user_data = {"username": "test-user-1", "email": "test-user-1@example.com", "password": "helloworld"}

        response = self.client.post("/api/users", data=user_data, content_type="application/json", follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_user_create_bad_data(self):
        """Cannot create user with incorrect post data"""
        user_data = {"name": "test-user-1"}
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))

        response = self.client.post("/api/users/", data=user_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0], "This field is required.")

    def user_create_duplicate_data(self):
        """Cannot create user with the same username"""
        user_data = {"username": "test-user-1", "email": "test-user-1@example.com", "password": "helloworld"}
        _new_user = User.objects.create_user(username=user_data["username"], password=user_data["password"])

        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))

        response = self.client.post("/api/users/", data=user_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    # ###
    # ### Begin tests for GET '/api/users/{user_id}/'
    # ###

    def test_user_detail(self):
        """Get a user by their ID"""
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.get(f"/api/users/{self.user.id}/")
        self.assertEqual(set(response.data.keys()), self.default_user_keys)

    def test_user_detail_not_logged_in(self):
        """Cannot get a user without logging in"""
        response = self.client.get(f"/api/users/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_trailing_slash(self):
        """Redirect when missing a trailing slash"""
        response = self.client.get(f"/api/users/{self.user.id}", follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_user_detail_not_found(self):
        """Return 404 when user is not found"""
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.get(f"/api/users/9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ###
    # ### Begin tests for DELETE '/api/users/{user_id}/'
    # ###

    def test_user_delete(self):
        """Delete a user"""
        new_user = User.objects.create_user(username="delete-me", password="will-be-deleted")

        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.delete(f"/api/users/{new_user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertRaises(User.DoesNotExist, User.objects.get, pk=new_user.pk)

    def test_user_delete_not_logged_in(self):
        """Cannot delete a user without logging in"""
        new_user = User.objects.create_user(username="delete-me", password="will-be-deleted")

        response = self.client.delete(f"/api/users/{new_user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_trailing_slash(self):
        """Redirect when missing a trailing slash on delete"""
        new_user = User.objects.create_user(username="delete-me", password="will-be-deleted")

        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.delete(f"/api/users/{new_user.pk}", follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_user_delete_not_found(self):
        """Return 404 when user is not found"""
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.delete(f"/api/users/9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ###
    # ### Begin tests for PUT '/api/users/{user_id}/'
    # ###

    def test_user_update(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.patch(
            f"/api/users/{self.user.id}/", data={"first_name": "New Name"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.keys(), self.default_user_keys)
        self.assertEqual(response.data["first_name"], "New Name")

        user = User.objects.get(pk=self.user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "New Name")

    def test_user_update_not_logged_in(self):
        response = self.client.patch(
            f"/api/users/{self.user.id}/", data={"first_name": "New Name"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_update_trailing_slash(self):
        response = self.client.patch(f"/api/users/{self.user.id}", data={"first_name": "New Name"}, follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_user_update_not_found(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))

        response = self.client.patch(f"/api/users/999/", data={"first_name": "New Name"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_update_duplicate_data(self):
        _new_user = User.objects.create_user(username="delete-me", password="will-be-deleted")
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))

        response = self.client.patch(
            f"/api/users/{self.user.id}/", data={"username": "delete-me"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0], "A user with that username already exists.")
