import pandas as pd
import pandas as pd
import numpy as np
import os
import datetime
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
DATA_PATH = "data/dataset.csv"

# đọc dữ liệu, làm sạch
@st.cache_data
def load_and_clean_data():
    if not os.path.exists(DATA_PATH): 
        st.error(f"Không tìm thấy file: {DATA_PATH}")
        return pd.DataFrame()
    
    try:
        # Đọc file CSV
        df = pd.read_csv(DATA_PATH)
        
        # 1. Xử lý tên cột (Xóa khoảng trắng thừa)
        df.columns = df.columns.str.strip()
        
        # 2. Map tên cột từ CSV của bạn sang tên chuẩn của App
        # Dựa trên header bạn gửi: track_name -> song, artists -> artist
        rename_map = {
            'track_name': 'song',
            'artists': 'artist',
            'track_genre': 'genre',
            'album_name': 'album'
        }
        df = df.rename(columns=rename_map)
        
        # 3. KIỂM TRA & SỬA LỖI (Fallback)
        # Nếu đổi tên thất bại (vẫn còn track_name), ta copy dữ liệu sang cột mới
        if 'song' not in df.columns and 'track_name' in df.columns:
            df['song'] = df['track_name']
        if 'artist' not in df.columns and 'artists' in df.columns:
            df['artist'] = df['artists']
            
        # Nếu vẫn thiếu cột thì báo lỗi và dừng
        if 'song' not in df.columns or 'artist' not in df.columns:
            st.error(f"⚠️ Lỗi CSV: Không tìm thấy cột tên bài hát/ca sĩ. Các cột hiện có: {list(df.columns)}")
            return pd.DataFrame()

        # 4. Làm sạch dữ liệu
        # Xóa dòng thiếu dữ liệu
        df = df.dropna(subset=['song', 'artist'])
        # Xóa dòng trùng lặp
        df = df.drop_duplicates(subset=['song', 'artist'])
        
        # Lấy 5000 bài đầu tiên để chạy cho nhanh
        df = df.head(5000)
        
        # Tạo cột ID hiển thị (Combo tên + ca sĩ)
        df['combined_name'] = df['song'] + " - " + df['artist']
        
        return df
        
    except Exception as e:
        st.error(f"❌ Lỗi khi đọc file: {e}")
        return pd.DataFrame()

# nhận dữ liệu, trả về ma trận tương đồng
@st.cache_resource
def build_similarity_model(df):
    if df.empty: return None
    # Vector hóa: Kết hợp Artist + Genre
    df['tags'] = df['artist'].astype(str)
    if 'genre' in df.columns:
        df['tags'] += " " + df['genre'].astype(str)
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(df['tags'])
    return cosine_similarity(vectors)

def get_content_based_recs(song_row, df, model, k=6):
    """Gợi ý dựa trên sự tương đồng (Cosine)"""
    try:
        idx = df[df['combined_name'] == song_row['combined_name']].index[0]
        distances = model[idx]
        indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:k+1]
        return [df.iloc[i[0]] for i in indices]
    except:
        return []

def get_context_recommendations(df, user_history=None):
    """
    LOGIC GỢI Ý ĐA NGỮ CẢNH (ĐÃ SỬA LỖI LOGIC BUỒN)
    """
    # 1. ƯU TIÊN 1: PHÂN TÍCH LỊCH SỬ NGHE (User-Centric)
    if user_history and len(user_history) >= 5:
        recent_5 = user_history[:5]
        # Lấy valence trung bình
        avg_valence = sum([x.get('valence', 0.5) for x in recent_5]) / 5
        
        print(f"Debug: Avg Valence = {avg_valence}") # Dòng này để bạn kiểm tra

        # LOGIC SỬA ĐỔI:
        if avg_valence < 0.3: 
            # Đang buồn -> Kéo mood lên (Gợi ý nhạc trung tính/vui nhẹ > 0.4)
            # Thay vì tìm < 0.4 như cũ
            return df[(df['valence'] > 0.4) & (df['valence'] < 0.7)].sample(8), "🌤️ Tâm trạng hơi chùng? Thử chút giai điệu tươi sáng hơn nhé."
        
        elif avg_valence > 0.6: 
            # Đang vui (như hoang123) -> Gợi ý nhạc vui (Bất kể preference là acoustic)
            return df[df['valence'] > 0.6].sample(8), "🔥 Bạn đang rất sung! Tiếp tục giữ nhiệt nào."

    # 2. ƯU TIÊN 2: NẾU KHÔNG CÓ LỊCH SỬ ĐỦ LỚN -> THEO GIỜ (System-Centric)
    hour = datetime.datetime.now().hour
    
    if 5 <= hour < 9: # Sáng
        cond = (df['energy'] > 0.7)
        msg = "🏃‍♂️ Chào buổi sáng! Nhạc Workout năng lượng."
    
    elif 9 <= hour < 17: # Giờ làm
        # Ưu tiên Instrumental hoặc nhạc vừa phải
        if 'instrumentalness' in df.columns:
            cond = (df['instrumentalness'] > 0.5) | ((df['energy'] > 0.3) & (df['energy'] < 0.7))
        else:
            cond = ((df['energy'] > 0.3) & (df['energy'] < 0.7))
        msg = "💻 Giờ làm việc tập trung (Focus Mode)."
        
    elif 17 <= hour < 22: # Tối
        cond = (df['popularity'] > 50) if 'popularity' in df.columns else (df['valence'] > 0.5)
        msg = "🌆 Buổi tối thư giãn với Top Hits."
        
    else: # Khuya
        cond = (df['energy'] < 0.4) & (df['valence'] < 0.5)
        msg = "🌙 Khuya rồi. Nhạc Chill dễ ngủ."
        
    # Lấy dữ liệu
    recs = df[cond]
    # Fallback: Nếu lọc ra ít quá thì lấy random
    if len(recs) < 8: 
        return df.sample(8), msg
        
    return recs.sample(8), msg

def search_songs(df, query):
    """Hàm tìm kiếm bài hát theo tên hoặc nghệ sĩ"""
    if not query: 
        return pd.DataFrame()
    
    # Chuyển query về chữ thường để tìm không phân biệt hoa thường
    query = query.lower()
    
    # Lọc dữ liệu: Tên bài chứa query HOẶC Tên nghệ sĩ chứa query
    # case=False: Không phân biệt hoa thường
    # na=False: Bỏ qua giá trị lỗi
    mask = df['song'].astype(str).str.contains(query, case=False, na=False) | \
           df['artist'].astype(str).str.contains(query, case=False, na=False)
           
    results = df[mask]
    
    # Trả về tối đa 20 kết quả để giao diện không bị dài quá
    return results.head(20)