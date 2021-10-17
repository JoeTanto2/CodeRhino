from django.contrib import admin
from django.urls import path, include
from .views import signup, LogIn, users, googleAuth, create_channel, ServerManipulations

urlpatterns = [
    path('signup/', signup),
    path('login/', LogIn.as_view()),
    path('users/', users),
    path('google/', googleAuth),
    path('create_channel/', create_channel),
    path('server/<str:pk>/', ServerManipulations.as_view({
        'get': 'get',
        'patch': 'server_patch',
        'delete': 'server_delete',
    })),
]