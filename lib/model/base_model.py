from abc import (
    ABCMeta,
    abstractmethod
)


from lib.utils.misc import load_config


class BaseModel(object):

    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        self.root_config = load_config()
        self.model_config = load_config()['model']

    @abstractmethod
    def fit(self):
        raise NotImplementedError

    @abstractmethod
    def verification(self):
        raise NotImplementedError

    @abstractmethod
    def predict(self, **kwargs):
        raise NotImplementedError

