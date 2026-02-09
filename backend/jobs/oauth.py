from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

def verify_google_token(token):
    """
    Verifies a Google ID token.
    Returns the user's information if valid, otherwise None.
    """
    try:

        client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com')

        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

        return idinfo
    except ValueError:

        return None