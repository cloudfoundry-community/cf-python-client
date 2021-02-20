import hashlib
import os
import stat
import zipfile
from typing import Callable, Optional, Generator, Tuple, List


class FileHelper(object):
    @staticmethod
    def zip(file_location: str, directory_path: str, accept: Optional[Callable[[str], bool]] = None):
        with zipfile.ZipFile(file_location, "w", zipfile.ZIP_DEFLATED) as archive_out:
            for dir_path, file_names in FileHelper.walk(directory_path):
                dir_full_location = os.path.join(directory_path, dir_path)
                if len(dir_path) > 0:
                    archive_out.write(dir_full_location, dir_path, zipfile.ZIP_STORED)
                for file_name in file_names:
                    file_relative_location = os.path.join(dir_path, file_name)
                    if accept is None or accept(file_relative_location):
                        archive_out.write(
                            os.path.join(dir_full_location, file_name), file_relative_location, zipfile.ZIP_DEFLATED
                        )

    @staticmethod
    def unzip(path: str, tmp_dir: str):
        with zipfile.ZipFile(path, "r") as zip_ref:
            for entry in zip_ref.namelist():
                filename = os.path.basename(entry)
                path_to_create = os.path.join(tmp_dir, entry)
                if not filename and not os.path.isdir(path_to_create):
                    os.makedirs(path_to_create)
                else:
                    zip_ref.extract(entry, tmp_dir)

    @staticmethod
    def walk(path: str) -> Generator[Tuple[str, List[str]], None, None]:
        for dir_path, _, files in os.walk(path, topdown=True):
            yield dir_path[len(path) :].lstrip("/"), files

    @staticmethod
    def sha1(file_location: str) -> str:
        sha1 = hashlib.sha1()
        with open(file_location, "rb") as f:
            while True:
                data = f.read(64 * 1024)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    @staticmethod
    def size(path: str) -> int:
        return os.path.getsize(path)

    @staticmethod
    def mode(file_location: str) -> str:
        mode = str(oct(stat.S_IMODE(os.lstat(file_location).st_mode)))
        return mode[len(mode) - 3 :]
