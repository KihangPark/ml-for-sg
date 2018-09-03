from abc import (
    ABCMeta,
    abstractmethod
)


from lib.utils.misc import load_config
from lib.resource.resource_handler import ResourceHandler


class BaseModel(object):

    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        self.root_config = load_config()
        self.model_config = load_config()['model']
        self._resource_handler = ResourceHandler()

    @abstractmethod
    def fit(self, feature, cost):
        raise NotImplementedError

    @abstractmethod
    def verification(self):
        raise NotImplementedError

    @abstractmethod
    def predict(self, **kwargs):
        raise NotImplementedError
