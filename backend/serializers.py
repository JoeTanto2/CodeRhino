from rest_framework import serializers
from .models import CustomUser, Servers, JoinServerRequests, InvitationsToServer
import re
from . import google
from decouple import config
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from .managers import CustomUserManager
from .register import social_user_registration


class SignUpSerializer (serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    profile_pic = serializers.ImageField(required=False)
    id = serializers.IntegerField(required=False)
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'profile_pic']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create (self, validated_data):
        re_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email = validated_data['email']
        if email:
            if CustomUser.objects.filter(email=email).exists():
                raise serializers.ValidationError({'email': 'An account with this email already exists'})
            if(re.fullmatch(re_email, email)):
                instance = self.Meta.model(**validated_data)
                instance.set_password(validated_data['password'])
                instance.save()
                return instance
            else:
                message = {'email': 'The email is not valid! Please enter a valid email.'}
                raise serializers.ValidationError(message)





class GoogleSerializer (serializers.Serializer):
    auth_token = serializers.CharField()
    def validate_auth_token (self, auth_token):
        user_data = google.Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )
        if user_data['aud'] != config('GOOGLE_CLIENT_ID'):
            raise AuthenticationFailed ('How?')

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        provider = 'google'
        return social_user_registration(user_id, provider, name, email)

class ServerCreationSerializer (serializers.ModelSerializer):
    server_picture = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Servers
        fields = ['admin', 'server_name', 'server_picture']

    def create(self, validated_data):
        server_name = validated_data['server_name'].lower()
        name_check = Servers.objects.filter(server_name=server_name).first()
        if name_check:
            raise ValidationError(
                'Channel with this name already exists!'
            )
        validated_data['server_name'] = server_name
        instance = self.Meta.model(**validated_data)
        instance.save()
        instance.user_id.add(instance.admin)
        return instance

class ServerRequestSerializer(serializers.ModelSerializer):
    message = serializers.CharField(required=False)
    class Meta:
        model = JoinServerRequests
        fields = ['server_id', 'requested_by', 'message']

class InvitationSerializer(serializers.ModelSerializer):
    message = serializers.CharField(required=False)
    class Meta:
        model = InvitationsToServer
        fields = '__all__'

    def create(self, validated_data):
        invitation_check = InvitationsToServer.objects.filter(server_id=validated_data['server_id'], user_invited=validated_data['user_invited'])
        if not invitation_check:
            instance = self.Meta.model(**validated_data)
            instance.save()
            return instance
        return "Invitation for this user already exists."
