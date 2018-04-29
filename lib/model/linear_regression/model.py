from sklearn import linear_model
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


from lib.model.base_model import BaseModel


class LinearRegression(BaseModel):

    def __init__(self, feature_data, cost_data, model_name=None):
        super(LinearRegression, self).__init__()
        if model_name == 'ordinary' or model_name is None:
            self.model = OrdinaryLeastSquares()
        self.feature_data = feature_data
        self.cost_data = cost_data

    def fit(self):
        return self.model.fit(self.feature_data, self.cost_data)

    def predict(self, data):
        return self.model.predict(data)

    def verification(self):
        pass


class OrdinaryLeastSquares(object):

    def __init__(self):
        self.model = linear_model.LinearRegression()
        self.predictor = None

    def fit(self, feature_data, cost_data):
        X = feature_data.values
        y = cost_data.values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
        self.predictor = self.model.fit(X_train, y_train)

        return {
            'predictor': self.predictor,
            'mean_squared_error': mean_squared_error(y_test, self.predictor.predict(X_test))
        }

    def predict(self, data):
        return self.predictor.predict(data)
