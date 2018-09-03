import pandas as pd


from sklearn.metrics import r2_score
from sklearn.cross_validation import train_test_split


from lib.resource.resource_handler import ResourceHandler
from lib.model.utils import add_appendix_to_text_dataframe


class Trainer(object):

    def __init__(self):
        self._resource_handler = ResourceHandler()
        self._data = self._resource_handler.load_resource_data()

    def train_model(self, model, feature):

        cost = self._data['df_y_full']

        X_train, X_test, y_train, y_test = train_test_split(
            feature,
            cost,
            test_size=0.3,
            random_state=1234
        )

        trained_model = model.fit(X_train, y_train)
        y_pred = trained_model.predict(X_test)
        r2_score_result = r2_score(y_test, y_pred)

        return trained_model, r2_score_result

    def compare_models(self, model_list, feature):

        cost = self._data['df_y_full']

        X_train, X_test, y_train, y_test = train_test_split(
            feature,
            cost,
            test_size=0.3,
            random_state=1234
        )

        least_r2_score = 1.0
        best_model = None
        for model in model_list:
            trained_model = model.fit(X_train, y_train)
            y_pred = trained_model.predict(X_test)
            r2_score_value = r2_score(y_test, y_pred)
            if r2_score_value < least_r2_score:
                best_model = model
                least_r2_score = r2_score

        return best_model, least_r2_score

    def save_trained_model(self, model_name, trained_model):
        self._resource_handler.save_trained_model(model_name, trained_model)

    def merge_features(self, data):
        feature = pd.concat(
            [
                data['df_x_full'],
                add_appendix_to_text_dataframe(data['df_x_text_full'])
            ],
            axis=1
        )
        return feature

