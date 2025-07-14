
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import math
import random

st.set_page_config(layout="wide")
st.title("📦 납축전지 1단 적재 패턴 시각화 (중앙정렬 + 정사각형 패턴 + 무게중심 + 회전 지원)")

# 사이드바 입력
st.sidebar.header("팔렛트 크기 (mm)")
pallet_width = st.sidebar.number_input("팔렛트 가로", min_value=100, value=1200)
pallet_depth = st.sidebar.number_input("팔렛트 세로", min_value=100, value=1000)

st.sidebar.header("제품 입력 (1개 품목만 입력)")
default_data = {
    "모델명": ["BCI65"],
    "가로(mm)": [300],
    "세로(mm)": [180],
    "높이(mm)": [200],
    "중량(kg)": [20],
    "1단 적재수량": [12],
}
df = st.sidebar.data_editor(pd.DataFrame(default_data), num_rows=1)

if st.button("1단 적재 패턴 계산 및 시각화"):

    # 그래프 준비
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, pallet_width)
    ax.set_ylim(0, pallet_depth)
    ax.set_title("팔렛트 1단 적재 패턴")
    ax.set_xlabel("가로(mm)")
    ax.set_ylabel("세로(mm)")
    ax.set_aspect('equal')

    # 제품 정보 추출
    row = df.iloc[0]
    model = row["모델명"]
    pw = int(row["가로(mm)"])
    ph = int(row["세로(mm)"])
    qty = int(row["1단 적재수량"])
    weight = float(row["중량(kg)"])
    color = (random.random(), random.random(), random.random(), 0.6)

    # 가장 정사각형에 가까운 행×열 조합 찾기 (회전 포함)
    best_diff = float('inf')
    best_config = None
    for rotated in [False, True]:
        item_w, item_h = (pw, ph) if not rotated else (ph, pw)
        for r in range(1, qty + 1):
            c = math.ceil(qty / r)
            if r * c < qty:
                continue
            total_w = c * item_w
            total_h = r * item_h
            diff = abs(total_w - total_h)
            if total_w <= pallet_width and total_h <= pallet_depth and diff < best_diff:
                best_diff = diff
                best_config = (r, c, item_w, item_h, rotated)

    if best_config is None:
        st.error("❗ 어떤 방향으로도 제품을 적재할 수 없습니다. 수량이나 제품 크기를 조정하세요.")
        st.stop()

    rows, cols, pw_used, ph_used, rotated = best_config

    # 여유 공간 계산 (정중앙 정렬용)
    total_w = cols * pw_used
    total_h = rows * ph_used
    margin_x = (pallet_width - total_w) / 2
    margin_y = (pallet_depth - total_h) / 2

    if margin_x > 30 or margin_y > 30:
        st.info("💡 중앙 정렬을 위해 최대 30mm 완충재 공간 사용됨")

    if margin_x < 0 or margin_y < 0:
        st.error("❗ 제품이 팔렛트 크기를 초과합니다. 수량 또는 사이즈를 조정하세요.")
        st.stop()

    # 적재 및 무게중심 계산
    placed = 0
    cg_sum_x = 0
    cg_sum_y = 0
    total_weight = 0

    for r in range(rows):
        for c in range(cols):
            if placed >= qty:
                break
            x = margin_x + c * pw_used
            y = margin_y + r * ph_used

            ax.add_patch(Rectangle((x, y), pw_used, ph_used, facecolor=color, edgecolor='black'))
            ax.text(x + pw_used / 2, y + ph_used / 2, model, ha='center', va='center', fontsize=8)

            # 무게 중심 계산용
            cx = x + pw_used / 2
            cy = y + ph_used / 2
            cg_sum_x += cx * weight
            cg_sum_y += cy * weight
            total_weight += weight
            placed += 1

    # 무게 중심 위치
    cg_x = cg_sum_x / total_weight
    cg_y = cg_sum_y / total_weight
    ax.add_patch(Circle((cg_x, cg_y), radius=20, color='red', alpha=0.8))
    ax.text(cg_x, cg_y, "CG", ha='center', va='center', color='white', fontsize=10, weight='bold')

    # 오차 계산
    center_x = pallet_width / 2
    center_y = pallet_depth / 2
    offset_x = abs(cg_x - center_x)
    offset_y = abs(cg_y - center_y)

    # 출력
    st.write(f"### ✅ 적재 수량: {placed}개 / 총 중량: {total_weight:.1f}kg")
    st.success(f"무게 중심 좌표: ({cg_x:.1f}, {cg_y:.1f}) | "
               f"팔렛트 중심 대비 오차: X축 {offset_x:.1f}mm, Y축 {offset_y:.1f}mm")
    st.pyplot(fig)
