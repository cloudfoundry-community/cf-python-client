import ssl
from typing import Callable, Optional

import websocket


class WebsocketFrameReader(object):
    def __init__(
        self,
        url,
        access_token_provider: Callable[[], str],
        verify_ssl: bool = True,
        proxy_host: Optional[str] = None,
        proxy_port: Optional[int] = None,
    ):
        if not verify_ssl:
            self._ws = websocket.WebSocket(sslopt=dict(cert_reqs=ssl.CERT_NONE))
        else:
            self._ws = websocket.WebSocket()
        self._url = url
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port
        self._access_token_provider = access_token_provider

    def connect(self):
        kw_args = dict(header=dict(Authorization="Bearer %s" % self._access_token_provider()))
        if self._proxy_host is not None and self._proxy_port is not None:
            kw_args["http_proxy_host"] = self._proxy_host
            kw_args["http_proxy_port"] = str(self._proxy_port)
        self._ws.connect(self._url, **kw_args)

    def close(self):
        if self._ws.connected:
            self._ws.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        try:
            for frame in self._ws:
                yield frame
        except websocket.WebSocketConnectionClosedException:
            pass
