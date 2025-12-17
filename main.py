import streamlit as st
from modules import backend, ui, auth, visualization

st.set_page_config(layout="wide", page_title="Spotifake", page_icon="🎧")
st.markdown("""
<style>
    /* Ẩn Header mặc định của Streamlit */
    header {visibility: hidden;}
    /* Ẩn Footer mặc định */
    footer {visibility: hidden;}
    
    /* Chỉnh font chữ đẹp hơn */
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
        if st.button("🏠 Trang chủ"):
            st.session_state['current_page'] = 'Home'
            st.rerun()
            
        st.divider()
        # Nút Admin để xem biểu đồ báo cáo
        if st.button("📊 Xem Báo Cáo / Biểu đồ"):
            st.session_state['current_page'] = 'Dashboard'
            st.rerun()

    # 5. ROUTER (ĐIỀU HƯỚNG TRANG)
    page = st.session_state['current_page']
    
    if page == 'Home':
        st.title(f"Chào {st.session_state['username']}, hôm nay nghe gì?")
        
        # --- THANH TÌM KIẾM (SEARCH BAR) ---
        search_query = st.text_input("🔍 Tìm kiếm bài hát hoặc nghệ sĩ...", placeholder="Nhập tên bài hát (ví dụ: Alone, Chill...)")
        
        if search_query:
            # === TRƯỜNG HỢP 1: CÓ TÌM KIẾM ===
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
            # === TRƯỜNG HỢP 2: KHÔNG TÌM KIẾM (HIỆN GỢI Ý) ===
            
            # Lấy lịch sử (chỉ user thật mới có)
            history = []
            if not st.session_state['is_guest']:
                history = auth.get_history(st.session_state['username'])
            
            # SECTION 1: GỢI Ý NGỮ CẢNH & TÂM TRẠNG
            recs_ctx, msg_ctx = backend.get_context_recommendations(df, history)
            st.subheader(f"{msg_ctx}")
            
            cols = st.columns(4)
            for i, (idx, row) in enumerate(recs_ctx.iterrows()):
                with cols[i % 4]:
                    ui.render_song_card(row, i, "ctx")

            st.markdown("---")
            
            # SECTION 2: TRENDING (Ai cũng thấy)
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
        visualization.draw_charts(df)

if __name__ == "__main__":
    main()