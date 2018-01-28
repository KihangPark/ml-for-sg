import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


class DataConvertHandler(object):

    def __init__(self, target_data_list):
        self.target_data_list = target_data_list

    def convert_text_dictionary(self, text_feature_dict):

        count_vectorizer = CountVectorizer()
        feature_vectors = count_vectorizer.fit_transform(
            [' '.join(text_feature_dict.values())]
        )
        vocabulary = count_vectorizer.get_feature_names()

        keyword_dic = dict()
        for key, value in zip(vocabulary, feature_vectors.toarray()[0]):
            keyword_dic.update({key: value})

        return keyword_dic

    def convert_to_panda(self):

        data_df = None
        cost_df = None

        for target_data in self.target_data_list[:20]:

            # unpack target data
            id = target_data['id']
            cost = target_data['cost']

            # get feature dictionary
            feature_dictionary = dict()
            text_feature_dict = target_data['feature_dict']['text_feature']
            feature_dictionary = self.convert_text_dictionary(text_feature_dict)
            value_feature_dict = target_data['feature_dict']['value_feature']
            keyword_feature_dict = target_data['feature_dict']['keyword_feature']

            if data_df is None:
                data_df = pd.DataFrame(
                    [feature_dictionary.values()],
                    index=[id],
                    columns=feature_dictionary.keys()
                )
                cost_df = pd.DataFrame(
                    [cost],
                    index=[id],
                    columns=['cost']
                )
            else:
                additional_columns = list(set(feature_dictionary.keys()) - set(data_df.columns))
                additional_values = []
                for i in additional_columns:
                    additional_values.append(feature_dictionary[i])
                empty_df = pd.DataFrame(
                    [[0] * len(additional_columns)],
                    index=data_df.index,
                    columns=additional_columns
                )
                data_df = pd.concat([data_df, empty_df], axis=1)
                additional_data_values = []
                for column in data_df.columns:
                    if column in feature_dictionary.keys():
                        additional_data_values.append(feature_dictionary[column])
                        print additional_data_values
                    else:
                        additional_data_values.append(0)
                additional_data_df = pd.DataFrame(
                    [additional_data_values],
                    index=[id],
                    columns=data_df.columns
                )
                data_df = pd.concat([data_df, additional_data_df])
                additional_cost_df = pd.DataFrame(
                    [cost],
                    index=[id],
                    columns=['cost']
                )
                cost_df = pd.concat([cost_df, additional_cost_df])

        return {'data_df': data_df, 'cost_df': cost_df}
