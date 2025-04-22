from django.urls import path
from .views import verify_phone, verify_otp, get_credentials, verify_password


ver = '1.0'
urlpatterns = [
    path(f'api/{ver}/authenticate/', verify_phone, name='authenticate_phone'),
    path(f'api/{ver}/user_credentials/', get_credentials, name='get_credentials'),
    path(f'api/{ver}/verify_password/', verify_password, name='verify_password'),
    path(f'api/{ver}/verify_otp/', verify_otp, name='verify_otp'),
]