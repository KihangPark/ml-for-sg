import pandas as pd
from collections import defaultdict
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer


from lib.resource.resource_handler import ResourceHandler
from lib.source_generator.shotgun.utils import get_shotgun_handler
from lib.source_generator.base_source_generator import BaseSourceGenerator
# TODO: replace real data.
#import sys
#print sys.path
#from tests.fixtures.mocked_shotgun_data import MOCKED_SHOT_BASE_GENERATED_SOURCE


class ShotgunSourceGenerator(BaseSourceGenerator):

    def __init__(self):

        super(ShotgunSourceGenerator, self).__init__()

        self.handler = get_shotgun_handler(self.root_config)
        if not self.handler:
            raise Exception('Shotgun server connection fails.')
        self.data_config = self.generator_config['shotgun']['data']
        #self.keyword = self.data_config['keyword']
        #self.value = self.data_config['value']
        self.text = self.data_config['text']
        self.cost = self.data_config['cost']
        self.source_schema = self.data_config['source_schema']
        self.skip_features = self.data_config['skip_features']
        self.resource_handler = ResourceHandler()

    def generate_source_data(self, project_id, limit=0):

        '''
        # Get raw source.
        raw_source = self.get_raw_source()

        # Reformat raw source.
        panda_data = self.convert_raw_source_to_panda_data(raw_source)

        return panda_data
        '''
        raw_data = self._get_raw_data(project_id, limit)
        modified_raw_data = self._reformat_raw_data(raw_data)
        panda_data = self._convert_raw_to_source_data(modified_raw_data)
        return panda_data


    def _get_raw_data(self, project_id, limit=0):
        limit = 3

        # Generate filter for project.
        if project_id:
            filters = [[
                'project', 'is', {
                    'type': 'Project',
                    'id': project_id}
            ]]
        else:
            return []

        # Get source data from shotgun.
        schema_field_list = self.handler.schema_field_read(self.source_schema)
        sources = self.handler.find(
            self.source_schema,
            filters,
            schema_field_list.keys(),
            limit=limit
        )

        valid_sources = []
        for source in sources:
            # Filter out improper project source.
            if not source['project']:
                continue
            valid_sources.append(source)

        return valid_sources

    def _reformat_raw_data(self, raw_data):
        modified_raw_data = dict()
        schema_field_list = self.handler.schema_field_read('Task')

        for raw_datum in raw_data:

            task_sources = []
            cost_feature = 0
            text_feature = {}
            for task in raw_datum['tasks']:
                filters = [
                    [
                        'project', 'is', {'type': 'Project', 'id': raw_datum['project']['id']}
                    ], [
                        'id', 'is', task['id']
                    ]
                ]
                task_source = self.handler.find(
                    'Task',
                    filters,
                    schema_field_list.keys(),
                    limit=1
                )[0]

                # Get cost feature.
                cost_feature = cost_feature + task_source[self.cost]

            # Get text feature dict.
            text_features, value_features = self._get_field_data(raw_datum, self.text['feature_list'])

            modified_raw_data.update({
                raw_datum['code']: {
                'id': raw_datum['id'],
                'feature_dict': {
                    'text_features': text_features,
                    'value_features': value_features
                },
                'cost': cost_feature}}
            )

        return modified_raw_data

    def _convert_raw_to_source_data(self, modified_raw_data):

        value_columns = self._generate_value_column_data(modified_raw_data)
        text_columns = self._generate_text_column_data(modified_raw_data)

        df_y_full = self._generate_cost_panda_data(modified_raw_data)
        panda_data = self._generate_feature_panda_data(modified_raw_data, value_columns, text_columns)
        df_x_full = panda_data['df_x']
        df_x_text_full = panda_data['df_x_text']
        return {
            'df_x_full': df_x_full,
            'df_x_text_full': df_x_text_full,
            'df_y_full': df_y_full
        }

    def _generate_feature_panda_data(self, modified_raw_data, value_columns, text_columns):

        heatmap = []
        df_x_full = None
        text_feature_index = []
        value_feature_index = []
        # text_feature_values = []
        # print value_columns
        for _, shot_values in modified_raw_data.iteritems():
            for column, _ in shot_values['feature_dict']['value_features'].iteritems():
                if value_columns[column] is None:
                    value_feature_index.append(column)
                else:
                    for value in value_columns[column]:
                        value_feature_index.append('{}__{}'.format(column, value))

                        # text_feature_values = value['feature_dict']['text_features']
                        # value_feature_values = value['feature_dict']['value_features']

        value_feature_index = sorted(set(value_feature_index))
        text_feature_index = sorted(set(text_columns))

        df_x_values = []
        df_x_text_values = []
        value_feature_values = []
        text_feature_values = []
        cost_values = []

        for shot_name, shot_datum in modified_raw_data.iteritems():
            value_feature_values = []
            cost_values.append(shot_datum['cost'])
            for value_feature in value_feature_index:
                if '__' in value_feature:
                    column = value_feature.split('__')[0]
                    sub_column = value_feature.split('__')[1]
                    value_feature_values.append(
                        1 if sub_column in shot_datum['feature_dict']['value_features'][column] else 0)
                else:
                    value_feature_values.append(shot_datum['feature_dict']['value_features'][value_feature])
            df_x_values.append(value_feature_values)
        for shot_name, shot_datum in modified_raw_data.iteritems():
            text_feature_values = []
            for text_feature in text_feature_index:
                result = 0
                for key, value in shot_datum['feature_dict']['text_features'].iteritems():
                    if text_feature in value:
                        result = 1
                        break
                text_feature_values.append(result)
            df_x_text_values.append(text_feature_values)
        print value_feature_index
        print df_x_values
        df_x = pd.DataFrame(df_x_values, index=modified_raw_data.keys(), columns=value_feature_index)
        df_y = pd.DataFrame(cost_values, index=modified_raw_data.keys(), columns=['cost'])
        df_x_text = pd.DataFrame(df_x_text_values, index=modified_raw_data.keys(), columns=text_feature_index)
        print df_x
        print df_y
        print df_x_text
        return {'df_x': df_x, 'df_x_text': df_x_text}

    def _get_field_data(self, raw_data, text_features):

        text_feature_dict = dict()
        value_feature_dict = dict()
        for feature in raw_data.keys():
            if feature in self.skip_features:
                continue
            if feature in text_features:
                target_feature_dict = text_feature_dict
            else:
                target_feature_dict = value_feature_dict
            if isinstance(raw_data[feature], list):
                list_value = []
                for value in raw_data[feature]:
                    if isinstance(value, dict):
                        list_value.append(value['name'])
                    else:
                        list_value.append(value)
                if list_value and isinstance(list_value[0], str):
                    target_feature_dict.update({feature: self._get_word_list(','.join(list_value))})
                if list_value and (isinstance(list_value[0], int) or isinstance(list_value[0], float)):
                    target_feature_dict.update({feature: sum(list_value)})
            elif isinstance(raw_data[feature], dict):
                target_feature_dict[feature] = raw_data[feature]['name']
            else:
                if feature in text_features:
                    target_feature_dict.update({feature: self._get_word_list(raw_data[feature])})
                else:
                    target_feature_dict.update({feature: raw_data[feature]})
        return text_feature_dict, value_feature_dict

    def _get_word_list(self, text):
        count_vectorizer = CountVectorizer()
        count_vectorizer.fit_transform([text])
        feature_names = count_vectorizer.get_feature_names()
        return ','.join(feature_names)
    '''
    def convert_raw_data_to_panda_source(self, raw_data):
        #source = MOCKED_SHOT_BASE_GENERATED_SOURCE

        value_column_data = self.generate_value_column_data(raw_data)
        text_column_data = self.generate_text_column_data(raw_data)
        df_y_full = self.generate_cost_data(raw_data)
        df_x_full, heatmap = self.generate_feature_data(raw_data, column_data, df_y_full)
        df_all = pd.concat([df_x_full, df_y_full], axis=1)

        self.heatmap = heatmap

        return {'df_x_full': df_x_full, 'df_y_full': df_y_full}
    '''

    def _generate_value_column_data(self, raw_data):

        column_data = defaultdict(list)
        # Collect all list value.
        for _, raw_datum in raw_data.iteritems():
            for key, value in raw_datum['feature_dict']['value_features'].iteritems():
                if (type(value) == str or type(value) == unicode) and ',' in value:
                    column_data[key].extend(value.split(','))
                else:
                    column_data[key] = None
        # Remove duplicated list from column_data.
        for _, value in column_data.iteritems():
            if type(value) == list:
                column_data[_] = sorted(set(value))

        return column_data

    def _generate_text_column_data(self, raw_data):

        columns = []
        for _, raw_datum in raw_data.iteritems():
            for key, value in raw_datum['feature_dict']['text_features'].iteritems():
                if value is not None:
                    columns.extend([x.strip() for x in value.split(',')])

        return sorted(set(columns))

    def _generate_cost_panda_data(self, modified_raw_data):

        indexes = []
        source_costs = []
        for key in sorted(modified_raw_data):
            indexes.append(key)
            source_costs.append(modified_raw_data[key]['cost'])

        return pd.DataFrame(source_costs, index=indexes, columns=['cost'])

    '''
    def generate_feature_data(self, source, column_data, df_y_full):

        heatmap = []
        df_x_full = None
        for column, column_values in column_data.iteritems():
            if column == 'cost':
                continue
            indexes = []
            values = []
            if not column_values:
                # Column value does not contains string list.
                for key in sorted(source):
                    single_source = source[key]
                    indexes.append(key)
                    if column in single_source.keys():
                        values.append(single_source[column])
                    else:
                        values.append(0)
                df_x = pd.DataFrame(values, index=indexes, columns=[column])
                df_x_full = pd.concat([df_x_full, df_x], axis=1)
            else:
                # Column value contains string list.
                for key in sorted(source):
                    single_source = source[key]
                    if single_source.has_key(column):
                        if ',' in str(single_source[column]):
                            single_source_column_values = [x.strip() for x in single_source[column].split(',')]
                        else:
                            single_source_column_values = [single_source[column]]
                    else:
                        single_source_column_values = []
                    indexes.append(key)
                    source_values = []
                    for column_value in column_values:
                        if column_value in single_source_column_values:
                            source_values.append(1)
                        else:
                            source_values.append(0)
                    values.append(source_values)
                df_x = pd.DataFrame(values, index=indexes, columns=column_values)
                df_x_full = pd.concat([df_x_full, df_x], axis=1)
            # Generate single pair data frame for calculating heatmap.
            df_single = pd.concat([df_x, df_y_full], axis=1)
            heatmap.append((column, df_single, df_single.corr()))

        return df_x_full, heatmap
    '''

