
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from rectpack import newPacker

st.title("📦 납축전지 팔렛트 적재 시뮬레이터 (2D)")

st.sidebar.header("🔧 팔렛트 설정")
pallet_width = st.sidebar.number_input("팔렛트 가로 (mm)", value=1200)
pallet_depth = st.sidebar.number_input("팔렛트 세로 (mm)", value=1000)
max_weight = st.sidebar.number_input("팔렛트 최대 적재 중량 (kg)", value=1000)

st.sidebar.header("🔋 배터리 모델 정보 입력")

default_data = {
    "모델명": ["BCI65", "DIN66"],
    "가로(mm)": [300, 280],
    "세로(mm)": [180, 175],
    "무게(kg)": [20, 18],
    "수량": [10, 10],
}
df = st.sidebar.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

if st.button("🚚 적재 최적화 실행"):

    packer = newPacker(rotation=False)

    for idx, row in df.iterrows():
        w, h, qty = int(row["가로(mm)"]), int(row["세로(mm)"]), int(row["수량"])
        for _ in range(qty):
            packer.add_rect(w, h, rid=row["모델명"])

    packer.add_bin(pallet_width, pallet_depth, float("inf"))

    packer.pack()

    total_pallets = len(packer)
    st.success(f"총 팔렛트 수: {total_pallets}")

    for i, abin in enumerate(packer):
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.set_title(f"팔렛트 #{i+1}")
        ax.set_xlim(0, pallet_width)
        ax.set_ylim(0, pallet_depth)
        ax.set_aspect('equal')

        for rect in abin:
            x, y, w, h, rid = rect
            ax.add_patch(plt.Rectangle((x, y), w, h, fill=True, alpha=0.6, label=str(rid)))
            ax.text(x + w/2, y + h/2, rid, ha='center', va='center', fontsize=8)

        st.pyplot(fig)
