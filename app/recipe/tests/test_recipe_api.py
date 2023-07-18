"""
Tests for Recipe Api
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer



#user = get_user_model()
RECIPES_URL = reverse("recipe:recipe-list")

def detail_url(recipe_id):
    """returns a unique url for a recipe"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_recipe(user, **params):
    """Creates and returns a sample recipe"""
    defaults = {
        'title': "Sample Recipe Title",
        "time_minutes": 22,
        'price': Decimal("5.25"),
        'description': "Sample Description",
        'link': "http://example.com/recipe.pdf"
    }
    
    defaults.update(params)
    recipe = Recipe.objects.create(user=user,**defaults)
    return recipe


def create_user(**params):
    """Helper function that creates user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Tests Unauthentic API requests"""
    
    def setUp(self):
        """set up the API client"""
        self.client = APIClient()
    
    def test_auth_required(self):
        """Test Auth is required to call recipe API"""
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateRecipeAPITests(TestCase):
    """Test Authenticated Recipe API requests"""
    
    def setUp(self):
        """Setup and authenticate client for recipe tests"""
        self.client = APIClient()
        self.user = create_user(email = "user@example.com",password="testpass123")
        self.client.force_authenticate(user=self.user)
        
    
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user = self.user)
        
        res = self.client.get(RECIPES_URL)
        
        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipe_list_limited_to_user(self):
        """Test list of api is limited to authenticated user"""
        other_user = create_user(
            email='other@example.com',
            password='password123'
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)
        
        recipe=Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipe_detail(self):
        """Test get recipe detail."""
        recipe=create_recipe(user=self.user)
        
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer =RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': "Sample recipe",
            'time_minutes':30,
            'price': Decimal("5.99"),
        }
        res = self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user,self.user)
        
        
    def test_partial_update(self):
        """Test partial update of a recipe"""
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(user=self.user,
                               title = "Sample Recipe Title",
                               link = original_link
                               )
        
        payload = {"title":"New recipe title",}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user,self.user)
        self.assertEqual(recipe.title,payload["title"])
        self.assertEqual(recipe.link,original_link)        
        
    
    def test_full_update(self):
        """Test Full update on recipe API."""
        recipe = create_recipe(
            user=self.user,
            title = 'Sample recipe Title',
            link = 'https://example.com/recipe.pdf',
            description = 'Sample recipe description',
            )
        
        payload = {"title":"New rexipe Title",
                   'link':'https://example.com/new_recipe',
                   'description':'New recipe description',
                   'time_minutes':10,
                   'price':Decimal("2.50"),
                   }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k,v in payload.items():
            self.assertEqual(getattr(recipe,k),v)
        self.assertEqual(recipe.user,self.user)