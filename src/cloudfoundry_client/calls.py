import requests
import json
import logging

# hide underneath logs
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARN)


class InvalidStatusCode(Exception):
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body

    def __str__(self):
        if self.body is None:
            return '%d' % self.status_code
        elif type(self.body) == str:
            return '%d : %s' % (self.status_code, self.body)
        else:
            return '%d : %s' % (self.status_code, json.dumps(self.body))


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
        if skip_verifications:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            import warnings
            warnings.filterwarnings('ignore', 'Unverified HTTPS request is being made.*', InsecureRequestWarning)

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

    def delete(self, url, **kwargs):
        return self._check_response(requests.delete(url,
                                                    proxies=self._proxy,
                                                    verify=not self._skip_verifications,
                                                    **kwargs))

    @staticmethod
    def _check_response(response):
        if response.status_code / 100 == 2:
            return response
        else:
            try:
                body = response.json()
            except Exception, _:
                body = response.text
            raise InvalidStatusCode(response.status_code, body)


caller = _Caller()

