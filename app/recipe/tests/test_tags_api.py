"""
Tests for the tags API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag , Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """create and return a tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)

class PublicTagsAPITests(TestCase):
    """test unauthenticated Api request"""
    def setUp(self):
        self.client = APIClient()
    def test_auth_required(self):
        """test auth is required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    class PrivateTagsAPITests(TestCase):
        """Test authenticated Api request"""
        def setUp(self):
            self.user = create_user()
            self.client = APIClient()
            self.client.force_authenticate(user=self.user)
        def test_retrieve_tags(self):
            """test retrieving a list of tags """
            Tag.objects.create(user=self.user, name='Vegan')
            Tag.objects.create(user=self.user, name='Dessert')
            res = self.client.get(TAGS_URL)
            tags = Tag.objects.all().order_by('-name')
            serializer = TagSerializer(tags, many=True)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res.data, serializer.data)

        def test_tags_limited_to_user(self):
            """test list of tags is limited to authenticated user"""
            user2 = create_user(email='user2@example.com')
            Tag.objects.create(user=user2, name='fruity')
            tag = Tag.objects.create(user=self.user, name='comfort food')
            res = self.client.get(TAGS_URL)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(len(res.data), 1)
            self.assertEqual(res.data[0]['name'], tag.name)
            self.assertEqual(res.data[0]['id'], tag.id)


        def test_update_tag(self):
            """test updating a tag"""
            tag = Tag.objects.create(user=self.user, name='After Dinner')
            payload = {'name': 'Dessert'}
            url = detail_url(tag.id)
            res = self.client.patch(url, payload)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            tag.refresh_from_db()
            self.assertEqual(tag.name, payload['name'])


        def test_delete_tag(self):
            """test deleting a tag"""
            tag = Tag.objects.create(user=self.user, name='lunch ')
            res = self.client.delete(detail_url(tag.id))
            self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
            tags = Tag.objects.filter(user=self.user)
            self.assertFalse(tags.filter.exists())




        def test_filter_tags_assigned_to_recipes(self):
            """
            Test filtering tags by those assigned to recipes
            """
            tag1=Tag.objects.create(user=self.user, name='fruity')
            tag2=Tag.objects.create(user=self.user, name='comfort food')
            recipe = Recipe.objects.create(
                title = 'green eggs on toast',
                time_minutes = 10,
                price = Decimal('5.25'),
                user=self.user

            )
            recipe.tags.add(tag1)
            res = self.client.get(TAGS_URL, {'assigned_only': 1})
            s1=TagSerializer(tag1)
            s2=TagSerializer(tag2)
            self.assertIn(res.data, s1.data)
            self.assertNotIn(res.data, s2.data)

        def test_filtered_tags_uniqe(self):
            """test filterd tags returns a uniqe list"""
            tag1=Tag.objects.create(user=self.user, name='fruity')
            tag2=Tag.objects.create(user=self.user, name='comfort food')
            recipe1 = Recipe.objects.create(
                title = 'green eggs on toast',
                time_minutes = 10,
                price = Decimal('5.25'),
                user=self.user


            )

            recipe2 = Recipe.objects.create(
                title = 'lobia polo',
                time_minutes = 12,
                price = Decimal('5.35'),
                user=self.user


            )
            recipe1.tags.add(tag1)
            recipe2.tags.add(tag2)
            res = self.client.get(TAGS_URL, {'assigned_only': 1})
            self.assertEqual(len(res.data), 1)