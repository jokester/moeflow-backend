"""
文件存储服务 (基本用于图片)

- 读写文件 (本地或云)
- 为文件生成供客户端使用的URL

代替1.0.7之前的oss+本地存储
"""

from __future__ import annotations

import io
import werkzeug
import opendal
from typing import Union, Optional, List

from app.constants.storage import StorageType, OpendalStorageService
from asgiref.sync import async_to_sync
from app.utils.logging import logger
from .file_storage_abstract import AbstractStorageService


def create_opendal_storage_service(config: dict[str, str]) -> OpenDalStorageService:
    if config['STORAGE_TYPE'] != StorageType.OPENDAL:
        raise Exception("unexpected STORAGE_TYPE")

    if config.get('OPENDAL_SERVICE') == OpendalStorageService.GCS:
        url_builder = GcpUrlBuilder(config)

        operator = opendal.AsyncOperator("gcs",
                                         bucket=config['OPENDAL_GCS_BUCKET'],
                                         root="/")
        return OpenDalStorageService(url_builder, operator)

    raise Exception("unsupported STORAGE_PROVIDER: {0}".format(config.get('OPENDAL_SERVICE')))


def read_key_file(path_or_value: str) -> str:
    with open(path_or_value, "r") as f:
        return f.read()


class OpenDalStorageService(AbstractStorageService):
    """
    各种云存储服务的io
    """

    def __init__(self, url_builder: GcpUrlBuilder, operator: opendal.AsyncOperator):
        self.url_builder = url_builder
        self.operator = operator

    def upload(self, path: str, filename: str,
               file: io.BufferedReader | werkzeug.wrappers.request.FileStorage | str,
               headers: Optional[dict[str, int | str]] = None, progress_callback=None) -> None:
        self._sync_upload(path, filename, file, headers or {})

    @async_to_sync
    async def _sync_upload(self, path: str, filename: str,
                           file: io.BufferedReader | werkzeug.wrappers.request.FileStorage | str,
                           headers: dict[str, int | str]):
        blob: bytes = file.encode() if isinstance(file, str) else file.read()
        write_kwargs = {
            k: headers[k]
            for k in ['content_type']
            if k in headers
        }
        await self.operator.write(path + filename, blob, **write_kwargs)

    def download(self, path: str, filename: str, /, *, local_path=None) -> Optional[io.BytesIO]:
        downloaded: memoryview = self._sync_download(path, filename)
        raise NotImplementedError("子类需要实现该方法")

    @async_to_sync
    async def _sync_download(self, path: str, filename: str):
        return await self.operator.read("{0}/{1}".format(path, filename))

    def download_to_file(self, path: str, filename: str, local_path: str) -> io.BytesIO:
        """下载文件"""
        raise NotImplementedError("子类需要实现该方法")

    def is_exist(self, path, filename, process_name=None):
        """检查文件是否存在"""
        raise NotImplementedError("子类需要实现该方法")

    def delete(self, path: str, filename: Union[List[str], str]):
        self._sync_delete(path, filename)

    @async_to_sync
    async def _sync_delete(self, path: str, filename: Union[List[str], str]):
        pass

    def sign_url(self, path_prefix: str, filename: str, expires: int = 3600, process_name: str = None) -> str:
        """生成URL"""
        return self.url_builder.create_public_url(path_prefix, filename, expires=expires, process_name=process_name)


class GcpUrlBuilder:
    """
    GCP Cloud Storage的URL生成
    """

    def __init__(self, options: dict[str, str]):
        self.bucket_name = options['OPENDAL_GCS_BUCKET']

    def create_public_url(self, path_prefix: str, filename: str, /, **kwargs) -> str:
        return f"https://storage.cloud.google.com/{self.bucket_name}/{path_prefix}{filename}"
