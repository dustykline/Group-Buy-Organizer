class Configuration:
    SECRET_KEY = 'temporary'  # todo secrets.token_hex(16)... have in config.py file?
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db' #todo turn into environment variable
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = None  # os.environ.get('EMAIL_USER') #todo merge into model
    MAIL_PASSWORD = None  # ^same