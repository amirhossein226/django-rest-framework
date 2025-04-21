from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer
from .models import CustomUser, PhoneOTP
from .permissions import VerifyPhoneRateLimit


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
    
    try:
        
        user = CustomUser.objects.get(phone=phone)
        if not user.phone_verified:

            raise CustomUser.DoesNotExist()
        # When the front end developer checking the content of response, she/he must knew
        # whether the user exists on database or no(newly created and It was not exists on database)
        # for this reason we are passing another information about user to response payload.
        # the frontend developer will check the content of 'userExists' to knew whether she/he
        # must get the password or otp code from user in the next step.
        # If frontend developer saw that the value of 'userExists' is set to True, then
        # she/he will found that the user already exists in database and he/she must display
        # the field to user to get the password of that user.
        return Response(
            {
                'message': 'user exists!',
                'userExists': 'true'
            },
            status=status.HTTP_200_OK
        )
    
    # if the user does not exists, then we will generate otp code for him/her and will send it to user via sms 
    except CustomUser.DoesNotExist:
        otp_code = PhoneOTP.generate_otp()

        user, created = CustomUser.objects.get_or_create(phone=phone)
        
        if created:
            otp_obj = PhoneOTP.objects.create(
                user=user,
                otp_code=otp_code
            )
        else:
            otp_obj = user.otp
            otp_obj.otp_code = otp_code
            otp_obj.created_at = timezone.now()
            otp_obj.save()


        otp_obj.send_sms(message='')
        # when the user does not exists on database, we inform frontend developer about this topic by
        # setting 'userExists' to false, in this case the frontend developer will display a field to user
        # for getting otp code sent to user
        return Response(
            {
                "message":f"User not found.OTP code send to {phone}.",
                'userExists': 'false',
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
        user = CustomUser.objects.get(phone=phone)
    
        if int(user.otp.otp_code) != int(otp):
            return Response({'error': 'Invalid OTP code!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.otp.is_expired():
            return Response({"message": "This OTP code has expired!"}, status=status.HTTP_401_UNAUTHORIZED)

        # We will not allow user to use one OTP code twice.
        if user.otp.used:
            return Response({'error': 'This OTP code is used already, please get another otp code'}, status=status.HTTP_403_FORBIDDEN)
        

        user.phone_verified = True
        user.save()

        # Settings the the current otp as used
        otp_obj = user.otp
        otp_obj.used = True
        otp_obj.save()

        token, created = Token.objects.get_or_create(user=user)

        return Response({'message': 'Verified Successfully', 'token': token.key}, status=status.HTTP_200_OK)
        
    except CustomUser.DoesNotExist:
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

    if not phone or not first_name or not last_name:
        return Response({'error': 'Phone number, Email, first name and last name are required!'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(phone=phone)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        serializer = UserSerializer(user)
        
        return Response({'message': 'User credentials stored successfully!', 'credentials': serializer.data}, status=status.HTTP_200_OK)
    
    except CustomUser.DoesNotExist:
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

