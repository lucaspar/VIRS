from functools import wraps

from django.conf import settings
from django.contrib import messages

import json
import urllib

def check_recaptcha(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if request.method == 'POST':

            # ReCAPTCHA validation
            recaptcha_response = request.POST.get('g-recaptcha-response')
            print(recaptcha_response)
            print()
            print()
            print()
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }

            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())

            if result['success']:
                request.recaptcha_is_valid = True

            else:
                request.recaptcha_is_valid = False
                print('\n\n\t>>> invalid reCAPTCHA; try again or disable the "@check_recaptcha" decorator in views.py\n\n')
                messages.error(request, 'reCAPTCHA inválido; por favor, tente novamente.')

        else:
            request.recaptcha_is_valid = True

        return view_func(request, *args, **kwargs)

    return _wrapped_view
