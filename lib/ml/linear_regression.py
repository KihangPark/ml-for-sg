from sklearn import linear_model
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from lib.ml.base import MLBase


class LinearRegression(MLBase):

    def __init__(self, target_data, cost_data, model_name=None):
        super(MLBase, self).__init__()
        if model_name == 'ordinary' or model_name is None:
            self.model = OrdinaryLeastSquares()
        self.target_data = target_data
        self.cost_data = cost_data

    def fit(self):
        return self.model.fit(self.target_data, self.cost_data)

    def verification(self):
        pass

    def predict(self, data):
        return self.model.predict(data)


class OrdinaryLeastSquares(object):

    def __init__(self):
        self.model = linear_model.LinearRegression()
        self.predictor = None

    def fit(self, target_data, cost_data):
        X = target_data.values
        y = cost_data.values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
        self.predictor = self.model.fit(X_train, y_train)

        return {
            'predictor': self.predictor,
            'mean_squared_error': mean_squared_error(y_test, self.predictor.predict(X_test))
        }

    def predict(self, data):
        return self.predictor.predict(data)
