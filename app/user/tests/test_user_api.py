"""
Tests for the user api.
"""

from django.test import TestCase
from django.contrib.auth import  get_user_model
from django.urls import reverse 

from rest_framework.test import APIClient
from rest_framework import  status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

def create_user(**params):
    """Creates and returns a user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Tests the public features of the user API.
    """
    def setUp(self):
        self.client = APIClient()
        
    def test_create_user_success(self):
        """Test create user is successful."""
        payload = {
            "email":"example@email.com",
            "password":"testpassword123",
            "name":"Test Name",
        }
        res = self.client.post(CREATE_USER_URL,payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  
        user = get_user_model().objects.get(email = payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password",res.data)  
        
        
    def test_new_user_with_existing_email_error(self):
        """Test that an error is returned if a user already exists with that email."""
        payload = {
            "email":"example@email.com",
            "password":"testpassword123",
            "name":"Test Name",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        
    def test_password_too_short_error(self):
        """Test returns error is password is too short."""
        payload = {
            "email":"example@email.com",
            "password":"123",
            "name":"Test Name",
        }
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)
        
    
    def test_token_create_for_users(self):
        """Test generates token for valid user credentials"""
        user_details = {
            'name':"Test Name",
            'email':"test@example.com",
            'password':"test-user-password"
        }
        create_user(**user_details)
        
        
        pay_load = {
            'email': user_details["email"],
            'password': user_details["password"],
        }
        res = self.client.post(TOKEN_URL,pay_load)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn("token",res.data)
        
    def test_create_token_bad_credentials(self):
        """Test create token with bad creadentials returns an error"""
        create_user(email = "test@example.com", password = "goodpass")
        payload = {"mail" : "test@example.com", "password" :"badpass"}
        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn("token",res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_empty_password(self):
        """Test create token with empty password returns an error"""
        create_user(email = "test@example.com", password = "")
        payload = {"mail" : "test@example.com", "password" :"badpass"}
        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn("token",res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    
    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
        
class PrivateUserApiTests(TestCase):
    """Test Api requests that requires authentication."""
    def setUp(self):
        self.user = create_user(
            email = "testemail@example.com",
            password = "goodpass",
            name = "Test Name",
            )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
       
        
    def test_retrieve_profile_success(self):
        """Test retrieving profile for loggen in users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })
        
    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint"""
        res = self.client.post(ME_URL,{})
        
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        
    def test_update_user_profile(self):
        """Test updating the user profile is successful"""
        payload = {'name':'upatedname', 'password':'newpassword123'}
        
        res = self.client.patch(ME_URL, payload)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.name == payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code,status.HTTP_200_OK)