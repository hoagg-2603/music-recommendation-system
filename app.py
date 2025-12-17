import streamlit as st
# 1. Thêm import evaluation
from modules import backend, ui, auth, visualization, evaluation 

st.set_page_config(layout="wide", page_title="Spotifake", page_icon="🎧")
st.markdown("""
<style>
    /* Ẩn Header/Footer mặc định */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Làm đẹp nút bấm */
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE SETUP ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'is_guest' not in st.session_state: st.session_state['is_guest'] = False
if 'username' not in st.session_state: st.session_state['username'] = None
if 'current_page' not in st.session_state: st.session_state['current_page'] = 'Home'

def main():
    # 1. LOAD DATA
    df = backend.load_and_clean_data()
    if df.empty:
        st.error("❌ Lỗi: Không tìm thấy file 'data/dataset.csv'. Hãy kiểm tra lại thư mục!")
        return
    model = backend.build_similarity_model(df)

    # 2. KIỂM TRA ĐĂNG NHẬP
    if not st.session_state['logged_in'] and not st.session_state['is_guest']:
        ui.render_login()
        return

    # 3. KIỂM TRA ONBOARDING (CHỈ USER)
    if not st.session_state['is_guest']:
        username = st.session_state['username']
        if not auth.check_onboarding_status(username):
            ui.render_onboarding(df, username)
            return

    # 4. SIDEBAR (MENU)
    with st.sidebar:
        st.header(f"👤 {st.session_state['username']}")
        
        if st.session_state['is_guest']:
            st.warning("Bạn đang là Khách. Lịch sử sẽ không được lưu.")
            if st.button("🔑 Đăng nhập ngay"):
                st.session_state['is_guest'] = False
                st.rerun()
        else:
            if st.button("🚪 Đăng xuất"):
                st.session_state['logged_in'] = False
                st.rerun()
        
        st.divider()
        # NÚT 1: TRANG CHỦ
        if st.button("🏠 Trang chủ"):
            st.session_state['current_page'] = 'Home'
            st.rerun()
            
        st.divider()
        st.caption("Công cụ Admin")
        
        # NÚT 2: BÁO CÁO (DASHBOARD)
        if st.button("📊 Xem Báo Cáo / Biểu đồ"):
            st.session_state['current_page'] = 'Dashboard'
            st.rerun()

        # NÚT 3: ĐÁNH GIÁ (TRANG MỚI)
        if st.button("📈 Đánh giá Hiệu năng"):
            st.session_state['current_page'] = 'Evaluation'
            st.rerun()

    # 5. ROUTER (ĐIỀU HƯỚNG TRANG)
    page = st.session_state['current_page']
    
    # Lấy lịch sử chung (Dùng cho cả Home và Evaluation)
    history = []
    if not st.session_state['is_guest']:
        history = auth.get_history(st.session_state['username'])
    
    if page == 'Home':
        st.title(f"Chào {st.session_state['username']}, hôm nay nghe gì?")
        
        # --- THANH TÌM KIẾM ---
        search_query = st.text_input("🔍 Tìm kiếm bài hát hoặc nghệ sĩ...", placeholder="Nhập tên bài hát (ví dụ: Alone, Chill...)")
        
        if search_query:
            st.subheader(f"Kết quả tìm kiếm cho: '{search_query}'")
            results = backend.search_songs(df, search_query)
            
            if not results.empty:
                cols = st.columns(4)
                for i, (idx, row) in enumerate(results.iterrows()):
                    with cols[i % 4]:
                        ui.render_song_card(row, i, "search")
            else:
                st.warning("Không tìm thấy bài hát nào!")
        
        else:
            # === HIỆN GỢI Ý THÔNG MINH ===
            
            # 1. Lấy chỉ số Profile Valence (Gu trung bình)
            user_profile_val = 0.5
            if not st.session_state['is_guest']:
                # Load thông tin user để lấy profile_valence
                u_data = auth.load_users().get(st.session_state['username'], {})
                user_profile_val = u_data.get('profile_valence', 0.5)

            # 2. Gọi hàm gợi ý (Truyền thêm user_profile_val)
            recs_ctx, msg_ctx = backend.get_context_recommendations(df, history, user_profile_val)
            
            st.subheader(f"{msg_ctx}")
            
            cols = st.columns(4)
            for i, (idx, row) in enumerate(recs_ctx.iterrows()):
                with cols[i % 4]:
                    ui.render_song_card(row, i, "ctx")

            st.markdown("---")
            
            # SECTION 2: TRENDING
            st.subheader("🔥 Top Thịnh hành")
            trending = df.sort_values('popularity', ascending=False).head(4)
            cols2 = st.columns(4)
            for i, (idx, row) in enumerate(trending.iterrows()):
                with cols2[i % 4]:
                    ui.render_song_card(row, i, "trd")

    elif page == 'Player':
        song = st.session_state.get('playing_song')
        if song is not None:
            ui.render_player(song, df, model, st.session_state['is_guest'])
            
    elif page == 'Dashboard':
        # Trang Dashboard cũ
        visualization.draw_charts(df) # Chỉ vẽ biểu đồ thống kê

    elif page == 'Evaluation':
        # TRANG ĐÁNH GIÁ MỚI
        # Gọi hàm vẽ giao diện từ module evaluation
        evaluation.draw_evaluation_page(df, history)

if __name__ == "__main__":
    main()