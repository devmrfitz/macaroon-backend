import os

from google.auth.transport import requests
from google.oauth2 import id_token

from macaroonBackend.settings import GAUTH_CLIENT_ID


def verify_token(token: str) -> tuple:
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GAUTH_CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        # If auth request is from a G Suite domain:

        # Get the user's Google Account ID from the decoded token.
        return idinfo['email'], idinfo['picture']
    except ValueError:
        # Invalid token
        return "", None
