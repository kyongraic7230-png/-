import streamlit as st
import pandas as pd
import os
from PIL import Image, ImageDraw
from io import BytesIO
import datetime


# -----------------------------------------------------------
# CSV 파일 로드 함수 (오류 원인 출력)
# -----------------------------------------------------------
def load_products():
    possible_paths = [
        "products.csv",
        "./products.csv",
        os.path.join(os.getcwd(), "products.csv")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, encoding="utf-8")
                return df
            except:
                try:
                    df = pd.read_csv(path, encoding="cp949")
                    return df
                except Exception as e:
                    st.error(f"❗ CSV 파일은 존재하지만 읽을 수 없습니다.\n오류 내용: {e}")
                    return None

    # 여기까지 오면 파일 자체가 없음
    st.error("❗ products.csv 파일을 찾을 수 없습니다.\n"
             f"현재 실행 위치: {os.getcwd()}")
    return None


# -----------------------------------------------------------
# 세션 초기화
# -----------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "start"

if "cart" not in st.session_state:
    st.session_state.cart = []


# -----------------------------------------------------------
# 페이지 이동
# -----------------------------------------------------------
def go_to(page):
    st.session_state.page = page


# -----------------------------------------------------------
# PNG 생성 함수
# -----------------------------------------------------------
def create_png(text):
    img = Image.new("RGB", (800, 400), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), text, fill="black")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


# -----------------------------------------------------------
# 1. 시작 화면
# -----------------------------------------------------------
def page_start():
    st.title("🎯 미션 선택하기")
    mission = st.selectbox("미션을 선택하세요.", ["미션 1", "미션 2", "미션 3"])

    if st.button("선택 완료 → 쇼핑 화면으로 이동"):
        st.session_state.selected_mission = mission
        go_to("shopping")


# -----------------------------------------------------------
# 2. 쇼핑 화면
# -----------------------------------------------------------
def page_shopping():
    st.title("🛒 쇼핑하기")

    # 🔥 CSV 로드 시도
    products = load_products()

    # 파일을 못 읽으면 화면 렌더링 중단
    if products is None:
        st.stop()

    cols = st.columns(3)

    for idx, row in products.iterrows():
        with cols[idx % 3]:
            st.image(row["image_url"], width=150)
            st.write(f"**{row['name']}**")
            st.write(f"💰 가격: {int(row['price']):,}원")

            if st.button("담기", key=f"add_{idx}"):
                st.session_state.cart.append(row.to_dict())
                st.success(f"{row['name']} 담김!")

    st.markdown("---")

    st.subheader("🧺 장바구니")
    if len(st.session_state.cart) == 0:
        st.write("장바구니가 비어 있습니다.")
    else:
        total = sum(int(item["price"]) for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.write(f"- {item['name']} | {int(item['price']):,}원")
        st.write(f"**총액: {total:,}원**")

    if st.button("구매하기 → 결과 화면"):
        go_to("result")


# -----------------------------------------------------------
# 3. 결과 화면
# -----------------------------------------------------------
def page_result():
    st.title("📦 구매 결과")

    st.subheader("🛍 구매 품목")
    if len(st.session_state.cart) == 0:
        st.write("구매한 물품이 없습니다.")
    else:
        for item in st.session_state.cart:
            st.write(f"- {item['name']} | {int(item['price']):,}원")

    st.markdown("---")

    reason = st.text_area("구매 이유 작성", height=150)

    if st.button("제출(PNG로 저장)"):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        text = f"[구매 이유]\n{reason}\n\n제출 시각: {timestamp}"
        png = create_png(text)

        st.download_button(
            label="📥 PNG 다운로드",
            data=png,
            file_name=f"구매이유_{timestamp}.png",
            mime="image/png"
        )
        st.success("제출 완료!")


# -----------------------------------------------------------
# 라우팅
# -----------------------------------------------------------
if st.session_state.page == "start":
    page_start()
elif st.session_state.page == "shopping":
    page_shopping()
elif st.session_state.page == "result":
    page_result()
