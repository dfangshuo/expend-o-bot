from db import EXPENSE_CATEGORIES

# WIP: Machine learning, currently hard-code rule-based categorizations


class Categorizer:
    def __init__(self):
        self.categories = EXPENSE_CATEGORIES
        self.food_tokens = ['food', '🍴', 'lim',
                            'thai', 'shooting', 'dinner', 'fud', 'boba', 'milk', 'bobz', 'bill']
        self.transport_tokens = ['lyft', 'uber', ':uber:']
        self.rent_tokens = ['rent']

    def train(self):
        raise NotImplementedError()

    def predict(self, descrip):
        text = descrip.lower()
        for tok in self.food_tokens:
            if tok in text:
                return 'f'

        for tok in self.transport_tokens:
            if tok in text:
                return 't'

        for tok in self.rent_tokens:
            if tok in text:
                return 'r'

        return 'm'
