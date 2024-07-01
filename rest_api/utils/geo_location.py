import requests
from rest_framework.exceptions import ValidationError

from website_backend.constants import DISALLOWED_COUNTRIES


def get_country(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    response = requests.get(f"https://geolocation-db.com/json/{ip}/").json()
    country = response.get('country_code', '')

    if country in DISALLOWED_COUNTRIES:
        raise ValidationError({'permission denied': "IP belonging to a disallowed country"})

    if country == 'Not found':
        return ''
    else:
        return country
