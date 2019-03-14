# drf-accountkit
**Using Facebook accountkit with Django https://developers.facebook.com/products/account-creation**

## Overview

This package enables the use of Facebook Accountkit for Django Rest Framework

If you want to know more about Facebook Accountkit, check out the following resources
- https://auth0.com/blog/facebook-account-kit-passwordless-authentication/
- https://developers.facebook.com/docs/accountkit

## Requirements

-  Python (3.6)
-  Django (2.10)


## Installation

Installation is easy using ``pip``

In release 0.1.0 you have to additionally ```pip install requests```. This will be fixed in the next release


	pip install drf-accountkit


Then to add the Django Accountkit to your project add the app ``drf_accountkit`` to your ``INSTALLED_APPS``.

Now add the following settings in your settings.py file


	ACCOUNT_KIT_APP_ID = <Accountkit App ID>
	ACCOUNT_KIT_APP_SECRET = <Accountkit App Secret>
	ACCOUNT_KIT_VERSION = "v1.0"

## Using Accountkitlogin


The ```LoginSuccess``` API view accepts the request as parameter and returns a dictionary with

- Key 'token'
- Key 'user_id'


### This is project is based on

- The django implementation of accountkit at https://github.com/antiproblemist/django-accountkit
