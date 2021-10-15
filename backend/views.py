import http
import json
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .models import CustomUser
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .serializers import SignUpSerializer, GoogleSerializer, ServerCreationSerializer
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
def signup (request):
    info = request.data
    serializer = SignUpSerializer(data=info)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({'User has been successfully registered': serializer.data})
    else:
        raise serializer.errors

class LogIn (APIView):
    def post (self, request):
        info = request.data
        user = CustomUser.objects.filter(email=info['email']).first()
        if not user:
            raise AuthenticationFailed("A user with this email does not exist")
        if not user.check_password(info['password']):
            raise AuthenticationFailed("wrong password")
        response = Response()
        token = RefreshToken.for_user(user)
        response.set_cookie(key="access_token", value=str(token.access_token), httponly=True)
        response.data = ({"message": "you have successfully logged in"})
        return response

@api_view(['POST'])
def googleAuth (request):
    serializer = GoogleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = ((serializer.validated_data)['auth_token'])
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users (request):
    user = request.user
    serializer = SignUpSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_channel (request):
    user = request.user
    data = request.data
    data["admin"] = user.id
    serializer = ServerCreationSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({"success": f"{serializer.data['server_name']} has been successfully crated"}, status=status.HTTP_201_CREATED)
    return Response({"error": "something went wrong"}, status=status.HTTP_409_CONFLICT)


