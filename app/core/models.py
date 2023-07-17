"""model for users"""

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,PermissionsMixin,BaseUserManager)
from django.conf import settings

class UserManager(BaseUserManager):
    '''Manager for Users.'''
    def create_user(self,email,password=None,**extra_fields):
        '''create users. '''
        if not email:
            raise ValueError("User must have a valid Email address.")
        user = self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    
    def create_superuser(self,email,password):
        "Create a superuser. "
        user = self.create_user(email,password)
        user.is_staff = True
        user.is_superuser = True    
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    '''User in the System.'''
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    
class Recipe(models.Model):
    """Recipe Model"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,                   
        )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5,decimal_places=2)
    link = models.CharField(max_length=255, blank = True)
    def __str__(self):
        return self.title
    