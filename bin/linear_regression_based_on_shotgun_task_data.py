import os
import sys

root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(root_dir)
os.environ['ML_FOR_SG_ROOT'] = root_dir

from lib.source_generator.shotgun.source_generator import ShotgunSourceGenerator

# Create shotgun data manager.
shotgun_source_generator = ShotgunSourceGenerator()
raw_data = shotgun_source_generator.get_raw_data(70, 3)
shot_data = shotgun_source_generator.reformat_raw_shot_data(raw_data)
value_columns = shotgun_source_generator.generate_value_column_data(shot_data)
text_columns = shotgun_source_generator.generate_text_column_data(shot_data)
df_y_full = shotgun_source_generator.generate_cost_data(shot_data)


'''
from lib.shotgun.task import SGTaskManager
from lib.machine_learning.data_generator import DataGenerator

sg_task_manager = SGTaskManager()
all_feature = sg_task_manager.get_all_feature_from_task()

print 'get_all_feature_from_task finished.'

data_generator = DataGenerator()
df = data_generator.generate_data_from_task(all_feature[:200])
'''
