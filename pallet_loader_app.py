
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import random

st.set_page_config(layout="wide")
st.title("📦 납축전지 1단 적재 패턴 시각화 (회전 허용 + 무게중심 표시)")

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
    ax.set_title("팔렛트 1단 적재 패턴 (회전 허용 + 무게중심)")
    ax.set_xlabel("가로(mm)")
    ax.set_ylabel("세로(mm)")
    ax.set_aspect('equal')

    total_weight = 0
    cg_sum_x = 0  # 무게중심 계산용 합산값
    cg_sum_y = 0

    def random_color():
        return (random.random(), random.random(), random.random(), 0.6)

    for idx, row in df.iterrows():
        try:
            model = row["모델명"]
            orig_w = int(row["가로(mm)"])
            orig_h = int(row["세로(mm)"])
            qty = int(row["1단 적재수량"])
            weight = float(row["중량(kg)"])
        except Exception as e:
            st.error(f"입력값 오류 (행 {idx+1}): {e}")
            continue

        color = random_color()
        x = 0
        y = 0
        placed = 0
        max_height_in_row = 0

        for i in range(qty):
            # 두 방향 중 현재 위치에 맞는 쪽을 선택
            can_place_normal = x + orig_w <= pallet_width and y + orig_h <= pallet_depth
            can_place_rotated = x + orig_h <= pallet_width and y + orig_w <= pallet_depth

            if not can_place_normal and not can_place_rotated:
                x = 0
                y += max_height_in_row
                max_height_in_row = 0

                can_place_normal = x + orig_w <= pallet_width and y + orig_h <= pallet_depth
                can_place_rotated = x + orig_h <= pallet_width and y + orig_w <= pallet_depth

                if not can_place_normal and not can_place_rotated:
                    st.warning(f"⚠️ 모델 {model}: 입력 수량 {qty}개 중 {placed}개만 적재됨 (팔렛트 초과).")
                    break

            # 최적 방향 선택
            if can_place_normal:
                w, h = orig_w, orig_h
            else:
                w, h = orig_h, orig_w

            # 그리기
            ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor='black', linewidth=1))
            ax.text(x + w / 2, y + h / 2, model, ha='center', va='center', fontsize=8, color='black')

            # 무게중심 계산용 합산
            center_x = x + w / 2
            center_y = y + h / 2
            cg_sum_x += center_x * weight
            cg_sum_y += center_y * weight
            total_weight += weight

            x += w
            placed += 1
            max_height_in_row = max(max_height_in_row, h)

        st.write(f"모델명: **{model}**, 요청: {qty}개, 적재됨: {placed}개, 단품 중량: {weight}kg → 총 중량: **{placed * weight:.2f} kg**")

    st.write(f"### 🧮 팔렛트 1단 총 적재 중량: {total_weight:.2f} kg")

    # 무게 중심 표시
    if total_weight > 0:
        cg_x = cg_sum_x / total_weight
        cg_y = cg_sum_y / total_weight
        ax.add_patch(Circle((cg_x, cg_y), radius=20, color='red', alpha=0.8))
        ax.text(cg_x, cg_y, "CG", ha='center', va='center', color='white', fontsize=10, weight='bold')
        st.success(f"무게 중심 좌표: ({cg_x:.1f}, {cg_y:.1f})")

    st.pyplot(fig)
    
