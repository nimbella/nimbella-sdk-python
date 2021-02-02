from .abstract_storage_plugin import AbstractStoragePlugin

class GoogleCloudStoragePlugin(AbstractStoragePlugin):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def id():
        return "@nimbella/storage-gcs"
