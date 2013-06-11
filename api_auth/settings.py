from django.conf import settings

# How long will a session last? Reset after each login. Defaults to 1 week.
TOKEN_SESSION_LENGTH = getattr(settings, 'TOKEN_SESSION_LENGTH', 604800)

# Customize the logger used inside the default views
TOKEN_LOGGER_NAME = getattr(settings, 'TOKEN_LOGGER_NAME', 'django_token_auth')