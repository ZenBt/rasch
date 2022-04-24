class Config():
    DEBUG = True
    SECRET_KEY = 'VerySecretKey'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://zenb:1@localhost/rasch'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_HEIGHT = 400