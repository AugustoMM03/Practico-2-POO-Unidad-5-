import os
SECRET_KEY = 'secretkey'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'datos.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH