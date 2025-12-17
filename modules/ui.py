import streamlit as st
from . import auth, visualization

def render_login():
    st.title("🎧 Music Pro System")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Đăng nhập")
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Login"):
            if auth.login(u, p):
                st.session_state['logged_in'] = True
                st.session_state['username'] = u
                st.session_state['is_guest'] = False
                st.rerun()
            else: st.error("Sai thông tin!")

    with c2:
        st.subheader("Đăng ký")
        nu = st.text_input("New Username", key="r_u")
        np = st.text_input("New Password", type="password", key="r_p")
        if st.button("Register"):
            ok, msg = auth.register(nu, np)
            if ok: st.success(msg)
            else: st.error(msg)
            
    st.divider()
    if st.button("🚀 Nghe nhạc với tư cách KHÁCH (Guest Mode)", type="primary"):
        st.session_state['is_guest'] = True
        st.session_state['username'] = "Khách"
        st.rerun()

def render_song_card(row, index, key_prefix="card"):
    """Vẽ 1 thẻ bài hát nhỏ"""
    st.info(f"🎵 **{row['song']}**")
    st.caption(f"{row['artist']}")
    if st.button("Play ▶", key=f"{key_prefix}_{index}"):
        st.session_state['playing_song'] = row
        st.session_state['current_page'] = 'Player'
        st.rerun()

def render_player(song, df, model, is_guest=False):
    """Giao diện Trình phát nhạc"""
    if st.button("⬅ Quay lại Home"):
        st.session_state['current_page'] = 'Home'
        st.rerun()
        
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image("https://cdn-icons-png.flaticon.com/512/3208/3208767.png", width=200)
        st.markdown(f"### {song['song']}")
        st.markdown(f"**{song['artist']}**")
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") # Nhạc demo
        
        # Chỉ User thật mới được lưu lịch sử
        if not is_guest:
            auth.save_history(st.session_state['username'], song)
            st.toast("✅ Đã lưu vào lịch sử nghe")
    
    with c2:
        st.subheader("✨ Gợi ý tương tự (Content-Based)")
        # Import local để tránh vòng lặp
        from . import backend
        recs = backend.get_content_based_recs(song, df, model)
        
        for i, r in enumerate(recs):
            with st.container():
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"**{r['song']}** - {r['artist']}")
                if col_b.button("Nghe", key=f"rec_{i}"):
                    st.session_state['playing_song'] = r
                    st.rerun()

def render_onboarding(df, username):
    st.title(f"👋 Chào mừng {username}!")
    st.markdown("### Để Music Pro hiểu gu của bạn, hãy chọn ít nhất 3 thể loại.")
    st.progress(0)

    # 1. Lấy danh sách thể loại từ file CSV
    if 'genre' in df.columns:
        all_genres = df['genre'].unique().tolist()
    else:
        all_genres = ['Pop', 'Rock', 'Indie', 'Hip-Hop', 'Jazz', 'Classical']
    
    # Form chọn
    with st.form("onboarding_form"):
        st.write("Bạn thích thể loại nào?")
        selected_genres = st.multiselect("Chọn thể loại", options=all_genres[:50]) # Lấy 50 cái đầu cho đỡ lag
        
        st.write("Nghệ sĩ yêu thích?")
        top_artists = df['artist'].value_counts().head(20).index.tolist()
        selected_artists = st.multiselect("Chọn nghệ sĩ", options=top_artists)
        
        submitted = st.form_submit_button("Bắt đầu")
        
        if submitted:
            if len(selected_genres) < 1:
                st.error("Hãy chọn ít nhất 1 thể loại!")
            else:
                # Gọi hàm lưu bên auth
                auth.save_onboarding(username, selected_genres, selected_artists)
                st.success("Đã lưu sở thích! Đang vào trang chủ...")
                st.rerun() # Load lại trang để vào Home

def render_song_card(row, index, key_prefix="card"):
    """Vẽ 1 thẻ bài hát nhỏ kèm chỉ số Mood"""
    
    # 1. Lấy chỉ số (Ép kiểu float để tránh lỗi)
    val = float(row.get('valence', 0.5))
    en = float(row.get('energy', 0.5))
    
    # 2. Xác định nhãn cảm xúc (Logic hiển thị)
    mood_icon = "🎵 Chill" # Mặc định
    color = "blue"
    
    if val >= 0.7 and en >= 0.6:
        mood_icon = f"🤩 Vui (v:{val:.1f})"
    elif val <= 0.4:
        mood_icon = f"😔 Buồn (v:{val:.1f})"
    elif en >= 0.8:
        mood_icon = f"⚡ (e:{en:.1f})"
    elif en <= 0.4 and val <= 0.5:
        mood_icon = f"🌙 Ngủ (e:{en:.1f})"
        
    # 3. Vẽ thẻ
    # Dùng st.container để đóng khung đẹp hơn
    with st.container(border=True):
        st.markdown(f"**{row['song']}**")
        st.caption(f"{row['artist']}")
        
        # Hiển thị Mood
        st.markdown(f"**{mood_icon}**")
        
        # Nút Play
        if st.button("Play ▶", key=f"{key_prefix}_{index}", use_container_width=True):
            st.session_state['playing_song'] = row
            st.session_state['current_page'] = 'Player'
            st.rerun()