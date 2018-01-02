import unittest

from lib.shotgun.task import SGTaskManager


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.sg_task_manager = SGTaskManager()

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
