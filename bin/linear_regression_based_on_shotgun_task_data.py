import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_dir, '..'))

from lib.shotgun.task import SGTaskManager
from lib.machine_learning.data_generator import DataGenerator

sg_task_manager = SGTaskManager()
all_feature = sg_task_manager.get_all_feature_from_task()

print 'get_all_feature_from_task finished.'

data_generator = DataGenerator()
df = data_generator.generate_data_from_task(all_feature[:200])
