from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create a superuser and a regular user for testing."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='mreza@0708',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='mreza@0708',
            name='Test User',  # Ensure consistent capitalization
        )

    def test_users_list(self):
        """Test that users are listed on the admin page."""
        url = reverse('admin:core_user_changelist')  # Ensure this matches your admin registration
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """test the edit user page"""
        url = reverse('admin:core_user_change', args=(self.user.id,))
        res = self.client.get(url)
        self.assertEquals(res.status_code, 200)

    def test_create_user_page(self):
        """test the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEquals(res.status_code, 200)
