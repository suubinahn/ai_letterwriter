import streamlit as st
from openai import OpenAI
from PIL import Image

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

st.title("💌 AI_레터라이터")
st.subheader("AI를 이용하여 특별한 '새해편지'를 작성해보세요!")
st.write("'새해 인사'를 전하고 싶지만 어떤 말을 전해야 좋을지 고민인 당신! AI_레터라이터를 통해 특별한 새해 편지를 작성해 보세요! 떠오르는 사람의 이름과 나이 그리고 그 대상을 표현하기 좋은 간단한 정보만 입력해 주면 끝! 편지 내용의 성격을 결정지을 MBTI 유형 및 작성 모드 그리고 내용에 포함시키고자 하는 키워드까지 더해주면 더욱 특별한 편지가 생성된답니다.")
local_image_path = "love-letter.png"
image = Image.open(local_image_path)
resized_image = image.resize((200, 215))
#st.image(resized_image, caption='Downloaded Image')
def image_to_base64(image):
    import base64
    from io import BytesIO

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
st.markdown(
    f'<div style="display: flex; justify-content: center;"><img src="data:image/png;base64,{image_to_base64(resized_image)}" width="300"></div>',
    unsafe_allow_html=True,
)

auto_complete = st.toggle(label="예시로 채우기")
example = {
    "name": "봉석",
    "age": "19",
    "desc": "예쁜 미소가 초능력인 사람",
    "mbti": "ENFP",
    "mode": "존댓말",
    "keyword_1": ["행복", "", ""]
}
def generate_prompt(user_name, user_age, user_desc, user_mbti, user_mode, max_length, keywords): # num, # user_mbti, # user_mode
    prompt = f"""
이름과 나이 그리고 간단 정보와 어울리는 재치있는 새해 편지를 생성해주세요.
반드시 {max_length} 단어 이내로 생성해주세요.
창의적이면서도 진실되게 작성해주세요.
간결하게 작성해주세요.
이모지를 적절하게 섞어주세요.
선택된 mbti의 성격을 고려하여 작성해주세요. 단, mbti는 편지 내용에 직접적으로 언급하지 말아주세요.
선택된 mbti가 랜덤일 경우 랜덤하게 결정하여 작성해주세요.
선택된 작성 모드에 따라 작성해주세요.
선택된 작성 모드가 랜덤일 경우 랜덤하게 결정하여 작성해주세요.
키워드가 주어질 경우 반드시 키워드 중 하나를 포함해 주세요.
문법적으로 표현이 어색하지 않게 작성해주세요.
현재는 2024년임을 고려하여 작성해주세요.

---
이름: {user_name}
나이: {user_age}
정보: {user_desc}
유형: {user_mbti}
모드: {user_mode}
키워드: {keywords}
---
    """.strip()
    return prompt

def request_chat_completion(prompt):
    response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "당신은 전문 편지 작가입니다."},
                {"role": "user", "content": prompt}
            ],
            stream=True
    )
    return response

def print_streaming_response(response):
    message = ""
    placeholder = st.empty()
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            message += delta.content
            placeholder.markdown(message + "▌")
    placeholder.markdown(message)

with st.form("form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("이름(필수)",
                             value=example["name"] if auto_complete else "",
                             placeholder=example["name"]
                             )
    with col2:
        age = st.text_input("나이(필수)",
                             value=example["age"] if auto_complete else "",
                             placeholder=example["age"]
                             )
    with col3:
        max_length = st.number_input(label="최대 단어 수",
                                     min_value=10,
                                     max_value=100,
                                     step=1,
                                     value=10)

    # with col4:
        # num = st.number_input(label="생성할 편지 수",
                                     # min_value=1,
                                     # max_value=10,
                                     # step=1,
                                     # value=5)

    desc = st.text_input(
        label="간단 정보(필수)",
        value=example["desc"] if auto_complete else "",
        placeholder=example["desc"]
    )

    option_col1, option_col2 = st.columns(2)
    with option_col1:
        default_selected_option = "ENFP"
        selected_option = st.selectbox("MBTI", ["랜덤", "ISTP", "ISTJ", "ISFP", "ISFJ", "INTP", "INTJ", "INFP", "INFJ", "ESTP", "ESTJ", "ESFP", "ESFJ", "ENTP", "ENTJ", "ENFP", "ENFJ"], index=["랜덤", "ISTP", "ISTJ", "ISFP", "ISFJ", "INTP", "INTJ", "INFP", "INFJ", "ESTP", "ESTJ", "ESFP", "ESFJ", "ENTP", "ENTJ", "ENFP", "ENFJ"].index(default_selected_option))
        # st.write("MBTI:", selected_option)

    with option_col2:
        default_selected_option2 = "반말"
        selected_option2 = st.selectbox("작성 모드", ["랜덤", "반말", "존댓말"], index=["랜덤", "반말", "존댓말"].index(default_selected_option2))
        # st.write("작성 모드:", selected_option2)

    st.text("포함할 키워드(최대 3개까지 허용)")
    col1, col2, col3 = st.columns(3)
    with col1:
        keyword_one = st.text_input(
            label="keyword_1",
            label_visibility="collapsed",
            value=example["keyword_1"][0] if auto_complete else "",
            placeholder=example["keyword_1"][0]
        )
    with col2:
        keyword_two = st.text_input(
            label="keyword_2",
            label_visibility="collapsed",
            value=example["keyword_1"][1] if auto_complete else "",
            placeholder=example["keyword_1"][1]
        )
    with col3:
        keyword_three = st.text_input(
            label="keyword_3",
            label_visibility="collapsed",
            value=example["keyword_1"][2] if auto_complete else "",
            placeholder=example["keyword_1"][2]
        )
        submit = st.form_submit_button("제출하기")

if submit:
    if not name:
        st.error("이름을 입력해주세요.")
    elif not age:
        st.error("나이를 입력해주세요")
    elif not desc:
        st.error("간단 정보를 입력해주세요.")
    else:
        keywords = [keyword_one, keyword_two, keyword_three]
        keywords = [x for x in keywords if x]
        prompt = generate_prompt(
            user_name=name,
            user_age=age,
            user_desc=desc,
            user_mbti=selected_option,
            user_mode=selected_option2,
            # num=num,
            max_length=max_length,
            keywords=keywords
        )
        response = request_chat_completion(prompt)
        print_streaming_response(response)
