from .views import LoginSuccess

try:
    from django.urls import path

    urlpatterns = [
        path('login_success', LoginSuccess.as_view(), name="login_success"),
    ]
except:
    from django.conf.urls import  url

    urlpatterns = [
        url(r'^login_success', LoginSuccess.as_view(), name="login_success"),
    ]