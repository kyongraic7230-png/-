import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from io import BytesIO
import datetime

# -----------------------------------------------------------
# 세션 상태 초기화
# -----------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "start"

if "cart" not in st.session_state:
    st.session_state.cart = []

# -----------------------------------------------------------
# 페이지 이동 함수
# -----------------------------------------------------------
def go_to(page):
    st.session_state.page = page

# -----------------------------------------------------------
# PNG 파일 생성 함수
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
    st.write("미션을 선택하면 쇼핑을 시작할 수 있습니다.")

    mission = st.selectbox(
        "미션을 선택하세요",
        ["미션 1", "미션 2", "미션 3"]
    )

    if st.button("선택 완료 → 쇼핑 화면으로 이동"):
        st.session_state.selected_mission = mission
        go_to("shopping")

# -----------------------------------------------------------
# 2. 쇼핑 화면
# -----------------------------------------------------------
def page_shopping():
    st.title("🛒 쇼핑하기")
    st.write("상품을 선택하여 장바구니에 담아보세요!")

    # CSV 불러오기
    try:
        products = pd.read_csv("products(1).csv")
    except:
        st.error("❗ products.csv 파일을 불러올 수 없습니다. 같은 폴더에 있는지 확인해주세요.")
        return

    # 3열 그리드로 상품 배치
    cols = st.columns(3)
    
    for idx, row in products.iterrows():
        col = cols[idx % 3]

        with col:
            # 이미지
            try:
                st.image(row["image_url"], width=150)
            except:
                st.write("(이미지를 불러올 수 없습니다)")

            # 정보 출력
            st.write(f"**{row['name']}**")
            st.write(f"💰 가격: {int(row['price']):,}원")

            # 담기 버튼
            if st.button("담기", key=f"add_{idx}"):
                st.session_state.cart.append(row.to_dict())
                st.success(f"{row['name']} 담김!")

    st.markdown("---")

    # 장바구니 표시
    st.subheader("🧺 장바구니")
    if len(st.session_state.cart) == 0:
        st.write("장바구니가 비어 있습니다.")
    else:
        total = 0
        for item in st.session_state.cart:
            st.write(f"- {item['name']} | {int(item['price']):,}원")
            total += int(item["price"])
        st.write(f"**총액: {total:,}원**")

    # 다음 페이지로 이동
    if st.button("구매하기 → 결과 화면으로 이동"):
        go_to("result")

# -----------------------------------------------------------
# 3. 결과 화면
# -----------------------------------------------------------
def page_result():
    st.title("📦 구매 결과")
    st.write("내가 선택한 물품을 확인하고 구매 이유를 적어 제출하세요.")

    # 구매 목록 표시
    if len(st.session_state.cart) == 0:
        st.write("아무것도 구매하지 않았습니다.")
    else:
        st.subheader("🛍️ 구매 품목")
        for item in st.session_state.cart:
            st.write(f"- {item['name']} | {int(item['price']):,}원")

    st.markdown("---")

    # 구매 이유 입력
    st.subheader("✏ 구매 이유 작성")
    reason = st.text_area("왜 이 물건을 선택했나요?", height=150)

    if st.button("제출(PNG로 저장)"):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        text = f"[구매 이유]\n{reason}\n\n제출 시각: {timestamp}"
        png_file = create_png(text)

        # 다운로드 버튼
        st.download_button(
            label="📥 PNG 다운로드",
            data=png_file,
            file_name=f"구매이유_{timestamp}.png",
            mime="image/png"
        )

        st.success("제출 완료!")

# -----------------------------------------------------------
# 페이지 라우팅
# -----------------------------------------------------------
if st.session_state.page == "start":
    page_start()
elif st.session_state.page == "shopping":
    page_shopping()
elif st.session_state.page == "result":
    page_result()
