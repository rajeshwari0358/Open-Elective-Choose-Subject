import re
with open('routes.py', 'r') as f:
    content = f.read()

# Fix admin login
content = content.replace(
    "admin_data = db.admins.find_one({'username': username})",
    "admin_data = db.admins.find_one({'username': username.lower() if username else None})"
)

with open('routes.py', 'w') as f:
    f.write(content)
