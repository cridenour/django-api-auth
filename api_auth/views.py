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


class APIView(View):
    """
    API View

     * Offers functions for returning JSON objects
     * Catches api_auth.exceptions and returns intelligent HTTP status code
     * Pareses request body to JSON object if one exists
     * Defaults to only allowing OPTIONS HTTP method
    """
    http_method_names = ['options', ]

    def _parse_body(self, request):
        """
        Internal function to parse out the post data.
        """
        return json.loads(request.body)

    def json_response(self, request, *args, **kwargs):
        """
        Calls internal functions and returns the expected 2xx status or fails with another status
        """

        # What is our expected HTTP Status Code on success?
        success_status = kwargs.get('status_code', 200)

        # Does this request have a payload?
        has_payload = request.body is not None

        # Initialize our data variable
        data = {}

        if has_payload:
            try:
                data = self._parse_body(request)
            except TypeError as e:
                logger.exception('Error decoding JSON', e.args)
                return HttpResponse(status=400)

        try:
            if has_payload:
                response = self.parse_data(request, data, *args, **kwargs)
            else:
                response = self.get_data(request, *args, **kwargs)

            if type(response) is dict or type(response) is list:
                return HttpResponse(
                    status=success_status,
                    content_type='application/json',
                    content=json.dumps(response)
                )
            elif response:
                return HttpResponse(status=success_status)

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
        raise NotImplementedError('%s methods require a parse_data function.' % request.method)

    def get_data(self, request, *args, **kwargs):
        """
        Return true or an object for 200. Throw exceptions otherwise.
        """
        raise NotImplementedError('%s methods require a get_data function.' % request.method)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """
        Ensure CSRF tokens are not required on our calls
        """
        return super(APIView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Set a default status code for a success - easy to override
        kwargs.update({'status_code': 200})
        return self.json_response(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Set a default status code for a success - easy to override
        kwargs.update({'status_code': 200})
        return self.json_response(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # Set a default status code for a success - easy to override
        kwargs.update({'status_code': 201})
        return self.json_response(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Set a default status code for a success - easy to override
        kwargs.update({'status_code': 200})
        return self.json_response(request, *args, **kwargs)


class ProtectedView(APIView):
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