from .abstract_storage_plugin import AbstractStoragePlugin, AbstractStorageFile

from typing import Union
from urllib.parse import urlparse

import boto3
import botocore

# Simple wrapper around AWS S3 Object class to provide
# generic "storage file" for this provider
class S3StorageFile(AbstractStorageFile):
    def __init__(self, file, web, client):
        self.file = file
        self.web = web
        self.client = client

    @property
    def acl(self) -> str:
        return 'public-read' if self.web else ''

    @property
    def name(self) -> str:
        return self.file.key

    @property
    def metadata(self) -> dict:
        if self.exists():
            return self.file.metadata
        else:
            return {}

    @metadata.setter
    def metadata(self, metadata: dict):
        self.file.copy_from(CopySource={'Bucket':self.file.bucket_name, 'Key':self.file.key}, Metadata=metadata, MetadataDirective='REPLACE', ACL=self.acl)

    # This is convoluted but AWS SDK does not have a simple
    # exists() method, see: https://stackoverflow.com/questions/33842944
    def exists(self) -> bool:
        try:
            self.file.load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise
        else:
            return True

    def delete(self) -> None:
        self.file.delete()

    def save(self, data: Union[str, bytes], contentType: str) -> None:
        body = bytes(data, 'utf-8') if isinstance(data, str) else data
        self.file.put(Body=data, ContentType=contentType, ACL=self.acl)

    def download(self) -> bytes:
        response = self.file.get()
        return response['Body'].read()

    def signed_url(self, version: str, action: str, expires: int, contentType: str) -> str:
        method = f'{action.lower()}_object'
        params = {
            "Bucket": self.file.Bucket().name,
            "Key": self.name,
            "ResponseContentType": contentType
        }
        return self.client.generate_presigned_url(method, Params=params, ExpiresIn=expires)

# Simple wrapper around GoogleCloudStorage bucket class to provide
# generic bucket storage service for this provider
class AWSStoragePlugin(AbstractStoragePlugin):
    def __init__(self, client, namespace, apiHost, web, credentials):
        super().__init__(client, namespace, apiHost, web, credentials)
        self.bucket = self.client.resource('s3').Bucket(self.bucket_key)

    @staticmethod
    def id() -> str:
        return "@nimbella/storage-s3"

    @staticmethod
    def prepare_creds(credentials: dict) -> dict:
        return credentials['credentials']

    @staticmethod
    def create_client(credentials: dict) ->  botocore.client.BaseClient:
        session = boto3.Session(
            aws_access_key_id=credentials['accessKeyId'],
            aws_secret_access_key=credentials['secretAccessKey'])
        return session

    @property
    def url(self) -> Union[str, None]:
        if self.web:
            if "weburl" in self.credentials:
                return self.credentials["weburl"]
            else:
                hostname = urlparse(self.credentials["endpoint"]).netloc
                return f"http://{self.namespace}-nimbella-io.{hostname}"

    def file(self, destination) -> S3StorageFile:
        return S3StorageFile(self.bucket.Object(destination), self.web, self.client.client('s3'))

    def deleteFiles(self, prefix='') -> None:
        objects = self.bucket.objects.filter(Prefix=prefix)
        keys = list(map(lambda o: {"Key": o.key}, objects))
        if keys:
            self.bucket.delete_objects(Delete={ "Objects": keys })

    def upload(self, path, destination, contentType, cacheControl):
        extraArgs = {
            "ContentType": contentType,
            "CacheControl": cacheControl
        }
        self.bucket.upload_file(path, destination, ExtraArgs=extraArgs)

    def setWebsite(self, mainPageSuffix = None, notFoundPage = None):
        bucket_website = self.bucket.Website()
        website_configuration = {
            'ErrorDocument': {'Key': notFoundPage},
            'IndexDocument': {'Suffix': mainPageSuffix},
        }
        bucket_website.put(WebsiteConfiguration=website_configuration)

    def getFiles(self, prefix = '') -> list:
        objects = self.bucket.objects.filter(Prefix=prefix)
        return list(map(lambda o: S3StorageFile(self.bucket.Object(o.key), self.web, self.client.client('s3')), objects))

    @property
    def bucket_key(self):
        datapart = "" if self.web else "data-"
        return f"{datapart}{self.namespace}-nimbella-io"
