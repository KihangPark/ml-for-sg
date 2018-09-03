import os


import pandas as pd
import nbformat as nbf


from lib.resource.resource_handler import ResourceHandler


class FeatureAnalyzer(object):

    _resource_handler = None
    _feature_analyze_report_file_name = None

    df_x_full = None
    df_y_full = None
    df_x_text_full = None

    def __init__(self, df_x_full=None, df_x_text_full=None, df_y_full=None):
        self._resource_handler = ResourceHandler()
        self._feature_analyze_report_file_name = self._resource_handler.get_feature_analyze_report_file_name()
        if not df_x_full or not df_x_text_full or not df_y_full:
            self._load_source_data()
        else:
            self.df_x_full = df_x_full
            self.df_x_text_full = df_x_text_full
            self.df_y_full = df_y_full

    def analyze(self):

        # Remove feature candidates based on null values.
        df_x_remove_columns = self.generate_feature_delete_list_based_on_null_value(
            self.df_x_full
        )

        # Remove feature candidates based on co-relationship with cost.
        df_x_remove_columns.extend(self.generate_feature_delete_list_based_on_cost_relation(
            self.df_x_full, rate=0.3
        ))

        # Reduced dataframe based on candidates.
        df_x_full = self.df_x_full.drop(df_x_remove_columns, axis=1)

        # Remove feature candidates based on co-relationship with cost.
        df_x_text_remove_columns = self.generate_feature_delete_list_based_on_cost_relation(
            self.df_x_text_full, rate=0.8
        )

        # Reduced dataframe based on candidates.
        df_x_text_full = self.df_x_text_full.drop(df_x_text_remove_columns, axis=1)

        data = {
            'skip_feature_for_df_x_full': df_x_remove_columns,
            'skip_feature_for_df_x_text_full': df_x_text_remove_columns
        }
        self._resource_handler.save_source_convert_config(data)

        self._save_source_analyze_report()

    def generate_feature_delete_list_based_on_null_value(self, dataframe):
        null_columns = dataframe.columns[dataframe.isnull().any()].tolist()
        remove_columns = []
        # Remove column if column contains over than 20% null column.
        for column in null_columns:
            if pd.isnull(dataframe[column]).sum() > (0.2 * len(dataframe.index)):
                remove_columns.append(column)
        return remove_columns

    def generate_feature_delete_list_based_on_cost_relation(self, dataframe, rate=0.3):
        # Filter out based on relation
        df_full = pd.concat([dataframe, self.df_y_full], axis=1)
        series = df_full.corr()['cost'] < rate
        return series[series.values == True].index.tolist()

    def _load_source_data(self):
        source_data = self._resource_handler.load_source_data()
        self.df_x_full = source_data['df_x_full']
        self.df_y_full = source_data['df_y_full']
        self.df_x_text_full = source_data['df_x_text_full']

    def _save_source_analyze_report(self):
        nb = nbf.v4.new_notebook()
        nb['cells'] = []
        codes = []

        text = """\
# Analyze result based on original source dataframe."""
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        codes.append("""\
# Set package root directory.
import os
os.environ['ML_FOR_SG_ROOT'] = '{}'
import sys
sys.path.append(os.environ['ML_FOR_SG_ROOT'])
import pandas

# Set for inline graph.
import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline

from lib.resource.feature_analyzer import FeatureAnalyzer""".format(os.environ['ML_FOR_SG_ROOT']))

        codes.append("""\
feature_analyzer = FeatureAnalyzer()""")

        codes.append("""\
# Dataframe of features without string description.
feature_analyzer.df_x_full""")

        codes.append("""\
# Dataframe of string description features.
feature_analyzer.df_x_text_full""")

        codes.append("""\
# Dataframe of cost.
feature_analyzer.df_y_full""")

        codes.append("""\
# Remove feature candidates based on null values.
df_x_remove_columns = feature_analyzer.generate_feature_delete_list_based_on_null_value(feature_analyzer.df_x_full)
print df_x_remove_columns""")

        codes.append("""\
# Reduced dataframe based on candidates.
df_x_full = feature_analyzer.df_x_full.drop(df_x_remove_columns,axis=1)
print df_x_full""")

        codes.append("""\
# Remove feature candidates based on co-relationship with cost.
df_x_remove_columns2 = feature_analyzer.generate_feature_delete_list_based_on_cost_relation(feature_analyzer.df_x_full, rate=0.3)
print df_x_remove_columns2""")

        codes.append("""\
# Reduced dataframe based on candidates.
df_x_full = feature_analyzer.df_x_full.drop(df_x_remove_columns2,axis=1)
print df_x_full""")

        codes.append("""\
# Generate heatmap based on reduced dataframe.
df_full = pandas.concat([df_x_full, feature_analyzer.df_y_full], axis=1)
fig, ax = plt.subplots(figsize=(15, 15))
sns.heatmap(df_full.corr(), annot=True, linewidths=.5, cmap='YlGnBu')""")

        codes.append("""\
# Remove feature candidates based on co-relationship with cost.
df_x_text_remove_columns = feature_analyzer.generate_feature_delete_list_based_on_cost_relation(feature_analyzer.df_x_text_full, rate=0.7)
print df_x_text_remove_columns""")

        codes.append("""\
# Reduced dataframe based on candidates.
df_x_text_full = feature_analyzer.df_x_text_full.drop(df_x_text_remove_columns,axis=1)
print df_x_text_full""")

        codes.append("""\
# Generate heatmap based on reduced dataframe.
df_full = pandas.concat([df_x_text_full, feature_analyzer.df_y_full], axis=1)
fig, ax = plt.subplots(figsize=(15, 15))
sns.heatmap(df_full.corr(), annot=True, linewidths=.5, cmap='YlGnBu')""")

        codes.append("""\
# For updating configure,
# please update df_x_remove_columns, df_x_remove_columns2 and df_x_text_remove_columns
# and execute below.
from lib.resource.resource_handler import ResourceHandler
resource_handler = ResourceHandler()
data = {
    'skip_feature_for_df_x_full': df_x_remove_columns + df_x_remove_columns2,
    'skip_feature_for_df_x_text_full': df_x_text_remove_columns
}
resource_handler.save_source_convert_config(data)""")

        for code in codes:
            nb['cells'].append(nbf.v4.new_code_cell(code))

        with open(self._feature_analyze_report_file_name, 'w') as f:
            nbf.write(nb, f)

    def save_source_analyze_configure(self):
        pass