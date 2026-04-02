from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["open_elective_db"]

def seed_database():
    
    if db.branches.count_documents({}) == 0:
        branches = [
            {'code': 'CSE', 'name': 'Computer Science & Engineering'},
            {'code': 'IS', 'name': 'Information Science'},
            {'code': 'AI', 'name': 'Artificial Intelligence'},
            {'code': 'CIVIL', 'name': 'Civil Engineering'},
            {'code': 'MECHANICAL', 'name': 'Mechanical Engineering'},
            {'code': 'EC', 'name': 'Electronics & Communication'}
        ]
        db.branches.insert_many(branches)
        
        subjects = [
            {'code': 'BME654B', 'name': 'Renewable Energy Power Plants', 'branch_code': 'MECHANICAL'},
            {'code': 'BME654C', 'name': 'Mechatronics', 'branch_code': 'MECHANICAL'},
            {'code': 'BEC654C', 'name': 'Electronic Communication System', 'branch_code': 'EC'},
            {'code': 'BCV654A', 'name': 'Water Conservation and Rain Water Harvesting', 'branch_code': 'CIVIL'},
            {'code': 'BCS654A', 'name': 'Introduction to Data Structures', 'branch_code': 'CSE'},
            {'code': 'BAI654B', 'name': 'Fundamentals of Operating System', 'branch_code': 'AI'},
            {'code': 'BIS654D', 'name': 'Introduction to Artificial Intelligence', 'branch_code': 'IS'},
        ]
        db.subjects.insert_many(subjects)
        print("Seeded branches and subjects")

    if db.admins.count_documents({}) == 0:
        admin = {
            'username': 'admin',
            'password_hash': generate_password_hash('Admin@2025'),
            'created_at': datetime.utcnow()
        }
        db.admins.insert_one(admin)
        print("Seeded admin user")

