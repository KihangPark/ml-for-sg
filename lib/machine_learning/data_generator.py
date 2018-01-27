import pandas as pd
import numpy as np


class DataGenerator(object):

    def generate_data_from_task(self, task_data_list):

        df = None
        index = 0
        for x in task_data_list[:300]:

            index = index + 1
            print 'generate data : ' + str(index)
            if df is None:
                key = pd.DataFrame(list(x['feature_list']), columns=['key'])
                value = pd.DataFrame(np.ones(len(x['feature_list'])), columns=[x['id']])
                df = pd.concat([key, value], axis=1)
            else:
                temp_df = pd.DataFrame({'key': list(x['feature_list']), x['id']: np.ones(len(x['feature_list']))})
                df = pd.merge(df, temp_df, how='outer', on='key')

            df = df.fillna(0)
        df.set_index('key', inplace=True)
        df = df.transpose()
        return df

