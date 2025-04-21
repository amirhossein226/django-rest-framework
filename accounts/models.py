from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager 
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The phone must be defined!')

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()

        return user
    
    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True!")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True!")

        return self.create_user(phone, password, **extra_fields)

# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=20, unique=True)
    phone_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=255, blank=True)   
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone
    
class PhoneOTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='otp')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_expired(self):
        from django.utils import timezone
        print(self.created_at)
        return timezone.now() > self.created_at + timezone.timedelta(minutes=4)
    
    @staticmethod
    def generate_otp():
        import random
        return str(random.randint(100000, 999999))
    
    def send_sms(self, message):
        # The actual job for this method is sending sms.
        # but here we will simply print it to console
        print(f"{message}\nYour code: {self.otp_code}")