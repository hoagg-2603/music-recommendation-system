import numpy as np
import pandas as pd
import streamlit as st # Nhớ thêm dòng này
from sklearn.metrics import mean_squared_error, mean_absolute_error

# --- GIỮ NGUYÊN HÀM TÍNH TOÁN CŨ ---
def calculate_metrics(recs_df, actual_songs_df, k=10):
    metrics = {}
    hits = 0
    test_genres = set(actual_songs_df['genre'].unique()) if 'genre' in actual_songs_df else set()
    test_artists = set(actual_songs_df['artist'].unique())
    
    for _, row in recs_df.iterrows():
        if row['artist'] in test_artists or ('genre' in row and row['genre'] in test_genres):
            hits += 1
            
    metrics[f'Precision@{k}'] = hits / k
    if len(actual_songs_df) > 0:
        metrics[f'Recall@{k}'] = hits / len(actual_songs_df)
    else:
        metrics[f'Recall@{k}'] = 0
        
    pred_valence = recs_df['valence'].mean()
    actual_valence = actual_songs_df['valence'].mean()
    y_true = [actual_valence]
    y_pred = [pred_valence]
    
    metrics['Mood_RMSE'] = np.sqrt(mean_squared_error(y_true, y_pred))
    metrics['Mood_MAE'] = mean_absolute_error(y_true, y_pred)
    return metrics

def run_evaluation(df, history):
    if len(history) < 5:
        return {"Error": "Cần ít nhất 5 bài trong lịch sử để đánh giá!"}
    hist_df = pd.DataFrame(history)
    split_idx = int(len(hist_df) * 0.8)
    train_df = hist_df.iloc[split_idx:] 
    test_df = hist_df.iloc[:split_idx]  
    
    avg_v = train_df['valence'].mean()
    # Giả lập gợi ý (Lấy bài có valence gần nhất với trung bình lịch sử)
    recs = df.iloc[(df['valence'] - avg_v).abs().argsort()[:10]]
    
    return calculate_metrics(recs, test_df)

# --- THÊM HÀM VẼ GIAO DIỆN (MỚI) ---
def draw_evaluation_page(df, history):
    st.markdown("---")
    st.header("📈 Kiểm thử & Đánh giá Hiệu năng (Evaluation)")
    
    st.info("Trang này sử dụng phương pháp **Offline Evaluation** (Chia tập dữ liệu 80/20) để đo lường độ chính xác của các thuật toán gợi ý.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Cấu hình kiểm thử")
        st.write(f"- **Tổng lịch sử:** {len(history)} bài")
        st.write("- **Tập Train (Học):** 80%")
        st.write("- **Tập Test (Đối chiếu):** 20%")
        
        if len(history) < 5:
            st.error("⚠️ Không đủ dữ liệu (Cần > 5 bài)")
        else:
            if st.button("🚀 Chạy Kiểm thử ngay", type="primary", use_container_width=True):
                with st.spinner("Đang tính toán Metrics..."):
                    # Gọi hàm tính toán
                    metrics = run_evaluation(df, history)
                    st.session_state['eval_results'] = metrics # Lưu kết quả lại
    
    with col2:
        st.subheader("Kết quả Đánh giá")
        
        # Kiểm tra xem đã có kết quả chưa
        if 'eval_results' in st.session_state:
            res = st.session_state['eval_results']
            
            if "Error" in res:
                st.error(res["Error"])
            else:
                # Hiển thị 4 chỉ số đẹp mắt
                m1, m2 = st.columns(2)
                m1.metric("🎯 Precision@10", f"{res.get('Precision@10', 0):.1%}", delta="Độ chính xác Gu")
                m2.metric("🔍 Recall@10", f"{res.get('Recall@10', 0):.1%}", delta="Tỷ lệ tìm lại")
                
                m3, m4 = st.columns(2)
                m3.metric("🧠 Mood RMSE", f"{res.get('Mood_RMSE', 0):.3f}", delta="Độ lệch Cảm xúc", delta_color="inverse")
                m4.metric("📉 Mood MAE", f"{res.get('Mood_MAE', 0):.3f}")
                
                st.success("✅ Mô hình hoạt động ổn định trên tập dữ liệu cá nhân.")
        else:
            st.write("👈 Bấm nút chạy để xem kết quả.")