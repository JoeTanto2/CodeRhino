from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .models import CustomUser, Servers, JoinServerRequests
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .serializers import SignUpSerializer, GoogleSerializer, ServerCreationSerializer, ServerRequestSerializer, InvitationSerializer
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
        response.data = (serializer.data)
        return response
    raise serializer.errors

class LogIn (APIView):
    def post(self, request):
        info = request.data
        user = CustomUser.objects.filter(email=info['email']).first()
        if not user:
            raise AuthenticationFailed("A user with this email does not exist")
        if not user.check_password(info['password']):
            raise AuthenticationFailed("wrong password")
        response = Response()
        token = RefreshToken.for_user(user)
        response.set_cookie(key="access_token", value=str(token.access_token), httponly=True)
        response.data = ({'username': user.username,
                          'email': user.email
                          })
        return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout (request):
    respone = Response(status=status.HTTP_205_RESET_CONTENT)
    respone.delete_cookie(key="access_token")
    respone.data = ({"message": "successfully logged out"})
    return respone

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
    return Response({"verification": "Your google account could not be verified."}, status=status.HTTP_409_CONFLICT)

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
        server =redis_client.get(f'server_{pk}')
        if not server:
            info = Servers.objects.filter(id=pk).first()
            if info:
                serializer = ServerCreationSerializer(info)
                redis_client.set(f'server_{pk}', json.dumps(serializer.data), ex=10)
                return Response(serializer.data)
            return Response({"error": "server with this name was not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(json.loads(server))


    def server_patch(self, request, pk):
        user = request.user
        server = Servers.objects.filter(id=pk).first()
        if server:
            if server.admin != user.id:
                return Response({"Permission error": "Only admin can make changes to the server."}, status=status.HTTP_403_FORBIDDEN)
            info = request.data
            serializer = ServerCreationSerializer(server, data=info, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response("Server's info has been successfully updated", status=status.HTTP_202_ACCEPTED)
            return Response({'error': 'something went wrong'}, status=status.HTTP_304_NOT_MODIFIED)
        return Response({"server not found": "server is not found!"}, status=status.HTTP_404_NOT_FOUND)


    def invite_to_server(self, request, pk):
        server = Servers.objects.filter(id=pk).first()
        if not server:
            return Response({"Server not found": "Server with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        info = request.data
        serializer = InvitationSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"Invitation alreadi exists": "Invitation for this user already exists"}, status=status.HTTP_409_CONFLICT)

    def server_delete(self, request, pk):
        user = request.user
        server = Servers.objects.filter(id=pk).first()
        if server:
            if server.admin != user.id:
                return Response({"Permission error": "Only admin can delete the server"}, status=status.HTTP_403_FORBIDDEN)
            server.delete()
            return Response("The server has been successfully deleted", status=status.HTTP_200_OK)
        return Response({"server not found": "server is not found!"}, status=status.HTTP_404_NOT_FOUND)

class JoinRequests (GenericAPIView):


    def get(self, request, pk):
        user = request.user
        join_requests = JoinServerRequests.objects.filter(server_id=pk).exclude(response__gt=0).select_related()
        if not join_requests:
            return Response("There is not requests to join the server as of now", status=status.HTTP_200_OK)
        if user.id != join_requests[0].server_id.admin:
            return Response('Only admin of the server has access to this', status=status.HTTP_403_FORBIDDEN)
        serializer = ServerRequestSerializer(join_requests, many=True)
        return Response(serializer.data)



    def post(self, request, pk):
        user = request.user
        server = Servers.objects.filter(id=pk).first()
        if server:
            if server.admin != user.id:
                return Response({"Permission error": "Only admin has access to this page."},
                                status=status.HTTP_403_FORBIDDEN)
            info = request.data
            join_request = JoinServerRequests.objects.filter(id=info['request_id']).select_related()
            if not join_request:
                return Response("request does not exist", status=status.HTTP_404_NOT_FOUND)

            """
            2 is True while 1 is False
            """

            if info['response'] == 2:
                join_request.update(response=2)
                server.user_id.add(join_request[0].requested_by)
            else:
                join_request.update(response=1)
            return (Response(f"you have accepted {join_request[0].requested_by.username}'s join request",
                             status=status.HTTP_202_ACCEPTED)
                    if info['response'] == 2 else Response(
                f"you have rejected {join_request[0].requested_by.username}'s join request"))

        return Response({"server does not exist": "The server with this id does not exist"},
                        status=status.HTTP_404_NOT_FOUND)

