from django.contrib import admin
from django.urls import path, include
from .views import (signup, LogIn, users, googleAuth, create_channel,
                    ServerManipulations, logout, JoinRequests)

urlpatterns = [
    path('signup/', signup),
    path('login/', LogIn.as_view()),
    path('logout/', logout),
    path('me/', users),
    path('google/', googleAuth),
    path('create_channel/', create_channel),
    path('server/<str:pk>/', ServerManipulations.as_view({
        'get': 'get',
        'patch': 'server_patch',
        'delete': 'server_delete',
    })),
    path('requests/<str:pk>/', JoinRequests.as_view()),

]