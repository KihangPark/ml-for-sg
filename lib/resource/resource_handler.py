import os
import pandas as pd


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

    def _generate_raw_data_file_name(self):
        return os.path.join(self.package_root, 'raw_data')

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
        return None

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
        return None

    def load_source_analyze_configure(self):
        return None

    def load_train_result(self):
        return None
