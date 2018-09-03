from sklearn.metrics import r2_score
from sklearn.linear_model import Lasso
from sklearn.cross_validation import train_test_split


from lib.model.base_model import BaseModel


class LassoModel(BaseModel):

    type = 'lasso'

    def __init__(self, **kwargs):
        super(LassoModel, self).__init__(**kwargs)
        self.model = Lasso(alpha=0.1)

    def fit(self, feature, cost):
        return self.model.fit(feature, cost)

    def predict(self, data):
        return self.model.predict(data)

    def verification(self):
        pass
