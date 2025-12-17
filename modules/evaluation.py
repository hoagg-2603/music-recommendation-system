import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error

def calculate_metrics(recs_df, actual_songs_df, k=10):
    """
    Tính toán các chỉ số đánh giá
    - recs_df: DataFrame các bài hát được gợi ý
    - actual_songs_df: DataFrame các bài hát user thực sự nghe (Tập Test)
    """
    metrics = {}
    
    # 1. Precision@K: Tỉ lệ bài gợi ý "trúng" gu (dựa trên trùng Genre hoặc Artist)
    # (Do không có dữ liệu user thật nghe gì tiếp theo chính xác 100%, ta đánh giá dựa trên độ tương đồng)
    hits = 0
    test_genres = set(actual_songs_df['genre'].unique()) if 'genre' in actual_songs_df else set()
    test_artists = set(actual_songs_df['artist'].unique())
    
    for _, row in recs_df.iterrows():
        # Coi là "trúng" nếu cùng thể loại hoặc cùng ca sĩ với tập test
        if row['artist'] in test_artists or ('genre' in row and row['genre'] in test_genres):
            hits += 1
            
    metrics[f'Precision@{k}'] = hits / k
    
    # 2. Recall@K: Tỉ lệ bài "trúng" tìm được trên tổng số bài user thích
    # (Ở đây định nghĩa user thích là tập Test)
    if len(actual_songs_df) > 0:
        metrics[f'Recall@{k}'] = hits / len(actual_songs_df)
    else:
        metrics[f'Recall@{k}'] = 0
        
    # 3. RMSE & MAE cho Bài toán Dự đoán Cảm xúc (Mood Prediction)
    # So sánh Valence trung bình gợi ý vs Valence thực tế user nghe
    pred_valence = recs_df['valence'].mean()
    actual_valence = actual_songs_df['valence'].mean()
    
    # Vì đây là 2 con số scalar, RMSE = MAE = độ lệch tuyệt đối
    # Để chuyên nghiệp hơn, ta giả lập vector 
    y_true = [actual_valence]
    y_pred = [pred_valence]
    
    metrics['Mood_RMSE'] = np.sqrt(mean_squared_error(y_true, y_pred))
    metrics['Mood_MAE'] = mean_absolute_error(y_true, y_pred)
    
    return metrics

def run_evaluation(df, history):
    """Hàm chạy demo đánh giá để hiển thị lên UI"""
    if len(history) < 5:
        return {"Error": "Cần ít nhất 5 bài trong lịch sử để đánh giá!"}
    
    # Chuyển lịch sử thành DataFrame
    hist_df = pd.DataFrame(history)
    
    # Chia tập Train/Test (Hold-out strategy)
    # Lấy 20% bài nghe gần nhất làm tập Test (Ground Truth)
    split_idx = int(len(hist_df) * 0.8)
    train_df = hist_df.iloc[split_idx:] # Những bài cũ làm nền tảng
    test_df = hist_df.iloc[:split_idx]  # Những bài mới nghe (ngược vì history xếp mới nhất lên đầu)
    
    # Giả lập gọi hàm gợi ý từ backend (cần import backend ở ngoài)
    # Ở đây ta giả lập lấy random từ tập có valence tương đồng để demo logic
    avg_v = train_df['valence'].mean()
    recs = df.iloc[(df['valence'] - avg_v).abs().argsort()[:10]]
    
    return calculate_metrics(recs, test_df)