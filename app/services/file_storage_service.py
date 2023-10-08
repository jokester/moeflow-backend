"""
文件存储服务 (基本用于图片)

- 读写文件 (本地或云)
- 为文件生成供客户端使用的URL

代替1.0.7之前的oss+本地存储
"""

from __future__ import annotations
from io import BufferedReader
import asyncio
import opendal
from typing import Union

from app.constants.storage import StorageType
from app.services.oss import OSS
from .asyncio import wait_task


def create_file_storage_service(config: dict[str, str]) -> Union[OpenDalStorageService, OSS]:
    if config['STORAGE_TYPE'] == StorageType.LOCAL_STORAGE:
        return OSS(config)
    elif config['STORAGE_TYPE'] == StorageType.OSS:
        return OSS(config)
    elif config['STORAGE_TYPE'] == StorageType.GCS:
        url_builder = GcpUrlBuilder(config)
        operator = opendal.AsyncOperator("gcs",
                                    bucket="moeflow-dev-assets",
                                    root="object-prefix",
                                    predefined_acl="publicRead")
        return OpenDalStorageService(url_builder, operator)
    else:
        raise NotImplementedError("不支持的存储类型: %s" % config['STORAGE_TYPE'])


class OpenDalStorageService():
    """
    各种云存储服务的io
    """

    def __init__(self, url_builder: Union[GcpUrlBuilder], operator: opendal.AsyncOperator):
        self.url_builder = url_builder
        self.operator = operator

    def upload(self, path_prefix: str, filename: str, file: BufferedReader, headers: dict[str, str] = None):
        blob = file.read()
        written = self.operator.write(path_prefix + filename, blob)
        wait_task(written)

    def download(self, path_prefix: str, filename: str, ) -> BufferedReader:
        raise NotImplementedError("子类需要实现该方法")

    def is_exist(self, path, filename, process_name=None):
        """检查文件是否存在"""
        raise NotImplementedError("子类需要实现该方法")

    def sign_url(self, path_prefix: str, filename: str, expires: int = 3600, process_name: str = None) -> str:
        """生成URL"""
        return self.url_builder.sign_url(path_prefix, filename, expires=expires, process_name=process_name)


class GcpUrlBuilder():
    """
    GCP Cloud Storage的URL生成
    """

    def __init__(self, options: dict[str, str]):
        print(options)
        self.bucket_name = options['GCS_BUCKET_NAME']

    def sign_url(self, path_prefix: str, filename: str, **kwargs) -> str:
        return "https://wtf?prefix=%s&filename=%s" % (path_prefix, filename)
