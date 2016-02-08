import unittest
import logging
from cloudfoundry_client.loggregator.logmessage_pb2 import LogMessage
from cloudfoundry_client.loggregator.loggregator import LoggregatorManager
import os
from config_test import get_resource, get_build_dir, build_client_from_configuration, get_resource_dir

_logger = logging.getLogger(__name__)


class TestProtobuf(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestProtobuf, self).__init__(*args, **kwargs)
        # do this to do all init such as logging
        build_client_from_configuration()
        self.expected_nb_parts = 5946
        self.boundary = '7e061f8d6ec00677d6f6b17fcafec9eef2e3a2360e557f72e3e1116efcec'
        self.first_message = LogMessage()
        self.first_message.message = 'Updated app with guid 3048d795-f031-435f-85e8-71dce339e869 ({"state"=>"STOPPED"})'
        self.first_message.message_type = LogMessage.OUT
        self.first_message.timestamp = 1453887321557121799
        self.first_message.app_id = '3048d795-f031-435f-85e8-71dce339e869'
        self.first_message.source_id = '0'
        self.first_message.source_name = 'API'

    @staticmethod
    def file_reader(file_path, size):
        with open(file_path, 'rb') as f:
            while True:
                chunk_data = f.read(size)
                if len(chunk_data) == 0:
                    return
                else:
                    yield chunk_data

    def test_read_multi_part_response(self):
        dest_file = os.path.join(get_build_dir(), 'logs_recents.bin')
        source_file = get_resource('logs_recents.bin' )
        with open(dest_file, "wb") as f:
            cpt_part = 0
            for part in LoggregatorManager._read_multi_part_response(TestProtobuf.file_reader(
                    source_file, 128),
                    self.boundary):
                f.write('--%s\r\n\r\n' % self.boundary)
                f.write(part)
                f.write('\r\n')
                cpt_part += 1
            f.write('--%s--\r\n' % self.boundary)
        self.assertEqual(cpt_part, self.expected_nb_parts,
                         'Nb of parts does not match. Expected (%d) got (%d)' % (self.expected_nb_parts, cpt_part))
        dest_size = os.stat(dest_file).st_size
        source_size = os.stat(source_file).st_size
        self.assertEqual(source_size, dest_size)

    def test_load(self):
        for part in LoggregatorManager._read_multi_part_response(TestProtobuf.file_reader(
                get_resource('logs_recents.bin'), 128),
                self.boundary):
            message = LogMessage()
            message.ParseFromString(part)

    def test_load_unload(self):
        res = self.first_message.SerializeToString()
        _logger.debug("Message serialized successfully")
        message_read = LogMessage()
        message_read.ParseFromString(res)
        _logger.debug("Message deserialized successfully")
        self.assertEqual(message_read.message, self.first_message.message)
        self.assertEqual(message_read.message_type, self.first_message.message_type)
        self.assertEqual(message_read.timestamp, self.first_message.timestamp)
        self.assertEqual(message_read.app_id, self.first_message.app_id)
        self.assertEqual(message_read.source_id, self.first_message.source_id)
        self.assertEqual(message_read.source_name, self.first_message.source_name)

    def test_first_line(self):
        first_part = None
        for part in LoggregatorManager._read_multi_part_response(TestProtobuf.file_reader(
                get_resource('logs_recents.bin' ), 128),
                self.boundary):
            first_part = part
            break
        self.assertIsNotNone(first_part)
        first_line = self.first_message.SerializeToString()

        self.assertEqual(first_line, first_part)

