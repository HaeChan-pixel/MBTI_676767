import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Pastel MBTI Test",
    page_icon="🎨",
    layout="centered"
)

# Custom CSS for the Pastel Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Nanum Gothic', sans-serif;
        background-color: #fdfcf0;
        color: #5d4037;
    }
    
    .stMarkdown h1 {
        text-align: center;
        font-weight: 800;
        color: #5d4037;
        margin-bottom: 0.5rem;
    }

    .question-box {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 2rem;
        border-radius: 20px;
        border-left: 8px solid #d1c4e9;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* Streamlit widget styling override */
    .stSlider [data-baseweb="slider"] {
        padding-top: 1rem;
    }

    .result-container {
        background-color: white;
        padding: 2.5rem;
        border-radius: 30px;
        text-align: center;
        border: 2px dashed #81c784;
        margin-top: 2rem;
        animation: fadeIn 0.8s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

# MBTI Questions Data
questions = [
    {"q": "새로운 환경에서 처음 본 사람에게 먼저 말을 거는 편인가요?", "type": "EI"},
    {"q": "여러 명과 함께 있는 모임보다 혼자만의 시간을 가질 때 충전되나요?", "type": "IE"},
    {"q": "주목받는 자리에서 즐거움을 느끼는 편인가요?", "type": "EI"},
    {"q": "미래에 대한 상상보다 현재 일어나고 있는 일에 더 집중하는 편인가요?", "type": "SN"},
    {"q": "상상력이 풍부하다는 말을 자주 듣는 편인가요?", "type": "NS"},
    {"q": "현실적이고 실용적인 조언을 해주는 것이 더 가치 있다고 생각하나요?", "type": "SN"},
    {"q": "결정을 내릴 때 논리적인 인과관계보다 사람의 마음과 조화를 먼저 고려하나요?", "type": "FT"},
    {"q": "누군가 고민을 말하면 해결책보다는 공감을 먼저 해주고 싶나요?", "type": "FT"},
    {"q": "객관적인 비판이 감정적인 배려보다 더 필요하다고 생각하나요?", "type": "TF"},
    {"q": "미리 계획을 세우기보다 그때그때 상황에 맞춰 행동하는 것을 선호하나요?", "type": "PJ"},
    {"q": "방 정리가 잘 되어 있지 않아도 생활하는 데 큰 불편함이 없나요?", "type": "PJ"},
    {"q": "약속 시간이나 마감 기한을 엄격하게 지키려고 노력하나요?", "type": "JP"}
]

# MBTI Theme Data
mbti_themes = {
    "ISTJ": {"theme": "미니멀 클래식", "desc": "정돈된 책상과 무채색 톤이 주는 안정감.", "color": "#CFD8DC"},
    "ISFJ": {"theme": "포근한 코튼", "desc": "오후의 햇살이 스미는 부드러운 침구와 꽃향기.", "color": "#F8BBD0"},
    "INFJ": {"theme": "새벽의 사유", "desc": "깊은 밤, 비 내리는 소리와 따뜻한 차 한 잔.", "color": "#D1C4E9"},
    "INTJ": {"theme": "모던 아키텍처", "desc": "체계적이고 날카로운 통찰력을 닮은 직선의 미학.", "color": "#B0BEC5"},
    "ISTP": {"theme": "로그 캐빈", "desc": "나무 냄새와 직접 만든 도구들이 가득한 작업실.", "color": "#D7CCC8"},
    "ISFP": {"theme": "수채화 정원", "desc": "은은한 색채의 꽃들과 바람에 흔들리는 풀잎.", "color": "#DCEDC8"},
    "INFP": {"theme": "보랏빛 꿈", "desc": "몽환적이고 자유로운 영혼을 닮은 파스텔 노을.", "color": "#E1BEE7"},
    "INTP": {"theme": "코스믹 더스트", "desc": "끝없는 호기심을 자극하는 밤하늘의 성운.", "color": "#C5CAE9"},
    "ESTP": {"theme": "네온 시티", "desc": "에너지가 넘치는 도심의 밤과 화려한 조명.", "color": "#FFCCBC"},
    "ESFP": {"theme": "트로피컬 펀치", "desc": "경쾌한 음악과 즐거운 웃음이 가득한 여름 해변.", "color": "#FFF9C4"},
    "ENFP": {"theme": "페스티벌 레인보우", "desc": "어디로 튈지 모르는 다채롭고 밝은 색감.", "color": "#FFECB3"},
    "ENTP": {"theme": "혁신적 스튜디오", "desc": "창의적인 아이디어가 번뜩이는 역동적인 공간.", "color": "#B2EBF2"},
    "ESTJ": {"theme": "메트로폴리스", "desc": "질서와 효율이 돋보이는 수직적인 빌딩 숲.", "color": "#BBDEFB"},
    "ESFJ": {"theme": "애프터눈 티", "desc": "사람들과 온기를 나누는 평화로운 가든 파티.", "color": "#F0F4C3"},
    "ENFJ": {"theme": "골든 아워", "desc": "세상을 따뜻하게 비추는 일몰 직전의 금빛 조명.", "color": "#FFE0B2"},
    "ENTJ": {"theme": "피크 마운틴", "desc": "목표를 향해 나아가는 웅장하고 높은 설산.", "color": "#E0E0E0"}
}

def main():
    st.title("🎨 Pastel MBTI Test")
    st.markdown("<p style='text-align: center; color: #888;'>나의 성격과 가장 어울리는 감성 테마를 찾아보세요</p>", unsafe_allow_html=True)
    st.divider()

    # Create form for the quiz
    with st.form("mbti_form"):
        user_answers = []
        
        for i, item in enumerate(questions):
            st.markdown(f"<div class='question-box'><b>Q{i+1}.</b> {item['q']}</div>", unsafe_allow_html=True)
            
            # Slider for scale: -2 (Very No) to 2 (Very Yes)
            answer = st.select_slider(
                f"Question {i+1} slider",
                options=[-2, -1, 0, 1, 2],
                value=0,
                format_func=lambda x: {2: "매우 그렇다", 1: "그렇다", 0: "보통이다", -1: "아니다", -2: "매우 아니다"}[x],
                label_visibility="collapsed",
                key=f"q_{i}"
            )
            user_answers.append(answer)
            st.write("") # Spacing

        submitted = st.form_submit_button("나의 테마 확인하기 ✨")

        if submitted:
            # Score Calculation
            scores = { 'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0 }
            
            for i, val in enumerate(user_answers):
                char1 = questions[i]['type'][0]
                char2 = questions[i]['type'][1]
                
                if val > 0:
                    scores[char1] += abs(val)
                elif val < 0:
                    scores[char2] += abs(val)
                else:
                    scores[char1] += 0.5
                    scores[char2] += 0.5
            
            # Determine Result
            mbti_result = (
                ('E' if scores['E'] >= scores['I'] else 'I') +
                ('S' if scores['S'] >= scores['N'] else 'N') +
                ('T' if scores['T'] >= scores['F'] else 'F') +
                ('J' if scores['J'] >= scores['P'] else 'P')
            )
            
            # Show Results
            st.balloons()
            # Fixed NameError by using mbti_themes instead of mbtiThemes
            info = mbti_themes[mbti_result]
            
            st.markdown(f"""
                <div class="result-container" style="border-color: {info['color']};">
                    <p style="color: #999; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8rem;">Your Type is</p>
                    <h2 style="color: {info['color'] if info['color'] != '#E0E0E0' else '#444'}; font-size: 4rem; margin: 0;">{mbti_result}</h2>
                    <div style="background-color: {info['color']}44; padding: 20px; border-radius: 20px; margin-top: 20px;">
                        <p style="font-size: 0.7rem; color: #777; margin: 0;">Recommended Mood</p>
                        <h3 style="margin: 5px 0; font-size: 1.8rem;">{info['theme']}</h3>
                        <p style="color: #666; font-size: 0.9rem;">{info['desc']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.success(f"테스트 완료! 당신의 유형은 {mbti_result}입니다.")

if __name__ == "__main__":
    main()
