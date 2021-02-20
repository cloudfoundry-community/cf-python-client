import fnmatch
import logging
import os
from typing import List

_logger = logging.getLogger(__name__)


class CfIgnore(object):
    def __init__(self, application_path: str):
        ignore_file_path = os.path.join(application_path, ".cfignore")
        self.ignore_items = []
        if os.path.isfile(ignore_file_path):
            with open(ignore_file_path, "r") as ignore_file:
                for line in ignore_file.readlines():
                    self.ignore_items.extend(self._pattern(line.strip(" \n")))

    def is_entry_ignored(self, relative_file: str) -> bool:
        def is_relative_file_ignored(cf_ignore_entry):
            _logger.debug("is_relative_file_ignored - %s - %s", cf_ignore_entry, relative_file)
            file_path = (
                "/%s" % relative_file if cf_ignore_entry.startswith("/") and not relative_file.startswith("/") else relative_file
            )
            return fnmatch.fnmatch(file_path, cf_ignore_entry)

        return any([is_relative_file_ignored(ignore_item) for ignore_item in self.ignore_items])

    @staticmethod
    def _pattern(pattern: str) -> List[str]:
        if pattern.find("/") < 0:
            return [pattern, os.path.join("**", pattern)]
        elif pattern.endswith("/"):
            return [
                os.path.join("/", pattern, "*"),
                os.path.join("/", pattern, "**", "*"),
                os.path.join("/", "**", pattern, "*"),
                os.path.join("/", "**", pattern, "**", "*"),
            ]
        else:
            return [os.path.join("/", pattern), os.path.join("/", "**", pattern)]
