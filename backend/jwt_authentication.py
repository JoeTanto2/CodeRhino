from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWT (JWTAuthentication):

    def authenticate(self, request):
        print()
        token = request.COOKIES.get("access_token")
        if not token:
            return None
        validated_token = self.get_validated_token(token)
        return self.get_user(validated_token), validated_token