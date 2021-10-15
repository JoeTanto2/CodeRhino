from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from rest_framework_simplejwt.tokens import RefreshToken



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

    def __str__(self):
        return self.email

    def token_generator(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class Servers (models.Model):
    user_id = models.ManyToManyField(CustomUser)
    admin = models.IntegerField()
    server_name = models.CharField(max_length=100)
    server_picture = models.ImageField(blank=True)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.server_name



class TextChannels (models.Model):
    server_id = models.ForeignKey(Servers, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=100)
    users_online = models.ManyToManyField(CustomUser)

    def __str__(self):
        return f"{self.channel_name} id: {self.server_id.id}"
