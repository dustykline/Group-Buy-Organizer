class User: #(db.Model)

    #list db stuff here
    # id = db.Column(db.Integer, primary_key=True)

    def __init__(self, username, email, password):

        self.username = username
        self.email = email
        self.password = password

        self.disabled = False
        self.is_admin = False
        self.is_root = False

class Instance:
    pass

class Event:
    pass

class CaseSplit:
    pass