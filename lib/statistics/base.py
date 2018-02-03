import pandas as pd
import numpy as np


class StatisticsBase(object):

    def __init__(self, target_data):
        self.target_data = target_data
        self.data_df = target_data['data_df']
        self.cost_df = target_data['cost_df']
        self.df = pd.concat([target_data['data_df'], target_data['cost_df']], axis=1)

    def filter(self, filter_dict=None):
        pass

    def analyze_cost(self, target_data=None):
        if target_data is None:
            target_data = self.target_data
        return dict(target_data['cost'].describe(np.arange(0, 1, 0.1)))

    def get_average_cost(self, target_data=None):
        if target_data is None:
            target_data = self.target_data
        return target_data['cost'].sum() / target_data['cost'].count()

    def get_corr(self, field_name):
        """Return corr value based on target field name.
        """
        pass
