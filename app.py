import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from pymongo import MongoClient
import logging

# Disable heavy PyMongo debug logging
logging.getLogger('pymongo').setLevel(logging.WARNING)


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# MongoDB Setup
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client.open_elective_db

login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.init_app(app)
csrf.init_app(app)
login_manager.login_view = 'student_login'

# Helper to access db in other modules
def get_db():
    return db

with app.app_context():
    # Verify connection
    try:
        mongo_client.server_info()
        print("Connected to MongoDB")
    except Exception as e:
        print("Could not connect to MongoDB:", e)
    
    from seed_data import seed_database 
    seed_database()

   
    
  

    
  
