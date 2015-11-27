import requests


class InvalidStatusCode(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


_proxy = None
_skip_verification = False


class _Caller(object):
    def __init__(self):
        self._skip_verifications = False
        self._proxy = None

    def proxy(self, proxy):
        self._proxy = proxy

    def skip_verifications(self, skip_verifications):
        self._skip_verifications = skip_verifications

    def get(self, url, **kwargs):
        return self._check_response(requests.get(url,
                                                 proxies=self._proxy,
                                                 verify=not self._skip_verifications,
                                                 **kwargs))

    def post(self, url, data=None, json=None, **kwargs):
        return self._check_response(requests.post(url, data=data, json=json,
                                                  proxies=self._proxy,
                                                  verify=not self._skip_verifications,
                                                  **kwargs))

    def put(self, url, data=None, json=None, **kwargs):
        return self._check_response(requests.put(url, data=data, json=json,
                                                 proxies=self._proxy,
                                                 verify=not self._skip_verifications,
                                                 **kwargs))

    @staticmethod
    def _check_response(response):
        if response.status_code / 100 == 2:
            return response
        else:
            raise InvalidStatusCode(response.status_code)

caller = _Caller()

