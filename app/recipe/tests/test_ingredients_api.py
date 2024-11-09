from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Ingredient , Recipe)
from recipe.serializers import IngredientSerializer

from decimal import Decimal
INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """create and return a tag detail url"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='test@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientAPITests(TestCase):
    """Test unauthenticated user API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test authenticated user API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test authenticated user can retrieve ingredients list"""
        Ingredient.objects.create(user=self.user, name='milk')
        Ingredient.objects.create(user=self.user, name='eggs')
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-id')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test authenticated user can retrieve ingredients list for authenticated user"""
        user2 = create_user(email='other@example.com')
        Ingredient.objects.create(user=user2, name='milk')
        ingredient = Ingredient.objects.create(user=self.user, name='eggs')
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """test updating ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='milk')
        payload = {'name': 'butter'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='milk')
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        ingredient_exists = Ingredient.objects.filter(user=self.user).exists()
        self.assertFalse(ingredient_exists)

    def test_filter_ingredients_assigned_to_recipes(self):
        """test listing ingredients to those assigned to recipes"""
        in1 = Ingredient.objects.create(user=self.user, name='milk')
        in2 = Ingredient.objects.create(user=self.user, name='eggs')
        recipe = Recipe.objects.create(
            title='milky rice',
            time_minutes=10,
            price=Decimal('4.50'),
            user=self.user


        )
        recipe.ingredients.add(in1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1 })
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)


    def test_ingredients_unique(self):
        """test filtering ingredients return a unique list """
        ing = Ingredient.objects.create(user=self.user, name='eggs')
        Ingredient.objects.create(user=self.user, name='milk')
        recipe1= Recipe.objects.create(
            title='milky rice',
            time_minutes=10,
            price=Decimal('4.50'),
            user=self.user

        )
        recipe2= Recipe.objects.create(
            title='abgosht',
            time_minutes=12,
            price=Decimal('4.50'),
            user=self.user

        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)




