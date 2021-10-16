from django.contrib.auth import authenticate
from .models import CustomUser
from decouple import config
import random
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
def generate_username(name):

    username = "".join(name.split(' ')).lower()
    if not CustomUser.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)

def social_user_registration (user_id, provider, name, email):
    if_exists = CustomUser.objects.filter(email=email)
    if if_exists.exists():
        if provider == if_exists[0].authentication_type:
            user = authenticate(email=email, password=config('SOCIAL_SECRET'))
            return {
                'username': user.username,
                'email': user.email,
                'access_token': user.token_generator()['access_token']
            }
        else:
            raise AuthenticationFailed(detail=f"You have already registered an account, please login with your {if_exists[0].authentication_type} account!")
    else:
        user = {'username': generate_username(name),
                'email': email,
                'password': config('SOCIAL_SECRET'),
                'authentication_type': provider
                }
        user = CustomUser.objects.create_user(**user)
        user.is_email_verified = True
        user.save()
        new_user = authenticate(email=email, password=config('SOCIAL_SECRET'))
        to_return = {
            'email': new_user.email,
            'username': new_user.username,
            'provider': new_user.authentication_type,
            "access_token": new_user.token_generator()['access_token']
        }
        return to_return


