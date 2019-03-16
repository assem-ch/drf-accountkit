# drf-accountkit
This package enables the use of Facebook Accountkit for Django Rest Framework

If you want to know more about Facebook Accountkit, check out the following resources
- https://auth0.com/blog/facebook-account-kit-passwordless-authentication/
- https://developers.facebook.com/docs/accountkit


## Installation & Configuration

	pip install drf-accountkit

Then to add the Django Accountkit to your project add the app `drf_accountkit` to your `INSTALLED_APPS`

And add `drf_accountkit` URLconf to your `url.py` like this:

    path('[YOUR_PREFIX]/', include('drf_accountkit.urls')),


Now add the following settings in your settings.py file


	FACEBOOK_APP_ID = <Accountkit App ID>
	ACCOUNT_KIT_APP_SECRET = <Accountkit App Secret>
	ACCOUNT_KIT_VERSION = "v1.0"

## Usage

You have to configure account kit in your frontend and specify `[YOUR_PREFIX]/login_success` as the success url.

You either send to login success as POST (or GET) those info:
- `access_token`

or

- `code`, `state`, `status`

You will get as result:
- **Successful:** API status 200 or 201
    - `token`
    - `user_id`
- **Refusal:** API status 401
    - `message`


## Costumization
You can overide methods of  `LoginSuccess` API view like:
 - `get_username(phone, email)` to costumize the username to be stored
 - `response(user, token)` to costumize the response of endpoint


### This is project is based on

- The django implementation of accountkit at https://github.com/antiproblemist/django-accountkit
