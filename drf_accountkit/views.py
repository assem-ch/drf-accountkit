# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature
from django.contrib.auth import get_user_model

from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

api_version = getattr(settings, 'ACCOUNT_KIT_VERSION')
accountkit_secret = getattr(settings, 'ACCOUNT_KIT_APP_SECRET')
facebook_app_id = getattr(settings, 'FACEBOOK_APP_ID')


class LoginSuccess(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get_username(self, phone=None, email=None):
        return phone or email

    def get_or_create_user(self, username):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username)
            user.set_unusable_password()
            user.save()
        user = user if user.is_active else None
        return user

    def authenticate_user(self, request):

        if request.user.is_authenticated:
            return request.user, 'already connected'

        user_access_token = request.GET.get('access_token') if request.GET.get('access_token',
                                                                               None) else request.data.get(
            'access_token', None)

        if not user_access_token:
            code = request.GET.get('code') if request.GET.get('code', None) else request.POST.get('code', None)
            state = request.GET.get('state') if request.GET.get('state', None) else request.POST.get('state', None)
            status = request.GET.get('status') if request.GET.get('status', None) else request.POST.get('status', None)

            if status != "PARTIALLY_AUTHENTICATED":
                return None, 'Accountkit could not authenticate the user'

            try:
                signer = TimestampSigner()
                csrf = signer.unsign(state)
            except BadSignature:
                return None, 'Invalid request'

            # Exchange authorization code for access token
            token_url = 'https://graph.accountkit.com/%s/access_token' % api_version
            params = {'grant_type': 'authorization_code', 'code': code,
                      'access_token': 'AA|%s|%s' % (facebook_app_id, accountkit_secret)
                      }

            res = requests.get(token_url, params=params)
            token_response = res.json()

            if 'error' in token_response:
                return None, 'This authorization code has been used'

            user_id = token_response.get('id')
            user_access_token = token_response.get('access_token')
            refresh_interval = token_response.get('token_refresh_interval_sec')

        # Get Account Kit information
        identity_url = 'https://graph.accountkit.com/%s/me' % api_version
        identity_params = {'access_token': user_access_token}

        res = requests.get(identity_url, params=identity_params)
        identity_response = res.json()

        if 'error' in identity_response:
            return None, 'Identity error'
        elif identity_response['application']['id'] != facebook_app_id:
            return None, 'The application id returned does not match the one in your settings'

        user = None
        username = None
        if 'email' in identity_response:
            email = identity_response['email']['address']
            username = self.get_username(email=email)
        elif 'phone' in identity_response:
            phone = identity_response['phone']['number']
            username = self.get_username(phone=phone)

        if username:
            user = self.get_or_create_user(username)

        if not user:
            return None, 'user may not active'

        return user, 'success login'

    def response(self, user, token):
        return {
            'token': token.key,
            'user_id': user.id,
        }

    def main(self, request):
        user, message = self.authenticate_user(request)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response(self.response(user, token),
                            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

        else:
            return Response({'error': 'message'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, format=None):
        return self.main(request)

    def get(self, request, format=None):
        return self.main(request)
