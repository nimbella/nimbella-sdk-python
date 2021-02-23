from nimbella.storage.plugins.gcs_storage_plugin import GoogleCloudStoragePlugin, GoogleCloudStorageFile

import unittest
from unittest.mock import MagicMock
from unittest.mock import patch, mock_open

from google.cloud.storage.blob import Blob

class TestGoogleCloudStoragePlugin(unittest.TestCase):
    def test_google_storage_plugin_id(self):
        id = "@nimbella/storage-gcs"
        self.assertEqual(GoogleCloudStoragePlugin.id(), id)

    def test_constructor(self):
        client = MagicMock()
        gcs = GoogleCloudStoragePlugin(client, '', '', '', '')
        client.get_bucket.assert_called_with(gcs.bucket_key)

    def test_bucket_key_property(self):
        client = MagicMock()
        namespace = 'this-is-a-namespace'
        apiHost = 'https://this.is.a.host.com'

        # test bucket keys for web buckets
        web = True
        gcs = GoogleCloudStoragePlugin(client, namespace, apiHost, web, '')
        self.assertEqual(gcs.bucket_key, f'{namespace}-this-is-a-host-com')

        # test bucket keys for data buckets
        gcs.web = False
        self.assertEqual(gcs.bucket_key, f'data-{namespace}-this-is-a-host-com')

    def test_bucket_url(self):
        client = MagicMock()
        namespace = 'this-is-a-namespace'
        apiHost = 'https://this.is.a.host.com'

        gcs = GoogleCloudStoragePlugin(client, namespace, apiHost, True, '')
        self.assertEqual(gcs.url, f'https://{namespace}-this-is-a-host-com')

        # Data storage buckets should not return a URL
        gcs.web = False
        self.assertEqual(gcs.url, None)

    def test_bucket_delete_files(self):
        prefix = 'folder/'
        blobs = [
            Blob(name='folder/a-file', bucket='some-bucket'),
            Blob(name='folder/b-file', bucket='some-bucket'),
            Blob(name='folder/c-file', bucket='some-bucket')
        ]
        client = MagicMock()
        client.list_blobs = MagicMock(return_value=iter(blobs))

        gcs = GoogleCloudStoragePlugin(client, '', '', True, '')
        gcs.bucket.delete_blobs = MagicMock()

        gcs.deleteFiles(prefix)

        client.list_blobs.assert_called_with(gcs.bucket, prefix=prefix)
        gcs.bucket.delete_blobs.assert_called_with(blobs)

    def test_bucket_get_files(self):
        client = MagicMock()
        blobs = [
            Blob(name='folder/a-file', bucket='some-bucket'),
            Blob(name='folder/b-file', bucket='some-bucket'),
            Blob(name='folder/c-file', bucket='some-bucket')
        ]
        client.list_blobs = MagicMock(return_value=iter(blobs))
        gcs = GoogleCloudStoragePlugin(client, '', '', True, '')
        prefix = 'folder/'
        files = list(gcs.getFiles(prefix))
        file_blobs = list(map(lambda f: f.blob, files))
        self.assertEqual(file_blobs, blobs)
        client.list_blobs.assert_called_with(gcs.bucket, prefix=prefix)

    def test_bucket_get_file(self):
        client = MagicMock()
        destination = 'folder/file.txt'
        blob = Blob(name=destination, bucket='some-bucket')
        gcs = GoogleCloudStoragePlugin(client, '', '', True, '')
        gcs.bucket.blob = MagicMock(return_value=blob)
        self.assertEqual(gcs.file(destination).blob, blob)
        gcs.bucket.blob.assert_called_with(destination)

    def test_bucket_set_website(self):
        client = MagicMock()
        gcs = GoogleCloudStoragePlugin(client, '', '', True, '')
        mainPageSuffix = "index.html"
        notFoundPage = "404.html"
        gcs.bucket.configure_website = MagicMock()
        gcs.setWebsite(mainPageSuffix, notFoundPage)
        gcs.bucket.configure_website.assert_called_with(mainPageSuffix, notFoundPage)

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_bucket_upload(self, mock_file):
        client = MagicMock()
        gcs = GoogleCloudStoragePlugin(client, '', '', True, '')
        path = '/file/path.txt'
        destination = 'folder/path.txt'
        contentType = 'text/plain'
        cacheControl = 'no-cache'

        blob = Blob(name=destination, bucket='some-bucket')
        gcs = GoogleCloudStoragePlugin(client, '', '', True, '')
        gcs.bucket.blob = MagicMock(return_value=blob)
        blob.upload_from_file = MagicMock()
        gcs.upload(path, destination, contentType, cacheControl)
        gcs.bucket.blob.assert_called_with(destination)
        blob.upload_from_file.assert_called_with(file_obj=mock_file(path, 'rb'), content_type=contentType)
        mock_file.assert_called_with(path, 'rb')


