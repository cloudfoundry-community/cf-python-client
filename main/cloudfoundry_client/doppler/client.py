import logging
import re
from typing import Generator
from urllib.parse import urlparse

from oauth2_client.credentials_manager import CredentialManager
from requests import Response

from cloudfoundry_client.doppler.websocket_envelope_reader import WebsocketFrameReader
from cloudfoundry_client.dropsonde.envelope_pb2 import Envelope
from cloudfoundry_client.errors import InvalidLogResponseException

_logger = logging.getLogger(__name__)

EnvelopeStream = Generator[Envelope, None, None]


class DopplerClient(object):
    def __init__(self, doppler_endpoint: str, proxy: dict, verify_ssl: bool, credentials_manager: CredentialManager):
        self.proxy_host = None
        self.proxy_port = None
        self.ws_doppler_endpoint = doppler_endpoint
        self.http_doppler_endpoint = re.sub("^ws", "http", doppler_endpoint)
        self.verify_ssl = verify_ssl
        self.credentials_manager = credentials_manager
        if proxy is not None and len(proxy) > 0:
            proxy_domain = urlparse(proxy).netloc
            idx = proxy_domain.find(":")
            if 0 < idx < len(proxy_domain) - 2:
                self.proxy_host = proxy_domain[:idx]
                self.proxy_port = int(proxy_domain[idx + 1 :])

    def recent_logs(self, app_guid: str) -> EnvelopeStream:
        url = "%s/apps/%s/recentlogs" % (self.http_doppler_endpoint, app_guid)
        response = self.credentials_manager.get(url, stream=True)
        boundary = DopplerClient._extract_boundary(response)
        _logger.debug("Boundary: %s" % boundary)
        for part in DopplerClient._read_multi_part_response(response, boundary):
            yield DopplerClient._parse_envelope(part)

    def stream_logs(self, app_guid: str) -> EnvelopeStream:
        url = "%s/apps/%s/stream" % (self.ws_doppler_endpoint, app_guid)
        with WebsocketFrameReader(
            url,
            lambda: self.credentials_manager._access_token,
            verify_ssl=self.verify_ssl,
            proxy_host=self.proxy_host,
            proxy_port=self.proxy_port,
        ) as websocket:
            for message in websocket:
                yield DopplerClient._parse_envelope(message)

    @staticmethod
    def _parse_envelope(raw) -> Envelope:
        envelope = Envelope()
        envelope.ParseFromString(raw)
        return envelope

    @staticmethod
    def _extract_boundary(response: Response) -> str:
        content_type = response.headers["content-type"]
        _logger.debug("content-type=%s" % content_type)
        boundary_field = "boundary="
        idx = content_type.find(boundary_field)
        if idx == -1:
            _logger.debug(response.text)
            raise InvalidLogResponseException("Cannot extract boundary in %s" % content_type)
        boundary = content_type[idx + len(boundary_field) :]
        idx = boundary.find(" ")
        if idx != -1:
            boundary = boundary[:idx]
        return boundary

    @staticmethod
    def _read_multi_part_response(iterable, boundary):
        remaining = ""
        boundary_header = bytes("--%s" % boundary, "UTF-8")
        end_of_line = bytes("\r\n", "UTF-8")
        cpt_read = 0
        for chunk_data in iterable:
            # _logger.debug('reading %d bytes' % size)
            cpt_read += len(chunk_data)
            if len(chunk_data) == 0:
                # _logger.debug('end of file reached after %d bytes' % cpt_read)
                if len(remaining) > 0:
                    # _logger.debug('returning last data')
                    yield remaining
                return
            else:
                work = remaining + chunk_data if len(remaining) > 0 else chunk_data
                idx = work.find(boundary_header)
                while idx >= 0 and (idx + len(boundary_header) + 2) <= len(work):
                    if idx > 0:
                        part = work[:idx]
                        # do not use rstrip or lstrip
                        while part.find(end_of_line, 0, 2) == 0:
                            part = part[2:]
                        while part.rfind(end_of_line, len(part) - 2) == (len(part) - 2):
                            part = part[0 : len(part) - 2]
                        yield part
                    work = work[idx + len(boundary_header) :]
                    if work[0] == "-" and work[1] == "-":
                        _logger.debug("end boundary reached")
                        return
                    else:
                        idx = work.find(boundary_header)
                remaining = work
