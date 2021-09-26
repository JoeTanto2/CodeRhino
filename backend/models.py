from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from rest_framework_simplejwt.tokens import RefreshToken

# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password, **extra_fields):
#         if not email:
#             raise ValueError('The Email must be set')
#         if not password:
#             raise ValueError('Password must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, email, password, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#         return self.create_user(email, password, **extra_fields)
providers = {'google': 'google', 'apple': 'apple', 'email': 'email', 'facebook': 'facebook', 'twitter': 'twitter'}
class CustomUser (AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    profile_pic = models.ImageField(blank=True, null=True)
    is_staff = models.BooleanField(default=False, blank=True)
    is_active = models.BooleanField(default=True, blank=True)
    is_email_verified = models.BooleanField(default=False, blank=True)
    is_visible = models.BooleanField(default=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    authentication_type = models.CharField(max_length=50, default=providers['email'])

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def token_generator(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
