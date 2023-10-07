"""
文件存储服务 (基本用于图片)

- 读写文件 (本地或云)
- 为文件生成供客户端使用的URL

代替1.0.7之前的oss+本地存储
"""

from __future__ import annotations
from io import BufferedReader
import opendal
from typing import Union

from app.constants.storage import StorageType
from oss import OSS


def create_file_storage_service(config: dict[str, str]) -> Union[OpenDalStorageService, OSS]:
    if config['STORAGE_TYPE'] == StorageType.LOCAL_STORAGE:
        return OSS(config)
    elif config['STORAGE_TYPE'] == StorageType.OSS:
        return OSS(config)
    elif config['STORAGE_TYPE'] == StorageType.GCS:
        url_builder = GcpUrlBuilder(config)
        operator = opendal.Operator("gcs",
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

    def __init(self, url_builder: Union[GcpUrlBuilder], operator: opendal.Operator):
        self.url_builder = url_builder
        self.operator = operator

    def upload(self, path_prefix: str, filename: str, file: BufferedReader, headers: dict[str, str] = None):
        blob = file.read()
        self.operator.write(path_prefix + filename, blob)

    def download(self, path_prefix: str, filename: str, ) -> BufferedReader:
        raise NotImplementedError("子类需要实现该方法")

    def is_exist(self, path, filename, process_name=None):
        """检查文件是否存在"""
        raise NotImplementedError("子类需要实现该方法")


class GcpUrlBuilder():
    """
    GCP Cloud Storage的URL生成
    """

    def __init__(self, options: dict[str, str]):
        self.bucket_name = options['GCS_BUCKET_NAME']
