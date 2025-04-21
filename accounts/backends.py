from django.contrib.auth.backends import ModelBackend
from .models import CustomUser


# Custom authentication backend for phone number
class PhoneBackend(ModelBackend):   
    def authenticate(self, request, phone=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return None
        
        if user.check_password(password):        
            return user
        
        return None 