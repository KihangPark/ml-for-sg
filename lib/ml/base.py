

class MLBase(object):

    def __init__(self, target_data):
        self.target_data = target_data
        self.model = self.get_model()

    def get_model(self):
        pass

    def fit(self):
        pass

    def verification(self):
        pass

    def predict(self, data):
        pass

