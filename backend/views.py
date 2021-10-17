from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .models import CustomUser, Servers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status, viewsets
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
        response = Response()
        user = CustomUser.objects.get(email=serializer.data['email'])
        token = RefreshToken.for_user(user)
        response.set_cookie(key="access_token", value=str(token.access_token), httponly=True)
        response.data = ({'User has been successfully registered': serializer.data})
        return response
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
    if serializer.is_valid(raise_exception=True):
        data = (serializer.validated_data['auth_token'])
        response = Response(status=status.HTTP_201_CREATED)
        to_return = {
            'username': data['username'],
            'email': data['email'],
        }
        response.set_cookie(key='access_token', value=data['access_token'], httponly=True)
        response.data = (to_return)
        return response
    return Response({"error": "verification went wrong"}, status=status.HTTP_409_CONFLICT)

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

class ServerManipulations(viewsets.ViewSet):

    def get(self, request, pk):
        info = Servers.objects.filter(id=pk).first()
        if info:
            serializer = ServerCreationSerializer(info)
            return Response(serializer.data)
        return Response({"error": "server with this name was not found"}, status=status.HTTP_404_NOT_FOUND)

    def server_patch(self, request, pk):
        user = request.user
        server = Servers.objects.filter(id=pk).first()
        if server:
            if server.admin != user.id:
                return Response({"error": "Only admin can make changes to the server"}, status=status.HTTP_403_FORBIDDEN)
            info = request.data
            serializer = ServerCreationSerializer(server, data=info, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"success": "Server's info has been successfully updated"}, status=status.HTTP_202_ACCEPTED)
            return Response({'error': 'something went wrong'}, status=status.HTTP_304_NOT_MODIFIED)
        return Response({"error": "server is not found!"}, status=status.HTTP_404_NOT_FOUND)

    def server_delete(self, request, pk):
        user = request.user
        server = Servers.objects.filter(id=pk).first()
        if server:
            if server.admin != user.id:
                return Response({"error": "Only admin can delete the server"}, status=status.HTTP_403_FORBIDDEN)
            server.delete()
            return Response({"success": "The server has been succesfully deleted"}, status=status.HTTP_200_OK)
        return Response({"error": "server is not found!"}, status=status.HTTP_404_NOT_FOUND)
