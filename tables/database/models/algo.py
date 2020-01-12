
class Algo(object):

    def __init__(self, id, name, username, rating):
        self.id = id
        self.name = name
        self.username = username
        self.rating = rating

    @classmethod
    def from_tuple(cls, tup):
        return cls(*tup)