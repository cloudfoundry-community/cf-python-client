import logging
import aiohttp
from cloudfoundry_client.imported import urlparse

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
            idx = proxy_domain.find(':')
            if 0 < idx < len(proxy_domain) - 2:
                self.proxy_host = proxy_domain[:idx]
                self.proxy_port = int(proxy_domain[idx + 1:])

    async def stream_logs(self, app_guid):
        url = '%s/v2/read?log&source_id=%s' % (self.rlp_gateway_endpoint, app_guid)
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                    url=url,
                    headers={"Authorization": self.credentials_manager._access_token},
                )
            if response.status == 204:
                yield {}
            else:
                async for data in response.content.iter_any():
                    yield data
