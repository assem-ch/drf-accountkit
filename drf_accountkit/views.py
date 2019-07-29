# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_accountkit.accountkit import AccountKit


class LoginSuccess(AccountKit, APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    facebook_app_id = getattr(settings, 'FACEBOOK_APP_ID', default=None)
    accountkit_secret = getattr(settings, 'ACCOUNT_KIT_APP_SECRET', default=None)
    api_version = getattr(settings, 'ACCOUNT_KIT_VERSION', default='v1.1')
    accountkit_secret = getattr(settings, 'ACCOUNT_KIT_APP_SECRET')
    facebook_app_id = getattr(settings, 'FACEBOOK_APP_ID')
    api_version = getattr(settings, 'ACCOUNT_KIT_VERSION')

    def get_username(self, phone=None, email=None):
        return email or 'user{}'.format(phone)

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

        user_access_token = request.GET.get('access_token', None)

        try:
            if not user_access_token:
                code = request.POST.get('code', None)
                state = request.POST.get('state', None)
                status = request.POST.get('status', None)
                user_access_token = self.get_access_token(code, state, status)

            identity_response = self.identify(user_access_token)
        except Exception as e:
            return None, str(e)

        user = None
        email=phone=None
        if 'email' in identity_response:
            email = identity_response['email']['address']
        elif 'phone' in identity_response:
            phone = identity_response['phone']['number']

        username = self.get_username(phone=phone, email=email)

        if username:
            user = self.get_or_create_user(username)

        if not user:
            return None, 'User may not active'

        return user, 'Success login'

    def response(self, user, token):
        return {
            'token': token.key,
            'user_id': user.id,
        }

    def main(self, request):
        if not self.facebook_app_id or not self.accountkit_secret:
            raise Exception("Be sure you defined FACEBOOK_APP_ID and ACCOUNT_KIT_APP_SECRET in your settings file!")

        user, message = self.authenticate_user(request)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response(self.response(user, token),
                            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

        else:
            return Response({'error': message}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, format=None):
        return self.main(request)

    def get(self, request, format=None):
        return self.main(request)
