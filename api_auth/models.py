from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta

import uuid
import hmac
from hashlib import sha1

from api_auth import settings

class ValidTokenManager(models.Manager):
    def get_query_set(self):
        today = now()

        return super(ValidTokenManager, self).get_query_set()\
            .filter(Q(expires__gte=today) | Q(expires=None))\
            .prefetch_related('user')


class APIToken(models.Model):
    """
    This model will generate expirable API tokens. Some code generously borrowed from Django REST Framework

    Uses a custom manager to retrieve only active tokens
    """
    created = models.DateTimeField(auto_now_add=True, editable=False, help_text='When was this token first generated?')
    user = models.OneToOneField(User, related_name='token', help_text='Who does this token belong to?')
    token = models.CharField(max_length=40, unique=True, blank=True, help_text='The token itself.')
    updated = models.DateTimeField(auto_now=True, editable=False, help_text='When was this last updated?')
    expires = models.DateTimeField(blank=True, null=True, default=None, help_text='When does it expire?')

    objects = models.Manager()
    valid = ValidTokenManager()

    class Meta:
        verbose_name = 'User Token'
        verbose_name_plural = 'User Tokens'

    def refresh(self):
        self.expires = now() + timedelta(seconds=settings.TOKEN_SESSION_LENGTH)
        self.token = self.generate_key()
        self.save()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()

        return super(APIToken, self).save(*args, **kwargs)

    def generate_key(self):
        unique = uuid.uuid4()
        return hmac.new(unique.bytes, digestmod=sha1).hexdigest()

    def active(self):
        return self.expires is None or self.expires > now()
    active.boolean = True

    def __unicode__(self):
        return u'Token for %s' % self.user
