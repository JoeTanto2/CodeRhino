import json, redis
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .models import CustomUser, Servers, JoinServerRequests, InvitationsToServer, BlogManager, Blog, Comments, CommentsManager
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import (SignUpSerializer, GoogleSerializer, ServerCreationSerializer,
ServerRequestSerializer, InvitationSerializer, BlogSerializer, CommentsSerializer)
from rest_framework.permissions import IsAuthenticated

redis_client = redis.Redis(host="localhost", port=6379, db=0)

@api_view(['POST'])
def signup (request):
    info = request.data
    serializer = SignUpSerializer(data=info)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        response = Response()
        print(serializer.data)
        user = CustomUser.objects.get(id=serializer.data['id'])
        token = RefreshToken.for_user(user)
        response.set_cookie(key="access_token", value=str(token.access_token), httponly=True)
        response.data = serializer.data
        return response
    raise serializer.errors

"""
returns {"id": value, "username": value, "email": value, "profile_picture": value or null} + sets the access token in cookies
"""
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
        response.data = ({
                            'id': user.id,
                            'username': user.username,
                            "email": user.email,
                          })
        return response


"""returns just a message of success"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout (request):
    respone = Response(status=status.HTTP_205_RESET_CONTENT)
    respone.delete_cookie(key="access_token")
    respone.data = ({"message": "successfully logged out"})
    return respone



"""
returns {"username": value, "email": value} + sets access token in cookies
"""
@api_view(['POST'])
def googleAuth(request):
    serializer = GoogleSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = (serializer.validated_data['auth_token'])
        response = Response(status=status.HTTP_201_CREATED)
        to_return = {
            'username': data['username'],
            'email': data['email'],
        }
        response.set_cookie(key='access_token', value=data['access_token'], httponly=True)
        response.data = to_return
        return response
    return Response({"verification": "Your google account could not be verified."}, status=status.HTTP_409_CONFLICT)




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user (request):
    pk = request.query_params.get('id')
    if not pk:
        user = request.user
        serializer = SignUpSerializer(user)
        return Response(serializer.data)
    user = redis_client.hget('users', pk)
    if not user:
        user = CustomUser.objects.filter(id=pk).first()
        if not user:
            return Response("User with this ID does not exist", status=status.HTTP_404_NOT_FOUND)
        serializer = SignUpSerializer(user)
        redis_client.hset('users', pk, json.dumps(serializer.data))
        return Response(serializer.data)
    return Response(json.loads(user))


@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def update_profile(request):
    info = request.data
    user = request.user
    if user:
        serializer = SignUpSerializer(user, data=info, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            redis_client.hset('users', user.id, json.dumps(serializer.data))
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"update failed": "Update failed, please try again"}, status=status.HTTP_304_NOT_MODIFIED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_server (request):
    user = request.user
    data = request.data
    data["admin"] = user.id
    serializer = ServerCreationSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({"success": f"{serializer.data['server_name']} has been successfully crated"}, status=status.HTTP_201_CREATED)
    return Response({"error": "something went wrong"}, status=status.HTTP_409_CONFLICT)


@permission_classes([IsAuthenticated])
class ServerManipulations(viewsets.ViewSet):

    """
    returns {"admin": value, "server_name": value, "server_picture": value or null}
    """
    def get(self, request, pk):
        server = redis_client.hget('servers', pk)
        if not server:
            info = Servers.objects.filter(id=pk).first()
            if info:
                serializer = ServerCreationSerializer(info)
                redis_client.set(f'server_{pk}', json.dumps(serializer.data), ex=(120))
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
        if user.id != server.admin:
            return Response("Only admin can invite to the server", status=status.HTTP_403_FORBIDDEN)
        info = request.data
        info['server_id'] = pk
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_invitations(request):
    user = request.user
    invitations = InvitationsToServer.objects.filter(user_invited=user)
    if not invitations:
        return Response([])
    serializer = InvitationSerializer(invitations, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def my_invitations_response(request, pk):
    invitation_request = InvitationsToServer.objects.filter(id=pk).select_related().first()
    if not invitation_request:
        return Response("Invitations request has been deleted or expired", status=status.HTTP_404_NOT_FOUND)
    user = request.user
    if invitation_request.user_invited != user:
        return Response("You don't have a permission too accept/decline this invitation", status=status.HTTP_403_FORBIDDEN)
    info = request.data
    if info['response'] == True:
        invitation_request.server_name.user_id.add(user)
        invitation_request.delete()
        return Response(f"You have successfully joined {invitation_request.server_name.server_name}")
    invitation_request.delete()
    return Response(f"You have declined {invitation_request.server_name.server_name}'s invitation")

@permission_classes([IsAuthenticated])
class JoinRequests (GenericAPIView):


    def get(self, request, pk):
        user = request.user
        join_requests = JoinServerRequests.objects.filter(server_id=pk).exclude(response__gt=0).select_related()
        if user.id != join_requests[0].server_id.admin:
            return Response('Only admin of the server has access to this', status=status.HTTP_403_FORBIDDEN)
        if not join_requests:
            return Response("There is not requests to join the server as of now", status=status.HTTP_200_OK)
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

def post_finder(blogs: dict, id: int):

    for post in blogs:
        if post['id'] == id:
            return post
    return None

@api_view(['GET'])
def blog(request):
    params = dict(request.query_params)
    blogs = redis_client.get('blogs')
    if not blogs:
        blogs = BlogManager.posts(BlogManager())
        serializer_posts = BlogSerializer(blogs, many=True)
        redis_client.set('blogs', json.dumps(serializer_posts.data), ex=(60 * 20))
    blogs = json.loads(redis_client.get('blogs'))
    if not params:
        return Response(blogs)
    elif 'post_id' in params.keys() and 'latest' in params.keys():
        the_post = post_finder(blogs, int(params['post_id'][0]))
        if not the_post:
            return Response('Post with this ID does not exist', status=status.HTTP_404_NOT_FOUND)
        comments = CommentsManager.retrieve_ten_from_latest(CommentsManager(), params['latest'][0])
        serializer = CommentsSerializer(comments, many=True)
        the_post['comments'] = serializer.data
        return Response(the_post)
    else:
        the_post = post_finder(blogs, int(params['post_id'][0]))
        if not the_post:
            return Response('Post with this ID does not exist', status=status.HTTP_404_NOT_FOUND)
        return Response(the_post)




