from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId

class Admin(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.password_hash = user_data.get('password_hash')
        self.user_type = 'admin'

    def get_id(self):
        return f"admin_{self.id}"
    
    @staticmethod
    def check_password(stored_hash, password):
        return check_password_hash(stored_hash, password)

class Student(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.name = user_data.get('name')
        self.usn = user_data.get('usn')
        self.email = user_data.get('email')
        self.branch_code = user_data.get('branch_code')
        self.password_hash = user_data.get('password_hash')
        self.user_type = 'student'

    def get_id(self):
        return f"student_{self.id}"
    
    @staticmethod
    def check_password(stored_hash, password):
        return check_password_hash(stored_hash, password)

