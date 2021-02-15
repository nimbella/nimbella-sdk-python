from nimbella.storage import plugin_manager

import unittest

class TestPluginManager(unittest.TestCase):
    def test_finds_google_storage_plugin(self):
        id = "@nimbella/storage-gcs"
        plugin = plugin_manager.find_plugin(id)
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.id(), id)

    def test_finds_aws_storage_plugin(self):
        id = "@nimbella/storage-s3"
        plugin = plugin_manager.find_plugin(id)
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.id(), id)


    def test_does_not_find_missing_plugin(self):
        id = "@nimbella/storage-missing"
        plugin = plugin_manager.find_plugin(id)
        self.assertIsNone(plugin)
