#!/usr/bin/env python3
"""
user_manager.py — User management for NGK Sollai
Stores users in NGK_Solai_Data/users.json (bcrypt hashed passwords)
Roles: admin, user
"""
import json, os, re
import bcrypt
from datetime import datetime

DATA_DIR = os.environ.get("DATA_DIR", os.path.expanduser("~/NGK_Solai_Data"))
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# Password rules (Google-style)
PW_MIN_LEN    = 8
PW_RE_UPPER   = re.compile(r'[A-Z]')
PW_RE_LOWER   = re.compile(r'[a-z]')
PW_RE_DIGIT   = re.compile(r'\d')
PW_RE_SPECIAL = re.compile(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?`~]')

def validate_password(pw):
    """Returns (True, '') or (False, error_message)"""
    if len(pw) < PW_MIN_LEN:
        return False, f"குறைந்தது {PW_MIN_LEN} எழுத்துகள் இருக்க வேண்டும்"
    if not PW_RE_UPPER.search(pw):
        return False, "குறைந்தது ஒரு பெரிய எழுத்து (A-Z) இருக்க வேண்டும்"
    if not PW_RE_LOWER.search(pw):
        return False, "குறைந்தது ஒரு சிறிய எழுத்து (a-z) இருக்க வேண்டும்"
    if not PW_RE_DIGIT.search(pw):
        return False, "குறைந்தது ஒரு எண் (0-9) இருக்க வேண்டும்"
    if not PW_RE_SPECIAL.search(pw):
        return False, "குறைந்தது ஒரு சிறப்பு எழுத்து (!@#$ போன்றவை) இருக்க வேண்டும்"
    return True, ''

def _load():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save(data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _hash(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def _check(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def init_admin(username='admin', password=None):
    """Create admin user if no users exist. Called once at startup."""
    data = _load()
    if data:
        return  # users already exist
    if password is None:
        raise ValueError("Initial admin password required")
    ok, err = validate_password(password)
    if not ok:
        raise ValueError(err)
    data[username] = {
        'role': 'admin',
        'password_hash': _hash(password),
        'must_change': False,
        'created': datetime.now().isoformat(),
        'last_changed': datetime.now().isoformat(),
    }
    _save(data)
    print(f"Admin user '{username}' created.")

def authenticate(username, password):
    """Returns user dict or None"""
    data = _load()
    u = data.get(username)
    if not u:
        return None
    if not _check(password, u['password_hash']):
        return None
    return {'username': username, **u}

def change_password(username, new_password):
    """Returns (True,'') or (False, error)"""
    ok, err = validate_password(new_password)
    if not ok:
        return False, err
    data = _load()
    if username not in data:
        return False, "பயனர் இல்லை"
    data[username]['password_hash'] = _hash(new_password)
    data[username]['must_change'] = False
    data[username]['last_changed'] = datetime.now().isoformat()
    _save(data)
    return True, ''

def add_user(username, temp_password, role='user'):
    """Admin adds a new user. Returns (True,'') or (False, error)"""
    if not username or not re.match(r'^[a-zA-Z0-9_]{3,32}$', username):
        return False, "பயனர் பெயர் 3-32 எழுத்துகள், எண்கள், _ மட்டும்"
    ok, err = validate_password(temp_password)
    if not ok:
        return False, err
    data = _load()
    if username in data:
        return False, "பயனர் பெயர் ஏற்கனவே உள்ளது"
    data[username] = {
        'role': role,
        'password_hash': _hash(temp_password),
        'must_change': True,
        'created': datetime.now().isoformat(),
        'last_changed': datetime.now().isoformat(),
    }
    _save(data)
    return True, ''

def delete_user(username):
    """Returns (True,'') or (False, error)"""
    data = _load()
    if username not in data:
        return False, "பயனர் இல்லை"
    if data[username]['role'] == 'admin' and sum(1 for u in data.values() if u['role'] == 'admin') == 1:
        return False, "கடைசி admin-ஐ நீக்க முடியாது"
    del data[username]
    _save(data)
    return True, ''

def list_users():
    data = _load()
    return [{'username': k, 'role': v['role'],
             'must_change': v.get('must_change', False),
             'created': v.get('created',''),
             'last_changed': v.get('last_changed','')}
            for k, v in data.items()]

def get_user(username):
    data = _load()
    u = data.get(username)
    if not u:
        return None
    return {'username': username, **u}

def is_admin(username):
    u = get_user(username)
    return u and u.get('role') == 'admin'
