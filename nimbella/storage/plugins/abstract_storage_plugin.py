import abc
import typing
from typing import Union

# Abstract Bucket File Interface.
# Hides provider implementation bucket file class instances
class AbstractStorageFile(abc.ABC):
    # Name of the bucket file
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    # key/value pairs for provider-specific object metadata
    @property
    @abc.abstractmethod
    def metadata(self) -> dict:
        pass

    @metadata.setter
    @abc.abstractmethod
    def metadata(self, metadata: dict):
        pass

    # does file exist?
    @abc.abstractmethod
    def exists(self) -> bool:
        pass

    # delete file from bucket
    @abc.abstractmethod
    def delete(self) -> None:
        pass

    # update file contents from string or bytes with content-type
    @abc.abstractmethod
    def save(self, data: Union[str, bytes], contentType: str) -> None:
        pass

    # return file contents as bytes
    @abc.abstractmethod
    def download(self) -> bytes:
        pass

    # return pre-signed url from file for external access
    @abc.abstractmethod
    def signed_url(self, version: str, action: str, expires: int, contentType: str) -> str:
        pass

# Abstract interface for a storage provider.
class AbstractStoragePlugin(abc.ABC):
    def __init__(self, client, namespace, apiHost, web, credentials):
        self.client = client
        self.namespace = namespace
        self.apiHost = apiHost
        self.web = web
        self.credentials = credentials
        pass

    # Static method used to access provider identifier without 
    # having to create a new class instance.
    @staticmethod
    @abc.abstractmethod
    def id():
        pass

    # Provider-specific method to convert JSON creds from platform
    # into credentials ready for passing into constructor.
    @staticmethod
    @abc.abstractmethod
    def prepare_creds():
        pass

    # Provider-specific method to create new provider storage
    # client from credentials
    @staticmethod
    @abc.abstractmethod
    def create_client():
        pass

    # External bucket URL
    @property
    @abc.abstractmethod
    def url(self) -> Union[str, None]:
        pass

    # Configure website for web storage buckets
    @abc.abstractmethod
    def setWebsite(self, mainPageSuffix, notFoundPage):
        pass

    # Remove all files from the bucket (using optional prefix)
    @abc.abstractmethod
    def deleteFiles(self, force, prefix):
        pass

    # Upload new file from path to bucket destination.
    @abc.abstractmethod
    def upload(self, path, destination, contentType, cacheControl):
        pass

    # Return storage file instance from bucket
    @abc.abstractmethod
    def file(self, destination) -> AbstractStorageFile:
        pass

    # Return all storage files (with optional prefix) instance from bucket
    @abc.abstractmethod
    def getFiles(self, prefix) -> list:
        pass
