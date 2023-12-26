from django.contrib.auth.models import User, Group
from django.test import Client, TestCase
from rest_framework import status
from wiki.models.article import Article, ArticleRevision
from wiki.models.urlpath import URLPath


from the_wiki.settings import WIKI_API_ENABLED


class APITest(TestCase):
    admin_username = "test-admin"
    admin_password = "test-admin"

    def setUp(self):
        self.assertTrue(WIKI_API_ENABLED, "Wiki API not enabled. Failing tests")
        self.client = Client(headers={"Content-Type": "application/json", "Accept": "application/json"})
        self.user = User.objects.create_superuser(username=self.admin_username, password=self.admin_password)


class APIUserTest(APITest):
    fixtures = ["1-content-types.yaml", "2-permissions.yaml", "3-groups.yaml", "4-users.yaml"]

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
    # ### Begin tests for GET '/api/users/'
    # ###

    def test_user_list(self):
        """List all the users"""
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        # Issue a GET request.
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue("count" in response.data and response.data["count"] == 5)
        self.assertTrue("previous" in response.data and response.data["previous"] is None)
        self.assertTrue("next" in response.data and response.data["next"] is None)
        self.assertTrue(len(response.data["results"]) == 5)

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
    # ### Begin tests for POST '/api/users/'
    # ###

    def test_user_create(self):
        """Create a user"""
        user_data = {"username": "test-user", "email": "test-user@example.com", "password": "helloworld"}
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

    def test_user_create_bad_email(self):
        """Cannot create user with non-email"""
        user_data = {"username": "new-user", "email": "not an email", "password": "Hello, World!"}
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post("/api/users/", data=user_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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


class APIGroupTest(APITest):
    fixtures = ["1-content-types.yaml", "2-permissions.yaml", "3-groups.yaml"]

    default_group_keys = {"id", "name", "url"}

    @property
    def groups(self):
        return Group.objects.order_by("pk").all()

    # ###
    # ### Begin tests for GET '/api/groups/'
    # ###

    def test_group_list(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))

        response = self.client.get("/api/groups/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), len(self.groups))
        group = response.data["results"][0]
        self.assertEqual(set(group.keys()), self.default_group_keys)

    def test_group_list_not_logged_in(self):
        response = self.client.get("/api/groups/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_list_trailing_slash(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))

        response = self.client.get("/api/groups", follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    # ###
    # ### Begin tests for POST '/api/groups/'
    # ###

    def test_group_create(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post("/api/groups/", data={"name": "new-group"}, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_group_create_trailing_slash(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post(
            "/api/groups", data={"name": "new-group"}, content_type="application/json", follow=False
        )
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_group_create_not_logged_in(self):
        response = self.client.post("/api/groups/", data={"name": "new-group"}, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_create_bad_data(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post("/api/groups/", data={"name": None}, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_group_create_duplicate(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post("/api/groups/", data={"name": "readers"}, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "group with this name already exists.")

    # ###
    # ### Begin tests for GET '/api/groups/{group_id}'
    # ###

    def test_group_detail(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.get(f"/api/groups/{self.groups[0].id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(set(response.data.keys()), self.default_group_keys)

    def test_group_detail_not_logged_in(self):
        response = self.client.get(f"/api/groups/{self.groups[0]}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_detail_trailing_slash(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.get(f"/api/groups/{self.groups[0].id}", follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_group_detail_not_found(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.get(f"/api/groups/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ###
    # ### Begin tests for DELETE '/api/groups/{group_id}'
    # ###

    def test_group_delete(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        group = self.groups[0]
        response = self.client.delete(f"/api/groups/{group.id}/", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertRaises(Group.DoesNotExist, Group.objects.get, pk=group.id)

    def test_group_delete_not_logged_in(self):
        response = self.client.delete(f"/api/groups/{self.groups[0].id}/", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_delete_trailing_slash(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.delete(f"/api/groups/{self.groups[0].id}", follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_group_delete_not_found(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.delete(f"/api/groups/999/", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ###
    # ### Begin tests for PUT '/api/groups/{group_id}'
    # ###

    def test_group_put(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.put(
            f"/api/groups/{self.groups[0].id}/", data={"name": "New Name"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Name")

    def test_group_put_not_logged_in(self):
        response = self.client.put(
            f"/api/groups/{self.groups[0].id}/", data={"name": "New Name"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_put_trailing_slash(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.put(
            f"/api/groups/{self.groups[0].id}", data={"name": "New Name"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_group_put_not_found(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.put(f"/api/groups/999/", data={"name": "New Name"}, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class APIArticleTest(APITest):
    fixtures = ["1-content-types.yaml", "2-permissions.yaml", "3-groups.yaml", "4-users.yaml", "5-articles.yaml"]

    default_list_keys = {"id", "url", "current_revision"}
    default_list_current_revision_keys = {"id", "url", "revision_number", "title", "previous_revision"}
    default_detail_keys = default_list_keys.union(
        {
            "created",
            "modified",
            "group_read",
            "group_write",
            "other_read",
            "other_write",
            "owner",
            "group",
            "attachments",
        }
    )

    @property
    def root_article(self):
        return URLPath.objects.filter(level=0).first()

    @property
    def articles(self):
        return Article.objects.order_by("id").all()

    # ###
    # ### Begin tests for GET '/api/articles/'
    # ###

    def test_article_list(self):
        self.client.login(username=self.admin_username, password=self.admin_password)
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue("count" in response.data and response.data["count"] == 4)
        self.assertTrue("previous" in response.data and response.data["previous"] is None)
        self.assertTrue("next" in response.data and response.data["next"] is None)
        self.assertTrue(len(response.data["results"]) == 4)

        article = response.data["results"][0]
        self.assertEqual(set(article.keys()), self.default_list_keys)
        self.assertEqual(set(article["current_revision"].keys()), self.default_list_current_revision_keys)

    def test_article_list_not_logged_in(self):
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_article_list_trailing_slash(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.get("/api/articles", follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    # ###
    # ### Begin tests for POST '/api/articles/'
    # ###

    def test_article_create(self):
        article_data = {
            "parent": self.root_article.id,
            "title": "Article from the API",
            "content": "# Hello, World!\n\nThis is the article body",
            "summary": "Test article",
            "permissions": {  # optional
                "group": None,
                "group_read": True,
                "group_write": True,
                "other_read": True,
                "other_write": True,
            },
        }
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post("/api/articles/", data=article_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), self.default_detail_keys)

        # Make sure the article was created
        new_article = Article.objects.get(id=response.data["id"])
        self.assertIsNotNone(new_article)
        self.assertEqual(new_article.current_revision.title, article_data["title"])

        # Make sure a URLPath was created
        url_path = URLPath.objects.filter(article__id=response.data["id"]).first()
        self.assertIsNotNone(url_path)
        self.assertEqual(url_path.slug, "article-from-the-api")

        response = self.client.get("/article-from-the-api/", follow=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_create_custom_slug(self):
        article_data = {
            "parent": self.root_article.id,
            "title": "Article from the API",
            "slug": "custom-slug",
            "content": "# Hello, World!\n\nThis is the article body",
            "summary": "Test article",
            "permissions": {  # optional
                "group": None,
                "group_read": True,
                "group_write": True,
                "other_read": True,
                "other_write": True,
            },
        }
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post("/api/articles/", data=article_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), self.default_detail_keys)

        # Make sure the article was created
        new_article = Article.objects.get(id=response.data["id"])
        self.assertIsNotNone(new_article)
        self.assertEqual(new_article.current_revision.title, article_data["title"])

        # Make sure a URLPath was created
        url_path = URLPath.objects.filter(article__id=response.data["id"]).first()
        self.assertIsNotNone(url_path)
        self.assertEqual(url_path.slug, "custom-slug")

        response = self.client.get("/custom-slug/", follow=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_create_no_permissions(self):
        article_data = {
            "parent": self.root_article.id,  # root article
            "title": "Article from the API",
            "slug": "custom-slug",
            "content": "# Hello, World!\n\nThis is the article body",
            "summary": "Test article",
        }
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post("/api/articles/", data=article_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), self.default_detail_keys)

        # Make sure the article was created
        new_article = Article.objects.get(id=response.data["id"])
        self.assertIsNotNone(new_article)
        self.assertEqual(new_article.current_revision.title, article_data["title"])

        # Make sure a URLPath was created
        url_path = URLPath.objects.filter(article__id=response.data["id"]).first()
        self.assertIsNotNone(url_path)
        self.assertEqual(url_path.slug, "custom-slug")

        response = self.client.get("/custom-slug/", follow=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_create_not_logged_in(self):
        article_data = {
            "parent": self.root_article.id,
            "title": "Article from the API",
            "slug": "custom-slug",
            "content": "# Hello, World!\n\nThis is the article body",
            "summary": "Test article",
        }
        response = self.client.post("/api/articles/", data=article_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_article_bad_data(self):
        article_data = {
            "parent": self.root_article.id,
            "content": "# Hello, World!\n\nThis is the article body",
            "summary": "Test article",
        }
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post("/api/articles/", data=article_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(response.data["title"][0], "This field is required.")

    def test_create_article_duplicate(self):
        article_data = {
            "parent": self.root_article.id,
            "title": "Article from the API",
            "content": "# Hello, World!\n\nThis is the article body",
            "summary": "Test article",
        }
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post("/api/articles/", data=article_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post("/api/articles/", data=article_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0], "Article with this slug already exists under this parent URL."
        )

    def test_create_article_second_root(self):
        article_data = {
            "parent": None,
            "title": "Should Not Matter",
            "content": "This is a duplicate root article",
        }
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.post("/api/articles/", data=article_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0], "A root article already exists. You must specify a parent."
        )

    # ###
    # ### Begin tests for GET '/api/articles/{article_id}/'
    # ###

    def test_article_detail(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.get(f"/api/articles/{self.articles[0].id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), self.default_detail_keys)
        self.assertEqual(set(response.data["current_revision"].keys()), self.default_list_current_revision_keys)

    def test_article_detail_not_logged_in(self):
        response = self.client.get(f"/api/articles/{self.articles[0].id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_article_detail_trailing_slash(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.get(f"/api/articles/{self.articles[0].id}", follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_article_detail_not_found(self):
        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.get("/api/articles/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ###
    # ### Begin tests for PUT '/api/articles/{article_id}/'
    # ###

    def test_article_put(self):
        article_data = {"title": "New Title", "content": "", "user_message": ""}

        # Gather information first
        root_article_revision_id = self.root_article.article.current_revision.id

        self.assertTrue(self.client.login(username=self.admin_username, password=self.admin_password))
        response = self.client.put(
            f"/api/articles/{self.root_article.id}/", data=article_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        root_url = URLPath.objects.filter(parent__isnull=True).first()
        self.assertIsNotNone(root_url)
        root_article = root_url.article
        self.assertNotEqual(root_article.current_revision.id, root_article_revision_id)

