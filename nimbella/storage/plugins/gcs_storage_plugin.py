from .abstract_storage_plugin import AbstractStoragePlugin, AbstractStorageFile

from google.cloud import storage as gstorage
from google.cloud.storage.blob import Blob
from google.oauth2 import service_account

from typing import Union

# Simple wrapper around GoogleCloudStorage Blob class to provide
# generic "storage file" for this provider
class GoogleCloudStorageFile(AbstractStorageFile):
    def __init__(self, blob: Blob):
        self.blob = blob

    @property
    def name(self) -> str:
        return self.blob.name

    @property
    def metadata(self) -> dict:
        return self.blob.metadata

    @metadata.setter
    def metadata(self, metadata: dict):
        self.blob.metadata = metadata

    def exists(self) -> bool:
        return self.blob.exists()

    def delete(self) -> None:
        self.blob.delete()

    def save(self, data: Union[str, bytes], contentType: str) -> None:
        self.blob.upload_from_string(data=data, content_type=contentType)

    def download(self) -> bytes:
        return self.blob.download_as_bytes()

    def signed_url(self, version: str, action: str, expires: int, contentType: str) -> str:
        return self.blob.generate_signed_url(expiration=expires, version=version, method=action, response_type=contentType)

# Simple wrapper around GoogleCloudStorage bucket class to provide
# generic bucket storage service for this provider
class GoogleCloudStoragePlugin(AbstractStoragePlugin):
    def __init__(self, client, namespace, apiHost, web, credentials):
        super().__init__(client, namespace, apiHost, web, credentials)
        self.bucket = self.client.get_bucket(self.bucket_key)

    @staticmethod
    def id() -> str:
        return "@nimbella/storage-gcs"

    @staticmethod
    def prepare_creds(credentials: dict) -> service_account.Credentials:
        return service_account.Credentials.from_service_account_info(credentials)

    @staticmethod
    def create_client(credentials: service_account.Credentials) -> gstorage.Client:
        return gstorage.Client(credentials=credentials)

    @property
    def url(self) -> Union[str, None]:
        if self.web:
            return f'https://{self.bucket_key}'

    def file(self, destination) -> GoogleCloudStorageFile:
        return GoogleCloudStorageFile(self.bucket.blob(destination))

    def deleteFiles(self, prefix=None):
        blobs_to_delete = list(self.client.list_blobs(self.bucket, prefix=prefix))
        self.bucket.delete_blobs(blobs_to_delete)

    def upload(self, path, destination, contentType, cacheControl):
        blob = self.bucket.blob(destination)
        blob.cache_control = cacheControl
        with open(path, "rb") as f:
            blob.upload_from_file(file_obj=f, content_type=contentType)

    def setWebsite(self, mainPageSuffix = None, notFoundPage = None):
        self.bucket.configure_website(mainPageSuffix, notFoundPage)

    def getFiles(self, prefix = None) -> list:
        all_blobs = list(self.client.list_blobs(self.bucket, prefix=prefix))
        return list(map(lambda b: GoogleCloudStorageFile(b), all_blobs))

    @property
    def bucket_key(self):
        hostpart = '-'.join(self.apiHost.replace('https://', '').split('.'))
        datapart = '' if self.web else 'data-'
        return f'{datapart}{self.namespace}-{hostpart}'
