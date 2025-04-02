import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

st.set_page_config(page_title="EDM 文案產生器", layout="centered")
st.title("📧 EDM 文案產生器（群眾集資專用）")

# 👉 使用者輸入欄位
project_url = st.text_input("專案網址")
project_name = ""
project_pitch = st.text_area("主要訴求／亮點")
target_audience = st.text_input("目標受眾")
tone_style = st.selectbox("語氣風格", ["活潑親切", "溫暖療癒", "使命感強烈", "理性專業", "潮流俐落"])
extra_info = st.text_area("補充資訊（選填）")

TEST_API_KEY = "sk-actual-demo-key-should-be-replaced"

# 解析網址內容
web_summary = ""
if project_url:
    try:
        response = requests.get(project_url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 🔍 自動判斷是否為 WaBay 專案頁面，抓取專案名稱
        parsed_url = urlparse(project_url)
        if "wabay.tw" in parsed_url.netloc and "/projects/" in parsed_url.path:
            possible_title = soup.find('div', class_="project-title")
            if not possible_title:
                possible_title = soup.find('div', class_="text-lg font-bold")
            if not possible_title:
                possible_title = soup.find('meta', attrs={"name": "description"})
            if possible_title:
                if hasattr(possible_title, 'text'):
                    project_name = possible_title.get_text(strip=True)
                elif possible_title.has_attr("content"):
                    project_name = possible_title["content"]

        if not project_name:
            project_name = st.text_input("專案名稱")
        else:
            st.markdown(f"**🔎 自動擷取專案名稱：** {project_name}")

        # 文字內容摘要
        title = soup.title.string if soup.title else ""
        paragraphs = soup.find_all('p')
        text_content = '\n'.join([p.get_text() for p in paragraphs[:10]])
        web_summary = title + '\n' + text_content
        st.text_area("🔍 網頁自動摘要內容（供 GPT 理解背景使用）", web_summary, height=200)

    except Exception as e:
        st.warning(f"無法解析該網址內容：{str(e)}")
        project_name = st.text_input("專案名稱")
else:
    project_name = st.text_input("專案名稱")

# 👉 當按下按鈕後產生文案
if st.button("產生 EDM 文案（限測試 50 次）"):
    openai.api_key = TEST_API_KEY

    # Prompt 設定
    prompt = f"""
你是一位資深文案撰寫人，擅長撰寫 punchy、精煉且具有感召力的群眾集資宣傳文案。請根據以下專案資訊，撰寫一段短篇 EDM 文案（150字以內），需符合以下條件：

文字節奏活潑、有力，具備吸睛開場＋情境鋪陳＋行動召喚。
切中專案的核心亮點或議題（如永續、教育、共融、創新等），用詞需簡潔有層次。
語氣符合該專案的風格（例：溫暖、理性、感性、趣味、使命感等）。
不違反任何平台規範、無誤導性、善良風俗與公共道德。
可適度使用 emoji，但需自然、加分不干擾閱讀。
書寫時每一句都要換行。
文末加入一句 CTA（行動號召語），並以「▸」結尾。

請依據下列專案資訊進行撰寫：
【專案網址解析摘要】：{web_summary}
【專案名稱】：{project_name}
【主要訴求／亮點】：{project_pitch}
【目標受眾】：{target_audience}
【語氣風格】：{tone_style}
【補充資訊】：{extra_info}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        result = response.choices[0].message["content"].strip()
        st.subheader("✍️ 產出文案")
        st.write(result)
    except Exception as e:
        st.error(f"產生文案時發生錯誤：{str(e)}")
