import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


from lib.source_generator.shotgun.utils import get_shotgun_handler
from lib.source_generator.base_source_generator import BaseSourceGenerator
# TODO: replace real data.
from tests.fixtures.mocked_shotgun_data import MOCKED_SHOT_BASE_GENERATED_SOURCE


class ShotgunSourceGenerator(BaseSourceGenerator):

    def __init__(self):

        super(ShotgunSourceGenerator, self).__init__()

        self.handler = get_shotgun_handler(self.root_config)
        if not self.handler:
            raise Exception('shotgun connection failed.')
        self.data_config = self.generator_config['shotgun']['data']
        self.source_schema = self.data_config['source_schema']
        self.keyword = self.data_config['keyword']
        self.value = self.data_config['value']
        self.text = self.data_config['text']
        self.cost = self.data_config['cost']
        self.skip_feature_list = self.data_config['skip_feature_list']

    def generate_input_data(self):

        # Get raw source.
        raw_source = self.get_raw_source()

        # Reformat raw source.
        panda_data = self.convert_raw_source_to_panda_data(raw_source)

        return panda_data

    def get_raw_source(self, project_id, limit=100):

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

    def convert_raw_source_to_panda_data(self, raw_source):

        source = self.reformat_raw_source(raw_source)
        panda_data = self.convert_raw_source_to_panda_data(source)

        return panda_data

    def reformat_raw_source(self, raw_source):

        source = []
        for single_raw_source in raw_source:

            # Get cost feature.
            cost_feature = single_raw_source[self.cost]

            # Get text feature dict.
            text_feature_dict = self.get_field_data(single_raw_source, self.text['feature_list'])

            # get keyword feature
            keyword_feature_dict = dict()

            # get value feature
            value_feature_dict = dict()

            source.append({
                'id': single_raw_source['id'],
                'feature_dict': {
                    'text_feature': text_feature_dict,
                    'keyword_feature': keyword_feature_dict,
                    'value_feature': value_feature_dict
                },
                'cost': cost_feature})

        return source

    def get_field_data(self, single_raw_source, feature_list):

        feature_dict = dict()
        for feature in feature_list:
            if isinstance(single_raw_source[feature], list):
                for field in single_raw_source[feature]:
                    feature_dict.update({feature: field['name']})
            else:
                feature_dict.update({feature: single_raw_source[feature]})
        return feature_dict

    def convert_source_to_panda_data(self, source):
        source = MOCKED_SHOT_BASE_GENERATED_SOURCE

        column_data = self.generate_column_data(source)
        df_y_full = self.generate_cost_data(source)
        df_x_full, heatmap = self.generate_feature_data(source, column_data, df_y_full)
        df_all = pd.concat([df_x_full, df_y_full], axis=1)

        self.heatmap = heatmap

        return {'df_x_full': df_x_full, 'df_y_full': df_y_full}

    def generate_column_data(self, source):

        sorted_columns = sorted(source[source.keys()[0]].keys())

        # Gather string values.
        column_data = {}
        for column in sorted_columns:
            values = []
            for _, single_source_value in source.iteritems():
                if column in single_source_value.keys() and ',' in str(single_source_value[column]):
                    values.extend([x.strip() for x in single_source_value[column].split(',')])
                elif column in single_source_value.keys():
                    if type(single_source_value[column]) == str:
                        values.append(single_source_value[column].strip())
            values = sorted(set(values))
            column_data.update({column: values})

        return column_data

    def generate_cost_data(self, source):

        indexes = []
        source_costs = []
        for key in sorted(source):
            indexes.append(key)
            source_costs.append(source[key]['cost'])

        return pd.DataFrame(source_costs, index=indexes, columns=['cost'])

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

