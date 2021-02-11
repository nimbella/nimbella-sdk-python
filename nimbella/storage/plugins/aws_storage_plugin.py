from .abstract_storage_plugin import AbstractStoragePlugin, AbstractStorageFile

from typing import Union
from urllib.parse import urlparse

import boto3

# Simple wrapper around AWS S3 Object class to provide
# generic "storage file" for this provider
class S3StorageFile(AbstractStorageFile):
    def __init__(self, file):
        self.file = file

    @property
    def name(self) -> str:
        return self.file.key

    @property
    def metadata(self) -> dict:
        # return self.blob.metadata
        pass

    @metadata.setter
    def metadata(self, metadata: dict):
        # self.blob.metadata = metadata
        pass

    def exists(self) -> bool:
        # return self.blob.exists()
        pass

    def delete(self) -> None:
        # self.blob.delete()
        pass

    def save(self, data: Union[str, bytes], contentType: str) -> None:
        # self.blob.upload_from_string(data=data, content_type=contentType)
        pass

    def download(self) -> bytes:
        # return self.blob.download_as_bytes()
        pass

    def signed_url(self, version: str, action: str, expires: int, contentType: str) -> str:
        # return self.blob.generate_signed_url(expiration=expires, version=version, method=action, content_type=contentType)
        pass

# Simple wrapper around GoogleCloudStorage bucket class to provide
# generic bucket storage service for this provider
class AWSStoragePlugin(AbstractStoragePlugin):
    def __init__(self, client, namespace, apiHost, web, credentials):
        super().__init__(client, namespace, apiHost, web, credentials)
        self.bucket = self.client.Bucket(self.bucket_key)

    @staticmethod
    def id() -> str:
        return "@nimbella/storage-aws"

    @staticmethod
    def prepare_creds(credentials: dict) -> dict:
        #return service_account.Credentials.from_service_account_info(credentials)
        pass

    @staticmethod
    def create_client(project_id: str, credentials: dict) -> None:
        #return gstorage.Client(project_id, credentials)
        pass

    @property
    def url(self) -> Union[str, None]:
        if self.web:
            if "weburl" in self.credentials:
                return self.credentials["weburl"]
            else:
                hostname = urlparse(self.credentials["endpoint"]).netloc
                return f"http://{self.namespace}-nimbella-io.{hostname}"

    def file(self, destination) -> S3StorageFile:
        return S3StorageFile(self.bucket.Object(destination))

    def deleteFiles(self, prefix=None) -> None:
        objects = self.client.list_objects_v2(
            Bucket=self.bucket_key,
            Prefix=prefix
        )
        self.bucket.delete_objects(
            Delete={ "Objects": objects["Contents"] }
        )

    def upload(self, path, destination, contentType, cacheControl):
        #blob = self.bucket.blob(destination)
        #blob.cache_control = cacheControl
        #with open(path, "rb") as f:
        #    blob.upload_from_file(file_obj=f, content_type=contentType)
        pass

    def setWebsite(self, mainPageSuffix = None, notFoundPage = None):
        #self.bucket.configure_website(mainPageSuffix, notFoundPage)
        pass

    def getFiles(self, prefix = None) -> list:
        objects = self.client.list_objects_v2(
            Bucket=self.bucket_key,
            Prefix=prefix
        )
        return list(map(lambda o: S3StorageFile(self.bucket.Object(o.get('Key'))), objects.get("Contents")))

    @property
    def bucket_key(self):
        hostpart = "-".join(self.apiHost.replace("https://", "").split("."))
        datapart = "" if self.web else "data-"
        return f"{datapart}{self.namespace}-{hostpart}"
