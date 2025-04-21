from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException

from django.conf import settings
from django.core.cache import cache

from accounts.utils import get_ipaddress

import time
import math


class TooManyRequests(APIException):
    """Custom exception for rate limiting."""
    status_code = 429
    default_detail = 'Request limit exceeded. Please try again later.'
    default_code = 'too_many_requests'


class VerifyPhoneRateLimit(BasePermission):

    rate_limit = getattr(settings, 'PHONE_RATE_LIMIT', 3)
    rate_limit_time = getattr(settings, 'PHONE_RATE_LIMIT_TIME', 60 * 60)

    def has_permission(self, request, view):
        
        
        ip_ = get_ipaddress(request)
        
        if not ip_:
            return True
        
        view_name = view.get_view_name().lower().replace(' ', '_')

        prefix = f"rate_limit:{view_name}"
        count_key = f"{prefix}:count:{ip_}"
        block_key = f"{prefix}:block:{ip_}"

        # check to see if the user already blocked
        block_end_time = cache.get(block_key)

        if block_end_time is not None:
            remaining_time = block_end_time - time.time()
            if remaining_time > 0:
                minutes, seconds = divmod(math.ceil(remaining_time), 60)
                if minutes > 0:
                    message = f"Your IP address is blocked for {minutes} minute{'s' if minutes > 1 else ''} and {seconds} second{'s' if seconds > 1 else ''}!"
                else:
                    message = f'Your IP address is blocked for {seconds} second{'s' if seconds > 1 else ''}!'

                raise TooManyRequests(f"Too many requests from {ip_}.{message}")

            else:
                cache.delete(block_key)
        
        added = cache.add(count_key, 1, self.rate_limit_time)

        if added:
            current_count = 1

        else:
            try:
                current_count = cache.incr(count_key)
            except ValueError:
                cache.set(count_key, 1, self.rate_limit_time)
                current_count = 1
            except Exception as e:
                print(f"Caching error occurred when trying to increment for key {count_key}: {e}")
                return True
            

        if current_count is not None and current_count > self.rate_limit:
            block_end_time = time.time() + self.rate_limit_time

            cache.set(block_key, block_end_time, self.rate_limit_time)

            minutes, seconds = divmod(math.ceil(self.rate_limit_time), 60)
            if minutes > 0:
                message = f"Please try again in {minutes} minute{'s' if minutes > 1 else ''} and {seconds} second{'s' if seconds > 1 else ''}!"
           
            else:
                message = f'Please try again in {seconds} second{'s' if seconds > 1 else ''}!'
            
            raise TooManyRequests(f'Too many request from {ip_}.{message}')        
        
        return True
    