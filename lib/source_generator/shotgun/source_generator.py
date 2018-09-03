import pandas as pd
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer


from lib.resource.resource_handler import ResourceHandler
from lib.source_generator.shotgun.utils import get_shotgun_handler
from lib.source_generator.base_source_generator import BaseSourceGenerator


class ShotgunSourceGenerator(BaseSourceGenerator):
    """Class for generating panda data based on shotgun information.
    """

    def __init__(self):
        super(ShotgunSourceGenerator, self).__init__()

        # Generate shotgun handler based on config settings.
        self.handler = get_shotgun_handler(self.root_config)
        if not self.handler:
            raise Exception('Shotgun server connection fails.')

        # Unpack config settings.
        self.data_config = self.generator_config['shotgun']['data']
        self.text = self.data_config['text']
        self.cost = self.data_config['cost']
        self.source_schema = self.data_config['source_schema']
        self.skip_features = self.data_config['skip_features']
        self.source_includes = self.data_config['source_includes']

        # Get resource handler instance for save / load source data file.
        self.resource_handler = ResourceHandler()

    def generate_source_data(self, project_id=None, limit=0):
        """Generate source data from shotgun information.

        Args:
            project_id (int): shotgun project id.
            limit (int): limit count for source items.
                        this value can be used for test.
        Returns:
            (dict): dictionary information which contains panda data.
                df_x_full (pd.DataFrame): dataframe which contains all features expect text features.
                df_x_text_full (pd.DataFrame): dataframe which contains all text features.
                df_y_full (pd.DataFrame): dataframe which contains all cost values.
        """
        if not project_id:
            return []

        # Get original raw field data from shotgun.
        raw_data = self._get_raw_data(project_id, limit)

        # Modify original raw file data and generate proper dictionary format for panda data converting.
        modified_raw_data = self._reformat_raw_data(raw_data)

        # Convert to panda dataframe data format.
        source_data = self._convert_raw_to_source_data(modified_raw_data)

        # Save source data to cvs files.
        self.resource_handler.save_source_data(source_data)

        return source_data

    def _get_raw_data(self, project_id, limit=0):
        """Get original raw data from shotgun.

        Args:
            project_id (int): shotgun project id.
            limit (int): limit count for source items.
                        this value can be used for test.

        """
        # Generate shotgun project filter.
        filters = [[
            'project', 'is', {
                'type': 'Project',
                'id': project_id}
        ]]

        # Generate source filter.
        if self.source_includes:
            filters.append(
                [
                    'code', 'in', self.source_includes
                ]
            )

        # Get raw data from shotgun.
        schema_field_list = self.handler.schema_field_read(self.source_schema)
        raw_data = self.handler.find(
            self.source_schema,
            filters,
            schema_field_list.keys(),
            limit=limit
        )

        # Filter out improper project.
        valid_raw_data = []
        for raw_datum in raw_data:
            if not raw_datum['project']:
                continue
            valid_raw_data.append(raw_datum)

        return valid_raw_data

    def _reformat_raw_data(self, raw_data):
        """Calculate shot cost and reformat raw data for panda data convert.

        Args:
            raw_data (list): dictionary which contains raw field information
                            from shotgun.

        """
        modified_raw_data = dict()
        schema_field_list = self.handler.schema_field_read('Task')

        for raw_datum in raw_data:

            cost_feature = 0
            for task in raw_datum['tasks']:

                # Generate filter for task.
                filters = [
                    [
                        'project', 'is', {
                            'type': 'Project',
                            'id': raw_datum['project']['id']
                        }
                    ], [
                        'id', 'is', task['id']
                    ]
                ]

                task = self.handler.find(
                    'Task',
                    filters,
                    schema_field_list.keys(),
                    limit=1
                )[0]

                # Update total cost.
                cost_feature = cost_feature + task[self.cost]

            # Get text, value feature dictionary.
            text_features, value_features = self._get_features(
                raw_datum,
                self.text['feature_list']
            )

            # Add new shot information.
            modified_raw_data[raw_datum['code']] = {
                'id': raw_datum['id'],
                'feature_dict': {
                    'text_features': text_features,
                    'value_features': value_features
                },
                'cost': cost_feature
            }

        return modified_raw_data

    def _get_features(self, raw_data, text_feature_list):
        """Return dictionaries which contains text, value feature information..

        Args:
            raw_data (dict): raw dictionary data from shotgun.
            text_feature_list (list): list of text feature field names.

        Returns:
            (dict, dict): text feature dictionary and value feature dictionary.
        """
        # Return dictionary which contains text feature and feature field value.
        text_feature_dict = dict()
        # Return dictionary which contains normal feature and feature field value.
        value_feature_dict = dict()

        for feature in raw_data.keys():

            # Skip if feature name is in skip list.
            if feature in self.skip_features:
                continue

            if feature in text_feature_list:
                # Update text_feature_dict if feature name is in text_feature_list.
                target_feature_dict = text_feature_dict
            else:
                # Update value_feature_dict if feature name is not in text_feature_list.
                target_feature_dict = value_feature_dict

            # Feature value is list.
            if isinstance(raw_data[feature], list):

                # Collect all list values.
                list_value = []
                for value in raw_data[feature]:
                    if isinstance(value, dict):
                        list_value.append(value['name'])
                    else:
                        list_value.append(value)

                # Item of list_value is string.
                if list_value and isinstance(list_value[0], str):
                    target_feature_dict[feature] = self._get_word_list(
                        ','.join(list_value)
                    )
                # Item of list_value is number.
                elif list_value and \
                        (isinstance(list_value[0], int) or isinstance(list_value[0], float)):
                    target_feature_dict.update({feature: sum(list_value)})

            # Feature value is dictionary.
            elif isinstance(raw_data[feature], dict):
                target_feature_dict[feature] = raw_data[feature]['name']

            # Feature value is value.
            else:
                if feature in text_feature_list:
                    target_feature_dict[feature] = self._get_word_list(
                        raw_data[feature]
                    )
                else:
                    target_feature_dict[feature] = raw_data[feature]

        return text_feature_dict, value_feature_dict

    def _convert_raw_to_source_data(self, modified_raw_data):
        """Convert raw data to panda dataframe data.

        Args:
            modified_raw_data (dict): dictionary which contains text, value, cost data.

        Returns:
            (dict): dictionary which contains value, text, cost dataframe.
                df_x_full (dataframe): value dataframe.
                df_x_text_full (dataframe): text dataframe.
                df_y_full (dataframe): cost dataframe.
        """
        # Generate column list for value panda dataframe.
        value_columns = self._generate_value_column_data(modified_raw_data)

        # Generate column list for text panda dataframe.
        text_columns = self._generate_text_column_data(modified_raw_data)

        # Generate cost dataframe.
        df_y_full = self._generate_cost_panda_data(modified_raw_data)

        # Generate value, text dataframe.
        panda_data = self._generate_panda_data(
            modified_raw_data,
            value_columns,
            text_columns
        )
        df_x_full = panda_data['df_x']
        df_x_text_full = panda_data['df_x_text']

        return {
            'df_x_full': df_x_full,
            'df_x_text_full': df_x_text_full,
            'df_y_full': df_y_full
        }

    def _generate_panda_data(self, modified_raw_data, value_columns, text_columns):
        """Generate text, value dataframe.

        Args:
            modified_raw_data (dict): dictionary which contains text, value, cost feature values.
                shot name (dict):
                    id (int): shot id.
                    feature_dict (dict):
                        text_features (dict): dictionary which contains text feature name and value.
                        value_feature (dict): dictionary which contains value feature name and value.
                    cost (int): total cost value.
        """
        # Generate value feature index.
        extended_value_columns = []
        for _, shot_values in modified_raw_data.iteritems():
            for column, _ in shot_values['feature_dict']['value_features'].iteritems():
                if value_columns[column] is None:
                    # Target feature does not have list values.
                    extended_value_columns.append(column)
                else:
                    # Target feature has list values.
                    # For example,
                    # 'asset': ['test1', 'test2', 'test3']
                    # will be converted to
                    # 'asset__test1', 'asset__test2', 'asset__test3'
                    # and these list will be added as feature columns.
                    for value in value_columns[column]:
                        extended_value_columns.append('{}__{}'.format(column, value))

        # Columns for value dataframe.
        extended_value_columns = sorted(set(extended_value_columns))

        # Value for value dataframe.
        df_x_values = []

        # Generate value dataframe.
        for shot_name, shot_datum in modified_raw_data.iteritems():
            value_feature_values = []
            for value_feature in extended_value_columns:
                if '__' in value_feature:
                    column = value_feature.split('__')[0]
                    sub_column = value_feature.split('__')[1]
                    value_feature_values.append(
                        1 if sub_column in shot_datum['feature_dict']['value_features'][column] else 0)
                else:
                    value_feature_values.append(shot_datum['feature_dict']['value_features'][value_feature])
            df_x_values.append(value_feature_values)

        # Columns for text dataframe.
        text_columns = sorted(set(text_columns))

        # Value for text dataframe.
        df_x_text_values = []

        # Generate text dataframe.
        for shot_name, shot_datum in modified_raw_data.iteritems():
            text_feature_values = []
            for text_feature in text_columns:
                result = 0
                for key, value in shot_datum['feature_dict']['text_features'].iteritems():
                    if text_feature in value:
                        result = 1
                        break
                text_feature_values.append(result)
            df_x_text_values.append(text_feature_values)

        df_x = pd.DataFrame(
            df_x_values,
            index=modified_raw_data.keys(),
            columns=extended_value_columns
        )
        df_x_text = pd.DataFrame(
            df_x_text_values,
            index=modified_raw_data.keys(),
            columns=text_columns
        )
        return {'df_x': df_x, 'df_x_text': df_x_text}

    def _get_word_list(self, text):
        """Return all word list based on text string.

        Args:
            text (str): text string.

        Returns:
            (list): word list.
        """
        count_vectorizer = CountVectorizer()
        count_vectorizer.fit_transform([text])
        feature_names = count_vectorizer.get_feature_names()
        return ','.join(feature_names)

    def _generate_value_column_data(self, modified_raw_data):
        """Return value column data for value dataframe.

        Args:
            modified_raw_data (dict): dictionary data which contains shotgun information.

        Returns:
            (dict): column information.
                column name (None or list): None if feature value has single element.
                                            list if feature value has multiple elements.
        """
        column_data = defaultdict(list)

        # Collect all list value.
        for _, raw_datum in modified_raw_data.iteritems():
            for key, value in raw_datum['feature_dict']['value_features'].iteritems():
                # Value contains multiple elements.
                if (type(value) == str or type(value) == unicode) and ',' in value:
                    column_data[key].extend(value.split(','))
                else:
                    column_data[key] = None

        # Remove duplicated list from column_data.
        for _, value in column_data.iteritems():
            if type(value) == list:
                column_data[_] = sorted(set(value))

        return column_data

    def _generate_text_column_data(self, modified_raw_data):
        """Return text column data for text dataframe.

        Args:
            modified_raw_data (dict): dictionary data which contains shotgun information.

        Returns:
            (list): column list.
        """
        columns = []
        for _, raw_datum in modified_raw_data.iteritems():
            for key, value in raw_datum['feature_dict']['text_features'].iteritems():
                if value is not None:
                    columns.extend([x.strip() for x in value.split(',')])

        return sorted(set(columns))

    def _generate_cost_panda_data(self, modified_raw_data):
        """Return cost dataframe.
        Args:
            modified_raw_data (dict): dictionary data which contains shotgun information.

        Returns:
            (pd.DataFrame): cost dataframe.
        """
        indexes = []
        source_costs = []
        for key in sorted(modified_raw_data):
            indexes.append(key)
            source_costs.append(modified_raw_data[key]['cost'])

        return pd.DataFrame(source_costs, index=indexes, columns=['cost'])

