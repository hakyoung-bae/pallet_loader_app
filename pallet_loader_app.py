
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rectpack import newPacker
import random

st.set_page_config(layout="wide")
st.title("📦 납축전지 1단 적재 패턴 시각화")

# 팔렛트 크기 입력
st.sidebar.header("팔렛트 크기 (mm)")
pallet_width = st.sidebar.number_input("가로", min_value=100, value=1200)
pallet_depth = st.sidebar.number_input("세로", min_value=100, value=1000)

# 품목 입력
st.sidebar.header("품목 입력 (모델명, 가로, 세로, 높이, 중량, 1단 적재수량)")
default_data = {
    "모델명": ["BCI65", "DIN66"],
    "가로(mm)": [300, 280],
    "세로(mm)": [180, 175],
    "높이(mm)": [200, 190],
    "중량(kg)": [20, 18],
    "1단 적재수량": [12, 15],
}
df = st.sidebar.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

if st.button("1단 적재 패턴 계산 및 시각화"):

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, pallet_width)
    ax.set_ylim(0, pallet_depth)
    ax.set_title("팔렛트 1단 적재 패턴")
    ax.set_xlabel("가로(mm)")
    ax.set_ylabel("세로(mm)")
    ax.invert_yaxis()
    ax.set_aspect('equal')

    total_weight = 0

    def random_color():
        return (random.random(), random.random(), random.random(), 0.6)

    for idx, row in df.iterrows():
        try:
            w = int(row["가로(mm)"])
            h = int(row["세로(mm)"])
            qty = int(row["1단 적재수량"])
            weight = float(row["중량(kg)"])
            model = row["모델명"]
        except Exception as e:
            st.error(f"입력값 오류 (행 {idx+1}): {e}")
            continue

        packer = newPacker(rotation=False)
        for _ in range(qty):
            packer.add_rect(w, h, rid=model)
        packer.add_bin(pallet_width, pallet_depth, float('inf'))
        packer.pack()

        rects = list(packer[0])
        placed_qty = len(rects)

        if placed_qty == 0:
            st.warning(f"❗ 모델 {model}: 팔렛트에 단 1개도 적재되지 않았습니다. 크기를 확인해주세요.")
            continue
        elif placed_qty < qty:
            st.warning(f"⚠️ 모델 {model}: 요청한 수량 {qty}개 중 {placed_qty}개만 적재되었습니다.")

        color = random_color()

        for rect in rects:
            try:
                x, y, rw, rh = rect[0], rect[1], rect[2], rect[3]
                rid = rect[4] if len(rect) > 4 else "제품"
            except Exception:
                continue
            rect_patch = Rectangle((x, y), rw, rh, facecolor=color, edgecolor='black', linewidth=1)
            ax.add_patch(rect_patch)
            ax.text(x + rw/2, y + rh/2, str(rid), ha='center', va='center', fontsize=8, color='black')

        item_weight = placed_qty * weight
        total_weight += item_weight

        st.write(f"모델명: **{model}**, 요청: {qty}개, 적재됨: {placed_qty}개, 단품 중량: {weight}kg → 총 중량: **{item_weight:.2f} kg**")

    st.write(f"### 팔렛트 1단 총 적재 중량: {total_weight:.2f} kg")
    st.pyplot(fig)
