from django.urls import path
from .views import (signup, LogIn, googleAuth, create_server,
                    ServerManipulations, logout, JoinRequests, user, update_profile, my_invitations, my_invitations_response)

urlpatterns = [
    path('signup/', signup),
    path('login/', LogIn.as_view()),
    path('logout/', logout),
    path('user/<str:pk>/', user),
    path('update_profile/', update_profile),
    path('google/', googleAuth),
    path('create_server/', create_server),
    path('server/<str:pk>/', ServerManipulations.as_view({
        'get': 'get',
        'patch': 'server_patch',
        'delete': 'server_delete',
        'post': 'invite_to_server'
    })),
    path('requests/<str:pk>/', JoinRequests.as_view()),
    path('my_invitations/', my_invitations),
    path('my_invitations_response/<str:pk>/', my_invitations_response)
]