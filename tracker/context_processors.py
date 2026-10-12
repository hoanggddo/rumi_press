from django.conf import settings


def account_features(request):
    return {'password_reset_enabled': settings.PASSWORD_RESET_ENABLED}