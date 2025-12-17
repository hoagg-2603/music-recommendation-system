import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

sns.set_theme(style="whitegrid")

def draw_charts(df):
    st.markdown("---")
    st.header("📊 Báo cáo Phân tích Dữ liệu (Admin)")
    
    tab1, tab2, tab3 = st.tabs(["Phân bố (Dist)", "Top Artist", "Tương quan (Corr)"])
    
    with tab1:
        st.subheader("Phân bố độ phổ biến bài hát")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(df['popularity'], bins=20, kde=True, color='#2ecc71', ax=ax)
        ax.set_title("Popularity Distribution")
        ax.axvline(df['popularity'].mean(), color='red', linestyle='--', label='Mean')
        ax.legend()
        st.pyplot(fig)
        
    with tab2:
        st.subheader("Top 10 Nghệ sĩ")
        top = df['artist'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=top.values, y=top.index, palette='viridis', ax=ax)
        st.pyplot(fig)
        
    with tab3:
        st.subheader("Tương quan Audio Features")
        nums = df.select_dtypes(include=[np.number])
        cols = [c for c in ['popularity','energy','valence','tempo','danceability'] if c in nums.columns]
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(nums[cols].corr(), annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
        st.pyplot(fig)