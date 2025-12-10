import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from io import BytesIO
import datetime

# -------------------------------------------------
# 초기 세션 상태 생성
# -------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "start"

if "cart" not in st.session_state:
    st.session_state.cart = []

# -------------------------------------------------
# 페이지 이동 함수
# -------------------------------------------------
def go_to(page_name):
    st.session_state.page = page_name


# -------------------------------------------------
# PNG 파일 생성 함수
# -------------------------------------------------
def create_png(text):
    img = Image.new("RGB", (800, 400), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), text, fill="black")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


# -------------------------------------------------
# 1. 시작 화면
# -------------------------------------------------
def page_start():
    st.title("🎯 미션 선택하기")
    st.write("학생은 미션을 선택한 후 쇼핑을 진행합니다.")

    missions = ["미션 1", "미션 2", "미션 3"]

    selected_mission = st.radio("미션을 선택하세요.", missions)

    if st.button("미션 선택 완료 → 쇼핑화면으로 이동"):
        st.session_state.selected_mission = selected_mission
        go_to("shopping")


# -------------------------------------------------
# 2. 쇼핑 화면
# -------------------------------------------------
def page_shopping():
    st.title("🛒 쇼핑하기")
    st.write("원하는 물품을 선택하여 장바구니에 담으세요.")

    # CSV 불러오기
    products = pd.read_csv("products.csv")

    cols = st.columns(3)

    for i, row in products.iterrows():
        with cols[i % 3]:
            st.image(row["image_url"], width=150)
            st.write(f"**{row['name']}**")
            st.write(f"💰 가격: {row['price']}원")

            if st.button(f"담기 — {row['name']}", key=f"add_{i}"):
                st.session_state.cart.append(row.to_dict())
                st.success(f"{row['name']} 이(가) 장바구니에 추가되었습니다!")

    st.markdown("---")

    st.subheader("🧺 현재 장바구니")
    if len(st.session_state.cart) == 0:
        st.write("장바구니가 비어 있습니다.")
    else:
        for item in st.session_state.cart:
            st.write(f"- {item['name']} ({item['price']}원)")

    if st.button("구매하기 → 결과화면으로 이동"):
        go_to("result")


# -------------------------------------------------
# 3. 결과 화면
# -------------------------------------------------
def page_result():
    st.title("📦 구매 결과")

    st.subheader("🛍️ 구매한 물품 목록")
    if len(st.session_state.cart) == 0:
        st.write("아직 구매한 물품이 없습니다.")
    else:
        for item in st.session_state.cart:
            st.write(f"- {item['name']} ({item['price']}원)")

    st.markdown("---")

    st.subheader("✏️ 구매 이유 작성")
    reason = st.text_area("구매 이유를 작성하세요.", height=150)

    if st.button("제출(PNG로 출력)"):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        text = f"[구매 이유]\n{reason}\n\n제출 시각: {timestamp}"
        png_file = create_png(text)

        st.download_button(
            label="📥 PNG 다운로드",
            data=png_file,
            file_name=f"구매이유_{timestamp}.png",
            mime="image/png"
        )

        st.success("제출이 완료되었습니다!")


# -------------------------------------------------
# 페이지 라우팅
# -------------------------------------------------
if st.session_state.page == "start":
    page_start()
elif st.session_state.page == "shopping":
    page_shopping()
elif st.session_state.page == "result":
    page_result()
