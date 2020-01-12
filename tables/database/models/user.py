
class User(object):

    def __init__(self, username, id):
        self.id = id
        self.username = username

    @classmethod
    def from_tuple(cls, tup):
        return cls(*tup)