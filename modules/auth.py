import json
import hashlib
import os
import datetime

USER_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f: json.dump({}, f)
        return {}
    try:
        with open(USER_FILE, "r") as f: return json.load(f)
    except: return {}

def save_users(users):
    with open(USER_FILE, "w") as f: json.dump(users, f, indent=4)

def login(username, password):
    users = load_users()
    if username in users:
        # Hash pass để so sánh
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if users[username]['password'] == hashed:
            return True
    return False

def register(username, password):
    users = load_users()
    if username in users: return False, "User đã tồn tại"
    
    users[username] = {
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "history": [],
        "preferences": []
    }
    save_users(users)
    return True, "Thành công"

def save_history(username, song_row):
    """Lưu bài hát vào lịch sử kèm chỉ số cảm xúc"""
    users = load_users()
    if username in users:
        record = {
            "song": song_row['song'],
            "artist": song_row['artist'],
            "valence": float(song_row.get('valence', 0.5)), # Lưu để phân tích Mood
            "energy": float(song_row.get('energy', 0.5)),
            "timestamp": str(datetime.datetime.now())
        }
        # Thêm vào đầu danh sách
        users[username]['history'].insert(0, record)
        # Giữ lại 50 bài gần nhất
        users[username]['history'] = users[username]['history'][:50]
        save_users(users)

def get_history(username):
    users = load_users()
    return users.get(username, {}).get('history', [])

def check_onboarding_status(username):
    """Kiểm tra xem user đã chọn sở thích chưa (True/False)"""
    users = load_users()
    if username in users:
        return users[username].get('onboarding_done', False)
    return False

def save_onboarding(username, genres, artists):
    """Lưu sở thích và đánh dấu đã hoàn thành"""
    users = load_users()
    if username in users:
        users[username]['preferences'] = {
            'genres': genres,
            'artists': artists
        }
        users[username]['onboarding_done'] = True # Đánh dấu XONG
        
        # TẠO LỊCH SỬ GIẢ LẬP (QUAN TRỌNG ĐỂ CÓ GỢI Ý NGAY)
        # Giả vờ user đã nghe 10 bài thuộc thể loại họ chọn
        fake_history = []
        for g in genres:
            fake_history.append({
                'song': f"Intro to {g}",
                'artist': "Various Artists",
                'genre': g,
                'valence': 0.7, 
                'energy': 0.7,
                'timestamp': str(datetime.datetime.now())
            })
        users[username]['history'] = fake_history
        
        save_users(users)
        return True
    return False
