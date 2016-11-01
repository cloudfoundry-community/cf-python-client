import logging
import re
from cloudfoundry_client.loggregator.logmessage_pb2 import LogMessage
from cloudfoundry_client.entities import EntityManager

_logger = logging.getLogger(__name__)


class InvalidLoggregatorResponseException(Exception):
    pass


class LoggregatorManager(object):
    def __init__(self, logging_endpoint, credentials_manager):
        self.logging_endpoint = logging_endpoint
        self.credentials_manager = credentials_manager

    def get_recent(self, application_guid):
        url = '%s/recent?app=%s' % (re.sub(r'^ws', 'http', self.logging_endpoint), application_guid)
        response = EntityManager._check_response(self.credentials_manager.get(url, stream=True))
        boundary = LoggregatorManager._extract_boundary(response)
        for part in LoggregatorManager._read_multi_part_response(response, boundary):
            message_read = LogMessage()
            message_read.ParseFromString(part)
            yield message_read

    @staticmethod
    def _extract_boundary(response):
        boundary = response.headers['content-type']
        boundary_field = 'boundary='
        idx = boundary.find(boundary_field)
        if idx == -1:
            _logger.debug(response.text)
            raise InvalidLoggregatorResponseException('Cannot extract boundary in %s' % boundary)
        boundary = boundary[idx + len(boundary_field):]
        idx = boundary.find(' ')
        if idx != -1:
            boundary = boundary[:idx]
        return boundary

    @staticmethod
    def _read_multi_part_response(iterable, boundary):
        remaining = ''
        boundary_header = '--%s' % boundary
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
                    # _logger.debug('found boundary in %d byte', (cpt_read - (len(work) - idx)))
                    if idx > 0:
                        part = work[:idx]
                        # do not use rstrip or lstrip
                        while part.find('\r\n', 0, 2) == 0:
                            part = part[2:]
                        while part.rfind('\r\n', len(part) - 2) == (len(part) - 2):
                            part = part[0:len(part) - 2]
                        yield part
                    work = work[idx + len(boundary_header):]
                    if work[0] == '-' and work[1] == '-':
                        _logger.debug('end boundary reached')
                        return
                    else:
                        idx = work.find(boundary_header)
                remaining = work
