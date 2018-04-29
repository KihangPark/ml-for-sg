from abc import (
    ABCMeta,
    abstractmethod
)


from lib.utils.misc import load_config


class BaseSourceGenerator(object):
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        self.root_config = load_config()
        self.generator_config = load_config()['source_generator']

    @abstractmethod
    def generate_input_data(self, **kwargs):
        raise NotImplementedError


