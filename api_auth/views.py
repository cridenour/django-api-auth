from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse
from django.views.generic import View

from api_auth import AccessDenied, ServiceUnavailable, PageNotFound
from api_auth.models import APIToken
from api_auth import settings

import logging
import json

logger = logging.getLogger(settings.TOKEN_LOGGER_NAME)


class ProtectedView(View):
    """
    Protected View

     * Intercept request and ensure we have an active user
     * Requires a token in the Authorization header of the request
     * Banned users also return 401 so they get redirected to the login page
     * Specific access control should be controlled with a 403
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', None)

        if token is None:
            return HttpResponse(status=401)

        try:
            user = APIToken.valid.get(token=token).user
        except APIToken.DoesNotExist:
            return HttpResponse(status=401)

        if not user.is_active:
            return HttpResponse(status=401)

        request.user = user

        return super(ProtectedView, self).dispatch(request, *args, **kwargs)


class PostJSONView(View):
    http_method_names = 'post'

    def _get_data(self, request):
        """
        Internal function to parse out the post data.
        """
        return json.loads(request.raw_post_data)

    def post(self, request, *args, **kwargs):
        """
        Method called by Django. Handles finding the data and passing to the parse_data function
        """
        try:
            data = self._get_data(request)
        except TypeError as e:
            logger.exception('Error decoding JSON', e.args)
            return HttpResponse(status=400)

        try:
            response = self.parse_data(request, data, *args, **kwargs)

            if type(response) is dict or type(response) is list:
                return HttpResponse(
                    status=200,
                    content_type='application/json',
                    content=json.dumps(response)
                )
            elif response:
                return HttpResponse(status=200)

        except AccessDenied as e:
            logger.info('Access denied to resource.', e.args)
            return HttpResponse(status=403)

        except PageNotFound as e:
            logger.info('Page not found.', e.args)
            return HttpResponse(status=404)

        except ServiceUnavailable as e:
            logger.exception(e, e.args)
            return HttpResponse(status=503)

        except Exception as e:
            logger.exception(e, e.args)
            return HttpResponse(status=500)

    def parse_data(self, request, data, *args, **kwargs):
        """
        Work with the data and return true or an object for 200. Throw exceptions otherwise.
        """
        raise PageNotFound


class GetJSONView(View):
    http_method_names = 'get'

    def get_data(self, request, *args, **kwargs):
        """
        Return true or an object for 200. Throw exceptions otherwise.
        """
        raise PageNotFound

    def get(self, request, *args, **kwargs):
        """
        Method called by Django. Passes actual request to the get_data function
        """
        try:
            response = self.get_data(request, *args, **kwargs)

            if type(response) is dict or type(response) is list:
                return HttpResponse(
                    status=200,
                    content_type='application/json',
                    content=json.dumps(response)
                )
            elif response:
                return HttpResponse(status=200)

        except AccessDenied as e:
            logger.info('Access denied to resource.', e.args)
            return HttpResponse(status=403)

        except PageNotFound as e:
            logger.info('Page not found.', e.args)
            return HttpResponse(status=404)

        except ServiceUnavailable as e:
            logger.exception(e, e.args)
            return HttpResponse(status=503)

        except Exception as e:
            logger.exception(e, e.args)
            return HttpResponse(status=500)
