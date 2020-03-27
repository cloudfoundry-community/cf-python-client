import logging
from urllib.parse import urlparse

import aiohttp

_logger = logging.getLogger(__name__)


class RLPGatewayClient(object):
    """
    A client to read application logs directly from RLP gateway.

    The client is initialized with client id and client secret,
    and provides functionality for asynchronous HTTP requests to RLP gateway endpoint.
    """

    def __init__(self, rlp_gateway_endpoint, proxy, verify_ssl, credentials_manager):
        self.proxy_host = None
        self.proxy_port = None
        self.rlp_gateway_endpoint = rlp_gateway_endpoint
        self.verify_ssl = verify_ssl
        self.credentials_manager = credentials_manager

        if proxy is not None and len(proxy) > 0:
            proxy_domain = urlparse(proxy).netloc
            idx = proxy_domain.find(":")
            if 0 < idx < len(proxy_domain) - 2:
                self.proxy_host = proxy_domain[:idx]
                self.proxy_port = int(proxy_domain[idx + 1 :])

    async def stream_logs(self, app_guid, **kwargs):
        url = f"{self.rlp_gateway_endpoint}/v2/read"
        headers = dict(Authorization=self.credentials_manager._access_token)
        params = dict(log="", source_id=app_guid)
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        if "params" in kwargs:
            params.update(kwargs["params"])
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url=url, params=params) as response:
                if response.status == 204:
                    yield {}
                else:
                    async for data in response.content.iter_any():
                        yield data
