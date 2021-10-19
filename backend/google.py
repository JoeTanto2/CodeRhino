from google.auth.transport import requests
from google.oauth2 import id_token
from decouple import config
from google.oauth2.id_token import verify_token, _GOOGLE_OAUTH2_CERTS_URL, _GOOGLE_ISSUERS

from rest_framework import exceptions


class Google:
    """Google class to fetch the user info and return it"""

    @staticmethod
    def validate(auth_token):
        """
        validate method Queries the Google oAUTH2 api to fetch the user info
        """
        # request = requests.Request()
        #
        # id_info = id_token.verify_oauth2_token(
        #     auth_token, request)
        # # userid = id_info['sub']
        # return id_info
        try:
            idinfo = id_token.verify_oauth2_token(
                auth_token, requests.Request())
            if 'accounts.google.com' in idinfo['iss']:
                return idinfo
        except:
            return "ivalid or expired"