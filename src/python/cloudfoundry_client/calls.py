import requests
import json
import logging
from requests.exceptions import ConnectionError as NativeConnectionError

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


class ConnectionError(Exception):
    pass


class OutputFormat(object):
    JSON = 1
    TEXT = 2
    RAW = 3

    def __init__(self):
        raise NotImplementedError('OutputFormat cannot be instantiated')


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
        return self._invoke_method(requests.get, url, **kwargs)

    def post(self, url, **kwargs):
        return self._invoke_method(requests.post, url, **kwargs)

    def put(self, url, **kwargs):
        return self._invoke_method(requests.put, url, **kwargs)

    def delete(self, url, **kwargs):
        return self._invoke_method(requests.delete, url, **kwargs)

    def _invoke_method(self, method, url, **kwargs):
        output_format = kwargs.get('output_format', None)
        if output_format is None:
            output_format = OutputFormat.JSON
        else:
            del kwargs['output_format']
        if output_format != OutputFormat.JSON and output_format != OutputFormat.TEXT \
                and output_format != OutputFormat.RAW:
            raise AttributeError('Invalid output format')
        if output_format == OutputFormat.RAW:
            kwargs['stream'] = True
        try:
            response = self._check_response(method(url,
                                                   proxies=self._proxy,
                                                   verify=not self._skip_verifications,
                                                   **kwargs))
            if output_format == OutputFormat.JSON:
                return response.json()
            elif output_format == OutputFormat.RAW:
                return response
            elif output_format == OutputFormat.TEXT:
                return response.text
        except NativeConnectionError, _:
            raise ConnectionError()

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

