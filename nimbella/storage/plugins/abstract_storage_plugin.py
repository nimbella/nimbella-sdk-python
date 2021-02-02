import abc

class AbstractStoragePlugin(abc.ABC):
    @abc.abstractmethod
    def __init__(self, namespace, apiHost, web, credentials):
        pass

    @staticmethod
    @abc.abstractmethod
    def id():
        pass
