"""Configuration settings for running the Python auth samples locally.

In a production deployment, this information should be saved in a database or
other secure storage mechanism.
"""

CLIENT_ID = 'ffd4bb1e-878d-450d-ad66-38cc88dab76f'
CLIENT_SECRET = 'gcunXCX27@^@cqvXVFJ927_'
REDIRECT_URI = 'https://18.221.72.213:8000/login/authorized'

# AUTHORITY_URL ending determines type of account that can be authenticated:
# /organizations = organizational accounts only
# /consumers = MSAs only (Microsoft Accounts - Live.com, Hotmail.com, etc.)
# /common = allow both types of accounts
AUTHORITY_URL = 'https://login.microsoftonline.com/common'

AUTH_ENDPOINT = '/oauth2/v2.0/authorize'
TOKEN_ENDPOINT = '/oauth2/v2.0/token'

RESOURCE = 'https://graph.microsoft.com/'
API_VERSION = 'v1.0'
SCOPES = ['User.Read', 'Mail.Send', 'Files.ReadWrite'] # Add other scopes/permissions as needed.

# This code can be removed after configuring CLIENT_ID and CLIENT_SECRET above.
if 'ENTER_YOUR' in CLIENT_ID or 'ENTER_YOUR' in CLIENT_SECRET:
    print('ERROR: config.py does not contain valid CLIENT_ID and CLIENT_SECRET')
    import sys
    sys.exit(1)
