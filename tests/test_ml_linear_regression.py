import unittest
from lib.ml.core import MLCore

from .fixtures.mocked_shotgun_core import SG_DATA_SAMPLE


class TestMLCore(unittest.TestCase):

    def setUp(self):
        ml_core = MLCore(SG_DATA_SAMPLE)

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
