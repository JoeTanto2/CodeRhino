from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import MaxValueValidator, MinValueValidator



providers = {'google': 'google', 'apple': 'apple', 'email': 'email', 'facebook': 'facebook', 'twitter': 'twitter'}
class CustomUser (AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    profile_pic = models.ImageField(blank=True, upload_to='pictures', default='pictures/default-pic.png')
    about = models.CharField(blank=True, null=True, max_length=150)
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
            'access_token': str(refresh.access_token)
        }


class Servers (models.Model):
    user_id = models.ManyToManyField(CustomUser)
    admin = models.IntegerField()
    server_name = models.CharField(max_length=100)
    server_picture = models.ImageField(blank=True, null=True)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.server_name

class JoinServerRequests (models.Model):
    server_id = models.ForeignKey(Servers, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=200, blank=True, null=True, default=None)
    response = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])

    def __str__(self):
        return f'requested by {self.requested_by.email} to {self.server_id.server_name}'

class InvitationsToServer(models.Model):
    server_name = models.ForeignKey(Servers, on_delete=models.CASCADE)
    user_invited = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=200, blank=True, null=True, default=None)

    def __str__(self):
        return f'from {self.server_name} to {self.user_invited}'



class TextChannels (models.Model):
    server_id = models.ForeignKey(Servers, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=100)
    users_online = models.ManyToManyField(CustomUser)

    def __str__(self):
        return f"{self.channel_name} id: {self.server_id.id}"





class BlogManager(models.Manager):
    def posts(self):
        blogs = Blog.objects.all().order_by('-date')
        return blogs


class Blog(models.Model):
    message = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message[0:10]

class CommentsManager(models.Manager):

    def last_ten(self):
        comments = Comments.objects.order_by('-time')[:10]
        return comments

    def retrieve_ten_from_latest(self, pk):
        comments = Comments.objects.filter(id__gt=pk)[:10]
        return comments



class Comments(models.Model):
    comment = models.CharField(max_length=100)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    blog_id = models.ForeignKey(Blog, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user_id)
