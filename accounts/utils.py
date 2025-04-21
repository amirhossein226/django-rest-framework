
def get_ipaddress(request):
    """
    This function will be helper to get the user's ip address.
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')


    return ip if ip else None
