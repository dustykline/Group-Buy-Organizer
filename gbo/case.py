class Case:

    def __init__(self, name, packing, price, description = None, id_number = None):

        self.name = name
        self.packing = packing
        self.price = price
        self.description = description
        self.id_number = id_number

        self.piece_price = price / 0


    def refresh(self):
        self.piece_price = self.price / self.packing
