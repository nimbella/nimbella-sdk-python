from nimbella.storage.plugins.aws_storage_plugin import AWSStoragePlugin, S3StorageFile


import unittest
from unittest.mock import MagicMock
from unittest.mock import patch, mock_open
from types import SimpleNamespace

class TestAWSStoragePlugin(unittest.TestCase):
    def test_aws_storage_plugin_id(self):
        id = "@nimbella/storage-aws"
        self.assertEqual(AWSStoragePlugin.id(), id)

    def test_constructor(self):
        client = MagicMock()
        aws = AWSStoragePlugin(client, '', '', '', '')
        client.Bucket.assert_called_with(aws.bucket_key)

    def test_bucket_key_property(self):
        client = MagicMock()
        namespace = 'this-is-a-namespace'
        apiHost = 'https://this.is.a.host.com'

        # test bucket keys for web buckets
        web = True
        aws = AWSStoragePlugin(client, namespace, apiHost, web, '')
        self.assertEqual(aws.bucket_key, f'{namespace}-this-is-a-host-com')

        # test bucket keys for data buckets
        aws.web = False
        self.assertEqual(aws.bucket_key, f'data-{namespace}-this-is-a-host-com')

    def test_bucket_url(self):
        # test happy path using bucket location in creds
        client = MagicMock()
        namespace = 'this-is-a-namespace'
        apiHost = 'https://this.is.a.host.com'
        bucketHost = 'bucket.host.com'
        credentials = {
            "endpoint": f'https://{bucketHost}' 
        }

        aws = AWSStoragePlugin(client, namespace, apiHost, True, credentials)
        self.assertEqual(aws.url, f'http://{namespace}-nimbella-io.{bucketHost}')

        # Test bucket credentials contain weburl
        weburl = "http://some_other_address.com"
        aws.credentials["weburl"] = weburl
        self.assertEqual(aws.url, weburl)

        # Data storage buckets should not return a URL
        aws.web = False
        self.assertEqual(aws.url, None)

    def test_bucket_delete_files(self):
        prefix = "folder/"
        Contents = [
            { "Key": "folder/a-file" },
            { "Key": "folder/b-file" },
            { "Key": "folder/c-file" }
        ]
        client = MagicMock()
        client.list_objects_v2 = MagicMock(return_value={ "Contents": Contents })

        aws = AWSStoragePlugin(client, '', '', True, '')
        aws.bucket.delete_objects = MagicMock()

        aws.deleteFiles(prefix)

        client.list_objects_v2.assert_called_with(Bucket=aws.bucket_key, Prefix=prefix)
        aws.bucket.delete_objects.assert_called_with(Delete={
            "Objects": Contents
        })

    def test_bucket_get_files(self):
        client = MagicMock()
        prefix = "folder/"
        Contents = [
            { "Key": "folder/a-file" },
            { "Key": "folder/b-file" },
            { "Key": "folder/c-file" }
        ]
        keys = list(map(lambda f: f.get('Key'), Contents))
        aws = AWSStoragePlugin(client, '', '', True, '')

        client.list_objects_v2 = MagicMock(return_value={ "Contents": Contents })
        aws.bucket.Object = MagicMock(side_effect=lambda key: SimpleNamespace(key=key))

        files = aws.getFiles(prefix)
        files_keys = list(map(lambda f: f.name, files))
        self.assertEqual(files_keys, keys)
        client.list_objects_v2.assert_called_with(Bucket=aws.bucket_key, Prefix=prefix)

    def test_bucket_get_file(self):
        client = MagicMock()
        destination = 'folder/file.txt'
        obj = SimpleNamespace(key=destination)
        aws = AWSStoragePlugin(client, '', '', True, '')
        aws.bucket.Object = MagicMock(return_value=obj)

        self.assertEqual(aws.file(destination).name, destination)
        aws.bucket.Object.assert_called_with(destination)

    '''
    def test_bucket_set_website(self):
        client = MagicMock()
        aws = AWSStoragePlugin(client, '', '', True, '')
        mainPageSuffix = "index.html"
        notFoundPage = "404.html"
        aws.bucket.configure_website = MagicMock()
        aws.setWebsite(mainPageSuffix, notFoundPage)
        aws.bucket.configure_website.assert_called_with(mainPageSuffix, notFoundPage)

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_bucket_upload(self, mock_file):
        client = MagicMock()
        aws = AWSStoragePlugin(client, '', '', True, '')
        path = '/file/path.txt'
        destination = 'folder/path.txt'
        contentType = 'text/plain'
        cacheControl = 'no-cache'

        blob = Blob(name=destination, bucket='some-bucket')
        aws = AWSStoragePlugin(client, '', '', True, '')
        aws.bucket.blob = MagicMock(return_value=blob)
        blob.upload_from_file = MagicMock()
        aws.upload(path, destination, contentType, cacheControl)
        aws.bucket.blob.assert_called_with(destination)
        blob.upload_from_file.assert_called_with(file_obj=mock_file(path, 'rb'), content_type=contentType)
        mock_file.assert_called_with(path, 'rb')

'''

