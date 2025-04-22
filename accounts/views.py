from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, get_user_model
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response 
from rest_framework import status

from .serializers import UserSerializer
from .models import PhoneOTP
from .permissions import VerifyPhoneRateLimit

User = get_user_model()

@api_view(['POST'])
@permission_classes([VerifyPhoneRateLimit])
def verify_phone(request):
    """
    This view is for verification of phone number and will check to see whether a user with specific phone number
    exists in database or not, we will inform frontend developer about existence of user.
    """
    phone = request.data.get('phone')

    if not phone:
        return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user, created = User.objects.get_or_create(phone=phone)

    otp_code = PhoneOTP.generate_otp()

    if created:
        otp_obj = PhoneOTP.objects.create(
            user=user,
            otp_code=otp_code
        )
    
    else:
        otp_obj = user.otp
        otp_obj.otp_code = otp_code
        otp_obj.used = False
        otp_obj.created_at = timezone.now()
        otp_obj.save()
    
    otp_obj.send_sms(message='')

    # We must inform frontend developer from 
    return Response(
        {
            'message':f'OTP code send to {phone}!',
            'user_was_exist': 'false' if created else 'true',
            'otp_code': otp_code
        },
        status=status.HTTP_200_OK
    )



@api_view(['POST'])
@permission_classes([VerifyPhoneRateLimit])
def verify_otp(request):
    """
    This is the second step(probably) and we will check the OTP code which sent to the user in previous step.
    """

    phone = request.data.get('phone')
    otp = request.data.get('otp')

    
    if not phone or not otp:
        return Response({'error': 'Phone number and OTP code required!'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(phone=phone)
    
        if int(user.otp.otp_code) != int(otp):
            return Response({'error': 'Invalid OTP code!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.otp.is_expired():
            return Response({"message": "This OTP code has expired!"}, status=status.HTTP_401_UNAUTHORIZED)

        # We will not allow user to use one OTP code twice.
        print(user.otp.used)
        if user.otp.used:
            return Response({'error': 'This OTP code is used already, please get another otp code'}, status=status.HTTP_403_FORBIDDEN)
        

        user.phone_verified = True
        user.save()

        # Settings the the current otp as used
        otp_obj = user.otp
        otp_obj.used = True
        otp_obj.save()


        return Response({'message': 'Verified Successfully'}, status=status.HTTP_200_OK)
    
    except ValueError:
        return Response({'error': 'Invalid OTP code.OTP code can not include letters!'}, status=status.HTTP_400_BAD_REQUEST)   
     
    except User.DoesNotExist:
        return Response({'error': f'The user with `{phone}` does not exist!'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def get_credentials(request):
    """
    After OTP verified, the frontend developer will get other credentials from user(first name, last name, ..) and 
    send it to this view. This view will update the  existing user's credentials and will send it back to the 
    """
    phone = request.data.get("phone")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    email = request.data.get("email")

    if not phone or not first_name or not last_name or not email:
        return Response({'error': 'Phone number, Email, first name and last name are required!'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(phone=phone)
        if not user.phone_verified:
            return Response({'error': 'Your phone number need to be verified first!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        serializer = UserSerializer(user)
        
        return Response({'message': 'User credentials stored successfully!', 'credentials': serializer.data}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({'error': f'The user with `{phone}` phone number not found!'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([VerifyPhoneRateLimit])
def verify_password(request):
    phone = request.data.get('phone')
    password = request.data.get('password')

    if not phone or not password:
        return Response({'error': 'Phone number and password are required!'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(phone=phone, password=password)
    if not user:
        return Response({'error': 'Invalid credentials!Make sure about correctness of Phone number and password!'}, status=status.HTTP_401_UNAUTHORIZED)

    login(request, user)

    return Response({'message': 'Welcome To our site!'}, status=status.HTTP_200_OK)

