
class Match(object):

    def __init__(self, id, winner_id, loser_id, winner_side):
        self.id = id
        self.winner_id = winner_id
        self.loser_id = loser_id
        self.winner_side = winner_side

    @classmethod
    def from_tuple(cls, tup):
        return cls(*tup)