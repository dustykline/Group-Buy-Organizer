

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(database.Model, UserMixin): #todo restructure
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(20), unique=True, nullable=False)
    password = database.Column(database.String(60), nullable=False)  # todo changed to hashed_pw
    email = database.Column(database.String(120), unique=True, nullable=False)
    disabled = database.Column(database.Boolean, nullable=False, default=False) #todo admin model
    is_admin = database.Column(database.Boolean, nullable=False, default=False)
    is_root = database.Column(database.Boolean, nullable=False, default=False)
    date_created = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)

    def get_reset_token(self, expires_seconds=3600):
        serializer = TimedJSONWebSignatureSerializer(web_app.config['SECRET_KEY'], expires_seconds)
        return serializer.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        serializer = TimedJSONWebSignatureSerializer(web_app.config['SECRET_KEY'])
        try:
            user_id = serializer.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Instance(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    root_created = database.Column(database.Boolean, nullable=False, default=False) #todo admin model
    registration_enabled = database.Column(database.Boolean, nullable=False, default=True)


class Category(database.Model):
    ''''''
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), nullable=False, unique=True) #todo admin model