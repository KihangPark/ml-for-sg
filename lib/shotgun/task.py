from lib.shotgun.shotgun_utils import get_shotgun_handler
from lib.utils.utils import load_config


class SGTaskManager(object):

    def __init__(self):
        self.sg_handler = get_shotgun_handler()
        self.sg_config = load_config()['shotgun']

    def get_all_task(self):

        task_field_list = self.sg_handler.schema_field_read('Task')
        print 'task collect started.'
        task_list = self.sg_handler.find('Task', [], task_field_list.keys())
        print 'task collect finished.'

        valid_task_list = list()
        for task in task_list:
            if task['project']:
                valid_task_list.append(task)

        return valid_task_list

    def get_all_feature_from_task(self):

        sg_feature_list = self.sg_config['feature_list']
        cost = self.sg_config['cost']
        task_list = self.get_all_task()

        task_data_list = list()

        index = 0
        for task in task_list[:300]:
            index = index + 1
            print 'task count : ' + str(index)

            feature_list = list()
            for feature_field in sg_feature_list:
                print task
                print task[feature_field]
                if isinstance(task[feature_field], list):
                    for field in task[feature_field]:
                        feature_list.append(field['name'])
                else:
                    feature_list.extend(task[feature_field].split(' '))

            task_data = {
                'id': task['id'],
                'feature_list': set(feature_list),
                'cost': task[cost]
            }

            task_data_list.append(task_data)

        return task_data_list
