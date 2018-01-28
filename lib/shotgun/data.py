from lib.utils.utils import load_sg_data_config
from lib.shotgun.utils import get_shotgun_handler


class SGDataManager(object):

    def __init__(self):

        self.sg_handler = get_shotgun_handler()
        self.sg_data_config = load_sg_data_config()
        self.target_schema = self.sg_data_config['target_schema']
        self.keyword_config = self.sg_data_config['keyword']
        self.value_config = self.sg_data_config['value']
        self.text_config = self.sg_data_config['text']
        self.cost = self.sg_data_config['cost']

    def get_target_list(self):

        schema_field_list = self.sg_handler.schema_field_read(self.target_schema)
        target_list = self.sg_handler.find(self.target_schema, [], schema_field_list.keys())

        valid_task_list = []
        for target in target_list:
            if not target['project']:
                continue
            valid_task_list.append(target)

        return valid_task_list

    def get_field_value(self, target, feature_list):

        feature_dict = dict()
        for feature in feature_list:
            if isinstance(target[feature], list):
                for field in target[feature]:
                    feature_dict.update({feature: field['name']})
            else:
                feature_dict.update({feature: target[feature]})
        return feature_dict

    def get_data(self):

        self.keyword_config = self.sg_data_config['keyword']
        self.value_config = self.sg_data_config['value']
        self.text_config = self.sg_data_config['text']
        self.cost = self.sg_data_config['cost']

        # get target list
        target_list = self.get_target_list()

        target_data_list = []
        for target in target_list[:300]:

            # get text feature
            text_feature_list = self.text_config['feature_list']

            # get cost feature
            cost = target[self.cost]

            text_feature_dict = dict()
            text_feature_dict.update(self.get_field_value(target, text_feature_list))

            # get keyword feature
            keyword_feature_dict = dict()

            # get value feature
            value_feature_dict = dict()

            data = {
                'id': target['id'],
                'feature_dict': {
                    'text_feature': text_feature_dict,
                    'keyword_feature': keyword_feature_dict,
                    'value_feature': value_feature_dict
                },
                'cost': cost
            }

            target_data_list.append(data)

        return target_data_list
