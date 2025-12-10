import streamlit as st
import pandas as pd
import os
from PIL import Image, ImageDraw
from io import BytesIO
import datetime


# --------------------------------------------------------
# CSV 로드 & 필요한 column 자동 매핑
# --------------------------------------------------------
def load_products():
    possible_paths = ["products.csv", "./products.csv", os.path.join(os.getcwd(), "products.csv")]

    path_found = None
    for p in possible_paths:
        if os.path.exists(p):
            path_found = p
            break

    if path_found is None:
        st.error("❗ products.csv 파일이 없습니다.")
        return None, None

    # 여러 인코딩으로 로드 시도
    df = None
    for enc in ["utf-8", "cp949", "utf-8-sig"]:
        try:
            df = pd.read_csv(path_found, encoding=enc)
            break
        except:
            continue

    if df is None:
        st.error("❗ CSV 파일을 읽을 수 없습니다. 인코딩 오류입니다.")
        return None, None

    # --------------------------------------------------------
    # 필요한 column 자동 감지
    # --------------------------------------------------------
    columns = df.columns.str.lower()

    # 이름 후보
    name_cols = ["name", "product", "product_name", "title", "품명"]
    price_cols = ["price", "cost", "가격"]
    image_cols = ["image_url", "image", "img", "img_url", "url", "이미지"]

    name_col = next((c for c in columns if c in name_cols), None)
    price_col = next((c for c in columns if c in price_cols), None)
    image_col = next((c for c in columns if c in image_cols), None)

    # 실제 df에서 원래 column 이름 찾기
    mapping = {}
    if name_col:
        mapping["name"] = df.columns[columns.tolist().index(name_col)]
    if price_col:
        mapping["price"] = df.columns[columns.tolist().index(price_col)]
    if image_col:
        mapping["image_url"] = df.columns[columns.tolist().index(image_col)]

    # 필요한 column이 없으면 에러 표시
    missing = []
    if "name" not in mapping:
        missing.append("상품명(name)")
    if "price" not in mapping:
        missing.append("가격(price)")
    if "image_url" not in mapping:
        missing.append("이미지(image_url)")

    if missing:
        st.error("❗ CSV 파일에 아래 열이 없습니다:\n" + ", ".join(missing))
        st.write("현재 CSV 열:", list(df.columns))
        return None, None

    return df, mapping


# --------------------------------------------------------
# PNG 생성 함수
# --------------------------------------------------------
def create_png(text):
    img = Image.new("RGB", (800, 400), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), text, fill="black")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


# --------------------------------------------------------
# 세션 초기화
# --------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "start"

if "cart" not in st.session_state:
    st.session_state.cart = []


def go_to(page):
    st.session_state.page = page


# --------------------------------------------------------
# 1. 시작 화면
# --------------------------------------------------------
def page_start():
    st.title("🎯 미션 선택하기")

    mission = st.selectbox("미션을 선택하세요", ["미션 1", "미션 2", "미션 3"])

    if st.button("선택 완료 → 쇼핑화면"):
        st.session_state.selected_mission = mission
        go_to("shopping")


# --------------------------------------------------------
# 2. 쇼핑 화면
# --------------------------------------------------------
def page_shopping():
    st.title("🛒 쇼핑하기")

    df, mapping = load_products()

    if df is None:
        st.stop()

    cols = st.columns(3)

    for idx, row in df.iterrows():
        col = cols[idx % 3]

        with col:
            st.image(row[mapping["image_url"]], width=150)

            st.write(f"**{row[mapping['name']]}**")
            st.write(f"💰 가격: {int(row[mapping['price']]):,}원")

            if st.button("담기", key=f"add_{idx}"):
                st.session_state.cart.append(row.to_dict())
                st.success("담았습니다!")


    st.markdown("---")
    st.subheader("🧺 장바구니")

    total = 0
    for item in st.session_state.cart:
        total += int(item[mapping["price"]])
        st.write(f"- {item[mapping['name']]} | {int(item[mapping['price']]):,}원")

    st.write(f"**총 금액: {total:,}원**")

    if st.button("구매하기 → 결과 화면"):
        go_to("result")


# --------------------------------------------------------
# 3. 결과 화면
# --------------------------------------------------------
def page_result():
    st.title("📦 구매 결과")

    st.subheader("🛍 구매 목록")
    for item in st.session_state.cart:
        st.write(item)

    st.markdown("---")

    reason = st.text_area("구매 이유 작성")

    if st.button("제출(PNG 저장)"):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        text = f"[구매 이유]\n{reason}\n\n제출 시각: {timestamp}"
        png = create_png(text)

        st.download_button(
            label="📥 PNG 다운로드",
            data=png,
            file_name=f"reason_{timestamp}.png",
            mime="image/png"
        )
        st.success("제출 완료!")


# --------------------------------------------------------
# 페이지 이동
# --------------------------------------------------------
if st.session_state.page == "start":
    page_start()
elif st.session_state.page == "shopping":
    page_shopping()
elif st.session_state.page == "result":
    page_result()
