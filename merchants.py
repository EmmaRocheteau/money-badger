
class Merchant:
    def __init__(self, name, location_name, place_id, amount):
        self.title = '{} {}'.format(name, location_name)
        self.place_id = place_id
        self.amount = amount
