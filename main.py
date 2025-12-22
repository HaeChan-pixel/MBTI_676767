<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pastel MBTI Test</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Nanum Gothic', sans-serif;
            background-color: #fdfcf0;
            color: #5d4037;
        }
        .question-card {
            background-color: #ffffff;
            border-radius: 20px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            border-left: 8px solid #d1c4e9;
            transition: transform 0.2s;
        }
        .option-btn {
            transition: all 0.2s;
            border: 2px solid #fce4ec;
        }
        .option-btn:hover {
            background-color: #fce4ec;
        }
        .option-btn.selected {
            background-color: #f8bbd0;
            border-color: #f06292;
            color: #880e4f;
            font-weight: bold;
        }
        .result-card {
            background-color: #e8f5e9;
            border: 2px dashed #81c784;
            border-radius: 25px;
        }
        .btn-submit {
            background-color: #fce4ec;
            color: #880e4f;
            transition: transform 0.2s, background-color 0.2s;
        }
        .btn-submit:hover {
            background-color: #f8bbd0;
            transform: scale(1.02);
        }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-2xl mx-auto">
        <header class="text-center mb-10">
            <h1 class="text-4xl font-bold mb-2">🎨 Pastel MBTI Test</h1>
            <p class="text-gray-500">나의 성격 유형과 어울리는 감성 테마를 찾아보세요.</p>
        </header>

        <div id="quiz-container">
            <!-- Questions will be injected here -->
        </div>

        <div class="mt-10 mb-20">
            <button id="submit-btn" class="btn-submit w-full py-4 rounded-full font-bold text-lg shadow-md">
                결과 확인하기 ✨
            </button>
        </div>

        <!-- Result Modal -->
        <div id="result-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-3xl max-w-lg w-full p-8 overflow-hidden relative">
                <div class="result-card p-6 text-center">
                    <h2 id="mbti-type" class="text-3xl font-bold text-green-700 mb-2">ENTP</h2>
                    <p class="text-lg mb-4">당신의 성격 유형입니다!</p>
                    <hr class="border-green-200 mb-4">
                    <div id="theme-info">
                        <p class="font-bold text-xl mb-2">추천 이미지 테마: <span id="theme-name">키워드</span></p>
                        <p id="theme-desc" class="text-gray-600 italic">설명문구</p>
                    </div>
                </div>
                <button onclick="closeModal()" class="mt-6 w-full py-3 bg-gray-100 rounded-xl font-bold text-gray-700 hover:bg-gray-200">
                    다시 하기
                </button>
            </div>
        </div>
    </div>

    <script>
        const questions = [
            { q: "주말에 집에서 쉬는 것보다 밖에서 사람들을 만나는 것이 더 에너지가 생기나요?", type: "EI" },
            { q: "새로운 사람과 대화를 시작하는 것이 어렵지 않은가요?", type: "EI" },
            { q: "파티나 모임에서 중심에 서는 것을 즐기나요?", type: "EI" },
            { q: "미래에 대한 상상보다 현재 일어나고 있는 일에 더 집중하는 편인가요?", type: "SN" },
            { q: "어떤 일을 할 때 세부적인 지침이 있는 것을 선호하나요?", type: "SN" },
            { q: "현실적인 해결책보다는 창의적이고 비유적인 표현을 더 좋아하나요?", type: "NS" }, // N/S flipped logic for simplicity in JS loop
            { q: "논리적으로 옳고 그름을 따지는 것이 감정을 배려하는 것보다 중요한가요?", type: "TF" },
            { q: "결정을 내릴 때 객관적인 데이터가 감정적인 호소보다 더 설득력 있게 느껴지나요?", type: "TF" },
            { q: "친구의 고민을 들을 때 해결책을 제시하기보다 먼저 공감해주나요?", type: "FT" }, // F/T flipped
            { q: "여행을 갈 때 시간 단위로 꼼꼼하게 계획을 세우는 편인가요?", type: "JP" },
            { q: "마감 기한이 임박해서 일을 처리하기보다 미리 여유 있게 끝내는 것을 선호하나요?", type: "JP" },
            { q: "정해진 규칙보다는 상황에 따라 유연하게 대처하는 것이 편한가요?", type: "PJ" } // P/J flipped
        ];

        const mbtiInfo = {
            "ISTJ": { "theme": "미니멀리즘 데스크셋업", "desc": "정돈된 책상과 깔끔한 무채색 톤이 마음을 편하게 해줍니다." },
            "ISFJ": { "theme": "따뜻한 코튼과 햇살", "desc": "부드러운 침구와 오후의 햇살이 어울리는 다정한 성격입니다." },
            "INFJ": { "theme": "비 내리는 밤의 서재", "desc": "깊은 생각과 영감을 주는 차분한 서재 분위기가 어울립니다." },
            "INTJ": { "theme": "새벽녘의 도시 풍경", "desc": "체계적이고 날카로운 통찰력을 닮은 새벽의 푸른 빛이 어울립니다." },
            "ISTP": { "theme": "빈티지 작업실", "desc": "손으로 무언가를 만드는 몰입의 순간, 거친 듯 따뜻한 톤이 어울립니다." },
            "ISFP": { "theme": "수채화 같은 자연", "desc": "예술적 감수성을 자극하는 은은한 꽃들과 들판이 어울립니다." },
            "INFP": { "theme": "구름 위 보랏빛 노을", "desc": "몽환적이고 자유로운 영혼을 닮은 파스텔톤 하늘이 어울립니다." },
            "INTP": { "theme": "우주와 별이 빛나는 밤", "desc": "끝없는 호기심과 논리를 탐구하는 신비로운 우주 테마가 어울립니다." },
            "ESTP": { "theme": "활동적인 도심의 네온", "desc": "에너지 넘치고 즉흥적인 당신에게는 화려한 도심 테마가 어울립니다." },
            "ESFP": { "theme": "햇살 가득한 해변 파티", "desc": "즐거움과 사교성이 넘치는 당신에게는 밝고 경쾌한 여름 테마가 딱입니다." },
            "ENFP": { "theme": "무지개빛 페스티벌", "desc": "상상력과 열정이 가득한 당신을 닮은 다채로운 색감의 테마입니다." },
            "ENTP": { "theme": "번뜩이는 아이디어 연구소", "desc": "끊임없는 토론과 혁신을 상징하는 역동적인 분위기가 어울립니다." },
            "ESTJ": { "theme": "현대적인 오피스 빌딩", "desc": "리더십과 질서를 상징하는 수직적이고 모던한 건축물이 어울립니다." },
            "ESFJ": { "theme": "정원에서의 티파티", "desc": "사람들과 어울리며 정을 나누는 따뜻한 정원 풍경이 어울립니다." },
            "ENFJ": { "theme": "등대의 따스한 불빛", "desc": "타인을 이끄는 부드러운 카리스마를 닮은 등대 테마가 어울립니다." },
            "ENTJ": { "theme": "정상의 설산 풍경", "desc": "목표를 향해 나아가는 당신의 포부를 닮은 웅장한 설산이 어울립니다." }
        };

        const answers = Array(questions.length).fill(null);

        function renderQuestions() {
            const container = document.getElementById('quiz-container');
            container.innerHTML = questions.map((q, idx) => `
                <div class="question-card p-6 mb-6">
                    <p class="text-lg font-bold mb-4">질문 ${idx + 1}. ${q.q}</p>
                    <div class="grid grid-cols-1 md:grid-cols-5 gap-2">
                        <button onclick="selectOption(${idx}, 2)" class="option-btn p-2 rounded-lg text-sm" id="opt-${idx}-2">매우 그렇다</button>
                        <button onclick="selectOption(${idx}, 1)" class="option-btn p-2 rounded-lg text-sm" id="opt-${idx}-1">그렇다</button>
                        <button onclick="selectOption(${idx}, 0)" class="option-btn p-2 rounded-lg text-sm" id="opt-${idx}-0">보통이다</button>
                        <button onclick="selectOption(${idx}, -1)" class="option-btn p-2 rounded-lg text-sm" id="opt-${idx}--1">아니다</button>
                        <button onclick="selectOption(${idx}, -2)" class="option-btn p-2 rounded-lg text-sm" id="opt-${idx}--2">매우 아니다</button>
                    </div>
                </div>
            `).join('');
        }

        window.selectOption = function(qIdx, score) {
            answers[qIdx] = score;
            // Update UI
            for (let s of [2, 1, 0, -1, -2]) {
                document.getElementById(`opt-${qIdx}-${s}`).classList.remove('selected');
            }
            document.getElementById(`opt-${qIdx}-${score}`).classList.add('selected');
        }

        document.getElementById('submit-btn').onclick = function() {
            if (answers.includes(null)) {
                alert("모든 질문에 답해주세요!");
                return;
            }

            const scores = { E: 0, I: 0, S: 0, N: 0, T: 0, F: 0, J: 0, P: 0 };

            questions.forEach((q, idx) => {
                const score = answers[idx];
                const char1 = q.type[0];
                const char2 = q.type[1];
                if (score > 0) scores[char1] += Math.abs(score);
                else if (score < 0) scores[char2] += Math.abs(score);
            });

            let result = "";
            result += scores.E >= scores.I ? "E" : "I";
            result += scores.S >= scores.N ? "S" : "N";
            result += scores.T >= scores.F ? "T" : "F";
            result += scores.J >= scores.P ? "J" : "P";

            showResult(result);
        };

        function showResult(type) {
            document.getElementById('mbti-type').innerText = type;
            document.getElementById('theme-name').innerText = mbtiInfo[type].theme;
            document.getElementById('theme-desc').innerText = mbtiInfo[type].desc;
            document.getElementById('result-modal').classList.remove('hidden');
        }

        window.closeModal = function() {
            location.reload();
        }

        renderQuestions();
    </script>
</body>
</html>
