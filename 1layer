
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from rectpack import newPacker

st.title("🔋 납축전지 1단 팔렛트 적재 시뮬레이터 (2D)")

st.sidebar.header("🛠️ 팔렛트 설정")
pallet_width = st.sidebar.number_input("팔렛트 가로 (mm)", value=1200)
pallet_depth = st.sidebar.number_input("팔렛트 세로 (mm)", value=1000)

st.sidebar.header("📦 배터리 모델 입력")

default_data = {
    "모델명": ["BCI65", "DIN66"],
    "가로(mm)": [300, 280],
    "세로(mm)": [180, 175],
}
df = st.sidebar.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

if st.button("📐 1단 적재 시뮬레이션 실행"):
    for idx, row in df.iterrows():
        model = row.get("모델명", f"모델{idx+1}")
        try:
            w = int(float(row["가로(mm)"]))
            h = int(float(row["세로(mm)"]))
        except (ValueError, TypeError, KeyError):
            st.warning(f"⚠️ {model}의 입력값이 올바르지 않습니다.")
            continue

        packer = newPacker(rotation=False)
        # 무한 수량으로 가정하고 최대한 배치
        for _ in range(999):
            packer.add_rect(w, h, rid=model)

        packer.add_bin(pallet_width, pallet_depth, float("inf"))
        packer.pack()

        rects = list(packer[0])
        total = len(rects)

        st.subheader(f"🧱 {model} (1단 최대 적재: {total}개)")

        fig, ax = plt.subplots(figsize=(6, 5))
        ax.set_title(f"{model} - 1단 적재 패턴")
        ax.set_xlim(0, pallet_width)
        ax.set_ylim(0, pallet_depth)
        ax.set_aspect('equal')

        for rect in rects:
            if len(rect) >= 5:
                x, y, rw, rh, rid = rect[:5]
            else:
                continue
            ax.add_patch(plt.Rectangle((x, y), rw, rh, fill=True, alpha=0.6))
            ax.text(x + rw/2, y + rh/2, str(rid), ha='center', va='center', fontsize=8)

        st.pyplot(fig)
