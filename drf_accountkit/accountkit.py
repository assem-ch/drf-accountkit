import requests
from django.core.signing import TimestampSigner, BadSignature


class AccountKit:
    accountkit_secret = None
    facebook_app_id = None
    api_version = "v1.1"

    def get_access_token(self, code, state, status):
        if status != "PARTIALLY_AUTHENTICATED":
            raise Exception('Accountkit could not authenticate the user')
        try:
            signer = TimestampSigner()
            csrf = signer.unsign(state)
        except BadSignature:
            raise Exception('Invalid request')

        # Exchange authorization code for access token
        token_url = 'https://graph.accountkit.com/%s/access_token' % self.api_version
        params = {'grant_type': 'authorization_code', 'code': code,
                  'access_token': 'AA|%s|%s' % (self.facebook_app_id, self.accountkit_secret)
                  }

        res = requests.get(token_url, params=params)
        token_response = res.json()

        if 'error' in token_response:
            raise Exception('This authorization code has been used')

        return token_response.get('access_token')

    def identify(self, access_token):
        identity_url = 'https://graph.accountkit.com/%s/me' % self.api_version
        identity_params = {'access_token': access_token}

        res = requests.get(identity_url, params=identity_params)
        identity_response = res.json()

        if 'error' in identity_response:
            raise Exception('Identity error: {}'.format(identity_response['error']['message']))
        elif identity_response['application']['id'] != self.facebook_app_id:
            raise Exception('The application id returned does not match the one in your settings')

        return identity_response
