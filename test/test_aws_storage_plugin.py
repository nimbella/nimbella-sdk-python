from nimbella.storage.plugins.aws_storage_plugin import AWSStoragePlugin, S3StorageFile


import unittest
from unittest.mock import MagicMock
from unittest.mock import patch, mock_open
from types import SimpleNamespace

class TestAWSStoragePlugin(unittest.TestCase):
    def test_aws_storage_plugin_id(self):
        id = "@nimbella/storage-s3"
        self.assertEqual(AWSStoragePlugin.id(), id)

    def test_constructor(self):
        client = MagicMock()
        client.resource = MagicMock(return_value=MagicMock())
        aws = AWSStoragePlugin(client, '', '', '', {})
        client.resource.assert_called_with('s3', endpoint_url=None)
        client.resource().Bucket.assert_called_with(aws.bucket_key)

    def test_constructor_with_endpoint(self):
        client = MagicMock()
        client.resource = MagicMock(return_value=MagicMock())
        endpoint = "https://some.host.com"
        aws = AWSStoragePlugin(client, '', '', '', { "endpoint": endpoint })
        client.resource.assert_called_with('s3', endpoint_url=endpoint)
        client.resource().Bucket.assert_called_with(aws.bucket_key)

    def test_bucket_key_property(self):
        client = MagicMock()
        namespace = 'this-is-a-namespace'
        apiHost = 'https://this.is.a.host.com'
        deployment = 'this'

        # test bucket keys for web buckets
        web = True
        aws = AWSStoragePlugin(client, namespace, apiHost, web, {})
        self.assertEqual(aws.bucket_key, f'{namespace}-{deployment}-nimbella-io')

        # test bucket keys for data buckets
        aws.web = False
        self.assertEqual(aws.bucket_key, f'data-{namespace}-{deployment}-nimbella-io')

    def test_bucket_url(self):
        # test happy path using bucket location in creds
        client = MagicMock()
        namespace = 'this-is-a-namespace'
        apiHost = 'https://this.is.a.host.com'
        deployment = 'this'
        bucketHost = 'bucket.host.com'
        credentials = {
            "endpoint": f'https://{bucketHost}' 
        }

        aws = AWSStoragePlugin(client, namespace, apiHost, True, credentials)
        self.assertEqual(aws.url, f'http://{namespace}-{deployment}-nimbella-io.{bucketHost}')

        # Test bucket credentials contain weburl
        weburl = "http://some_other_address.com"
        aws.credentials["weburl"] = weburl
        self.assertEqual(aws.url, weburl)

        # Data storage buckets should not return a URL
        aws.web = False
        self.assertEqual(aws.url, None)

    def test_bucket_delete_files(self):
        prefix = "folder/"
        files = [
            SimpleNamespace(key="folder/a-file"),
            SimpleNamespace(key="folder/b-file"),
            SimpleNamespace(key="folder/c-file"),
        ]
        keys = list(map(lambda f: f.key, files))

        client = MagicMock()

        aws = AWSStoragePlugin(client, '', '', True, {})
        aws.bucket.delete_objects = MagicMock()
        aws.bucket.objects.filter = MagicMock(return_value=files)
        aws.bucket.Object = MagicMock(side_effect=lambda key: SimpleNamespace(key=key))

        aws.deleteFiles(prefix)

        aws.bucket.delete_objects.assert_called_with(Delete={
            "Objects": list(map(lambda o: {"Key": o.key}, files))
        })
        aws.bucket.objects.filter.assert_called_with(Prefix=prefix)

    def test_bucket_get_files(self):
        client = MagicMock()
        prefix = "folder/"
        files = [
            SimpleNamespace(key="folder/a-file"),
            SimpleNamespace(key="folder/b-file"),
            SimpleNamespace(key="folder/c-file"),
        ]
        keys = list(map(lambda f: f.key, files))
        aws = AWSStoragePlugin(client, '', '', True, {})

        aws.bucket.objects.filter = MagicMock(return_value=files)
        aws.bucket.Object = MagicMock(side_effect=lambda key: SimpleNamespace(key=key))

        files = aws.getFiles(prefix)
        files_keys = list(map(lambda f: f.name, files))
        self.assertEqual(files_keys, keys)
        aws.bucket.objects.filter.assert_called_with(Prefix=prefix)

    def test_bucket_get_file(self):
        client = MagicMock()
        destination = 'folder/file.txt'
        obj = SimpleNamespace(key=destination)
        aws = AWSStoragePlugin(client, '', '', True, {})
        aws.bucket.Object = MagicMock(return_value=obj)

        self.assertEqual(aws.file(destination).name, destination)
        aws.bucket.Object.assert_called_with(destination)

    def test_bucket_set_website(self):
        client = MagicMock()
        aws = AWSStoragePlugin(client, '', '', True, {})
        mainPageSuffix = "index.html"
        notFoundPage = "404.html"
        website = MagicMock()
        aws.bucket.Website = MagicMock(return_value = website)
        WebsiteConfiguration = {
            'ErrorDocument': {'Key': notFoundPage},
            'IndexDocument': {'Suffix': mainPageSuffix},
        }
        aws.setWebsite(mainPageSuffix, notFoundPage)
        website.put.assert_called_with(WebsiteConfiguration=WebsiteConfiguration)

    def test_bucket_upload(self):
        client = MagicMock()
        aws = AWSStoragePlugin(client, '', '', True, {})
        path = '/file/path.txt'
        destination = 'folder/path.txt'
        contentType = 'text/plain'
        cacheControl = 'no-cache'
        extraArgs = {
            "ContentType": contentType,
            "CacheControl": cacheControl
        }

        aws.bucket.upload_file = MagicMock()

        aws.upload(path, destination, contentType, cacheControl)
        aws.bucket.upload_file.assert_called_with(path, destination, ExtraArgs=extraArgs)

    def test_file_signedurl_get(self):
        presigned_url = "https://some-url.com/"
        client = MagicMock()
        client.generate_presigned_url.return_value = presigned_url
        destination = 'file.txt'
        version = 'v4'
        action = 'get'
        bucket = 'my-bucket'
        expires = 3600
        contentType = 'text/plain'
        s3_file = SimpleNamespace(key=destination, Bucket=lambda: SimpleNamespace(name=bucket))
        file = S3StorageFile(s3_file, False, client)

        url = file.signed_url(version=version, action=action, expires=expires, contentType=contentType)
        self.assertEqual(url, presigned_url)
        client.generate_presigned_url.assert_called_with('get_object', Params={'Bucket': bucket, 
            'Key': destination, 'ResponseContentType': contentType}, ExpiresIn=expires)


    def test_file_signedurl_put(self):
        presigned_url = "https://some-url.com/"
        client = MagicMock()
        client.generate_presigned_url.return_value = presigned_url
        destination = 'file.txt'
        version = 'v4'
        action = 'put'
        bucket = 'my-bucket'
        expires = 3600
        contentType = 'text/plain'
        s3_file = SimpleNamespace(key=destination, Bucket=lambda: SimpleNamespace(name=bucket))
        file = S3StorageFile(s3_file, False, client)

        url = file.signed_url(version=version, action=action, expires=expires, contentType=contentType)
        self.assertEqual(url, presigned_url)
        client.generate_presigned_url.assert_called_with('put_object', Params={'Bucket': bucket, 
            'Key': destination, 'ContentType': contentType}, ExpiresIn=expires)
