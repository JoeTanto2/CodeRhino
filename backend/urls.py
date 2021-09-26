from django.contrib import admin
from django.urls import path, include
from .views import signup, LogIn, users, googleAuth

urlpatterns = [
    path('signup/', signup),
    path('login/', LogIn.as_view()),
    path('users/', users),
    path('google/', googleAuth),
]