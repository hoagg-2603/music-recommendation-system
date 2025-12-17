import json
import hashlib
import datetime
import os
import random # Thêm thư viện random

# Đường dẫn file dữ liệu user
USER_FILE = "data/users.json"

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_auto_data():
    now = datetime.datetime.now()
    
    users = {
        # --- USER 1: test_buon (GU VUI - NGHE BUỒN) ---
        "test_buon": {
            "password": hash_pass("123"),
            "onboarding_done": True,
            "profile_valence": 0.85, # Gu gốc: Rất Vui
            "preferences": {"genres": ["Pop", "EDM"], "artists": ["Alan Walker"]},
            "history": []
        },
        
        # --- USER 2: test_vui (GU BUỒN - NGHE VUI) ---
        "test_vui": {
            "password": hash_pass("123"),
            "onboarding_done": True,
            "profile_valence": 0.15, # Gu gốc: Rất Buồn/Chill
            "preferences": {"genres": ["Indie", "Lofi"], "artists": ["Vũ."]},
            "history": []
        }
    }

    print("⏳ Đang tạo dữ liệu lớn (50 bài/user)...")

    # 1. Tạo 50 bài nhạc BUỒN cho 'test_buon'
    # Valence dao động từ 0.05 đến 0.25 (Rất buồn)
    for i in range(50):
        # Giả lập thời gian nghe lùi dần về quá khứ
        timestamp = (now - datetime.timedelta(minutes=i*5)).isoformat()
        
        users["test_buon"]["history"].append({
            "song": f"Sad Ballad No.{i+1}",
            "artist": random.choice(["Mr. Siro", "Vũ.", "Adele", "Sam Smith"]), # Random ca sĩ buồn
            "valence": round(random.uniform(0.05, 0.25), 3), 
            "energy": round(random.uniform(0.1, 0.4), 3),
            "genre": random.choice(["Ballad", "Indie", "Soul"]),
            "timestamp": timestamp
        })

    # 2. Tạo 50 bài nhạc SUNG cho 'test_vui'
    # Valence dao động từ 0.75 đến 0.95 (Rất vui)
    for i in range(50):
        timestamp = (now - datetime.timedelta(minutes=i*5)).isoformat()
        
        users["test_vui"]["history"].append({
            "song": f"Party Hit No.{i+1}",
            "artist": random.choice(["Avicii", "Martin Garrix", "Sơn Tùng M-TP", "Blackpink"]), # Random ca sĩ vui
            "valence": round(random.uniform(0.75, 0.95), 3),
            "energy": round(random.uniform(0.8, 1.0), 3), 
            "genre": random.choice(["EDM", "Pop", "Dance"]),
            "timestamp": timestamp
        })

    # Lưu file
    if not os.path.exists("data"):
        os.makedirs("data")

    with open(USER_FILE, "w", encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
    
    print(f"✅ ĐÃ TẠO XONG: 2 User x 50 bài hát!")
    print(f"📂 File lưu tại: {USER_FILE}")

if __name__ == "__main__":
    create_auto_data()