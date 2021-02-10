import unittest
from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
from nimbella import storage
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# Generic Storage Plugin API integration test.
# Uses test framework to perform common operations on plugin provider
# instance using external interface.
# The __NIM_STORAGE_KEY environment parameter is used to store credentials
# for storage bucket. This includes a 'provider' field which controls which
# provider plugin is used. These tests should work with any provider.

class TestStoragePlugin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bucket = storage()

    # Reset bucket contents between tests
    def setUp(self):
        self.bucket.deleteFiles()

    def tearDown(self):
        self.bucket.deleteFiles()

    def test_can_add_and_remove_files_in_bucket(self):
        files = {
            'hello.txt' : ('Hello World!', 'text/plain'),
            'hello.json' : ('Hello World!', 'application/json'),
            'hello.bin' : (b'This is some binary bytes', 'application/octet-stream'),
        }
        # create new file in the bucket and check it exists
        for filename, contents in files.items():
            f = self.bucket.file(filename)
            self.assertFalse(f.exists())

            f.save(contents[0], contents[1])
            self.assertTrue(f.exists())

        # all files should now be in the bucket
        filenames = list(map(lambda f: f.name, self.bucket.getFiles()))
        self.assertEqual(sorted(filenames), sorted(list(files.keys())))

        # check each file contents matches & then delete
        for filename, contents in files.items():
            f = self.bucket.file(filename)
            if isinstance(contents[0], str):
                self.assertEqual(f.download(), bytes(contents[0], 'utf-8'))
            else:
                self.assertEqual(f.download(), contents[0])
            f.delete()
            self.assertFalse(f.exists())

    def test_upload_from_file(self):
        f = NamedTemporaryFile()
        contents = b"Hello world!\n"
        destination = "hello_world.txt" 
        f.write(contents)
        f.flush()

        bf = self.bucket.file(destination)
        self.assertFalse(bf.exists())

        self.bucket.upload(f.name, destination, "text/plain", '')
        self.assertTrue(bf.exists())
        self.assertEqual(bf.download(), contents)

    def test_can_generate_signedurl_for_file(self):
        filename = 'hello.txt'
        contents = "Hello world!\n"
        f = self.bucket.file(filename)

        f.save(contents, 'text/plain')
        expires = datetime.now() + timedelta(seconds=86400)
        method = "GET"

        url = f.signed_url("v4", method, expires, "text/plain")
        try: 
            req = Request(url)
            req.add_header('Content-Type', 'text/plain')
            resp = urlopen(req)
        except HTTPError as error:
            data = error.read()
            print(data)

    # This feature of the plugin is not workign yet....
    def test_can_configure_website_for_bucket(self):
        pass
