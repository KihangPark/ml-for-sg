import os
import yaml
import pandas as pd


from lib.utils.misc import (
    load_config,
    load_source_convert_config
)


class ResourceHandler(object):

    raw_data_file_name = None
    source_data_file_name = None
    resource_data_file_name = None
    source_analyze_report_file_name = None
    train_result_report_file_name = None

    def __init__(self):
        self.package_root = os.environ['ML_FOR_SG_ROOT']
        self.raw_data_file_name = self._generate_raw_data_file_name()
        self.source_data_file_name = self._generate_source_data_file_name()
        self.resource_data_file_name = self._generate_resource_data_file_name()
        self.source_analyze_report_file_name = self._generate_source_data_file_name()
        self.train_result_report_file_name = self._generate_train_result_report_file_name()
        self.analyze_report_directory = load_config()['analyze_report_export_directory']
        self.source_convert_config_file_name = self._generate_source_convert_config_file_name()

    def _generate_raw_data_file_name(self):
        return os.path.join(self.package_root, 'raw_data')

    def get_feature_analyze_report_file_name(self):
        return os.path.join(
            self.analyze_report_directory,
            'feature_analyze_report.ipynb'
        )

    def _generate_source_convert_config_file_name(self):
        return os.path.join(
            self.package_root,
            'config',
            'source_convert_config.yaml'
        )

    def _generate_source_data_file_name(self):
        source_data_dir = os.path.join(self.package_root, 'source_data')
        if not os.path.exists(source_data_dir):
            os.mkdir(source_data_dir)
        return {
            'df_x_full': os.path.join(source_data_dir, 'df_x_full.csv'),
            'df_x_text_full': os.path.join(source_data_dir, 'df_x_text_full.csv'),
            'df_y_full': os.path.join(source_data_dir, 'df_y_full.csv')
        }

    def _generate_resource_data_file_name(self):
        resource_data_dir = os.path.join(self.package_root, 'resource_data')
        if not os.path.exists(resource_data_dir):
            os.mkdir(resource_data_dir)
        return {
            'df_x_full': os.path.join(resource_data_dir, 'df_x_full.csv'),
            'df_x_text_full': os.path.join(resource_data_dir, 'df_x_text_full.csv'),
            'df_y_full': os.path.join(resource_data_dir, 'df_y_full.csv')
        }

    def _generate_source_analyze_report_file_name(self):
        return os.path.join(self.package_root, 'source_analyze_report')

    def _generate_train_result_report_file_name(self):
        return os.path.join(self.package_root, 'train_result_report')

    def save_raw_data(self):
        return None

    def save_source_data(self, source_data):
        file_names = self._generate_source_data_file_name()
        df_x_full = file_names['df_x_full']
        df_x_text_full = file_names['df_x_text_full']
        df_y_full = file_names['df_y_full']
        source_data['df_x_full'].to_csv(df_x_full, mode='w', sep=',')
        source_data['df_x_text_full'].to_csv(df_x_text_full, mode='w', sep=',')
        source_data['df_y_full'].to_csv(df_y_full, mode='w', sep=',')

    def save_resource_data(self):
        data = self._generate_resource_data_file_name()
        df_x_full_file_name = data['df_x_full']
        df_x_text_full_file_name = data['df_x_text_full']
        df_y_full_file_name = data['df_y_full']

        data = self.load_source_data()
        df_x_full = data['df_x_full']
        df_x_text_full = data['df_x_text_full']
        df_y_full = data['df_y_full']

        source_convert_config = load_source_convert_config()
        skip_feature_for_df_x_full = source_convert_config['skip_feature_for_df_x_full']
        skip_feature_for_df_x_text_full = source_convert_config['skip_feature_for_df_x_text_full']

        df_x_full = df_x_full.drop(skip_feature_for_df_x_full, axis=1)
        df_x_full = self.remove_string_values(df_x_full)
        df_x_text_full = df_x_text_full.drop(skip_feature_for_df_x_text_full, axis=1)

        df_x_full.to_csv(df_x_full_file_name, mode='w', sep=',')
        df_x_text_full.to_csv(df_x_text_full_file_name, mode='w', sep=',')
        df_y_full.to_csv(df_y_full_file_name, mode='w', sep=',')

    def load_raw_data(self):
        return None

    def load_source_data(self):
        file_names = self._generate_source_data_file_name()
        df_x_full = file_names['df_x_full']
        df_x_text_full = file_names['df_x_text_full']
        df_y_full = file_names['df_y_full']
        return {
            'df_x_full': pd.read_csv(df_x_full, index_col=[0]),
            'df_x_text_full': pd.read_csv(df_x_text_full, index_col=[0]),
            'df_y_full': pd.read_csv(df_y_full, index_col=[0])
        }

    def load_resource_data(self):
        file_names = self._generate_resource_data_file_name()
        df_x_full = file_names['df_x_full']
        df_x_text_full = file_names['df_x_text_full']
        df_y_full = file_names['df_y_full']
        return {
            'df_x_full': pd.read_csv(df_x_full, index_col=[0]),
            'df_x_text_full': pd.read_csv(df_x_text_full, index_col=[0]),
            'df_y_full': pd.read_csv(df_y_full, index_col=[0])
        }

    def load_source_analyze_configure(self):
        return None

    def load_train_result(self):
        return None

    def save_source_convert_config(self, data):
        with open(self.source_convert_config_file_name, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    def remove_string_values(self, dataframe):
        string_series = (dataframe.dtypes == 'object')
        string_columns = string_series[string_series == True].index
        df_without_string_columns = dataframe.drop(string_columns, axis=1)
        df_with_string_columns = dataframe[string_columns]
        for column in string_columns:
            for group in df_with_string_columns[[column]].groupby(column):
                new_column_name = column + '__' + group[0]
                # Replace string to int.
                values = df_with_string_columns[column].replace(group[0], 1).values
                replaced_values = []
                for value in values:
                    if value != 1:
                        replaced_values.append(0)
                    else:
                        replaced_values.append(1)
                df_with_string_columns[new_column_name] = replaced_values
        df_with_string_columns = df_with_string_columns.drop(
            string_columns, axis=1)
        df_full = pd.concat(
            [df_without_string_columns, df_with_string_columns],
            axis=1)
        return df_full

