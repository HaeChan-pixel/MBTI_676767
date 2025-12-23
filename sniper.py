import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="스나이퍼 저격 게임", layout="centered")

def main():
    st.title("🎯 1인칭 스나이퍼 저격 게임")
    st.markdown("""
    ### 조작 방법
    - **마우스 왼쪽 클릭**: 발사 (Shoot)
    - **마우스 오른쪽 클릭**: 줌 인/아웃 (Scope Toggle)
    - **목표**: 표적을 맞추면 100점! (표적은 2.5초 후 사라집니다)
    """)

    # 게임 로직 (HTML/JS/Canvas)
    game_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; overflow: hidden; font-family: sans-serif; cursor: crosshair; user-select: none; }
            #game-container { position: relative; width: 800px; height: 600px; background: #87CEEB; border: 5px solid #333; margin: auto; border-radius: 10px; overflow: hidden; }
            canvas { display: block; background: linear-gradient(to bottom, #87CEEB 0%, #87CEEB 60%, #228B22 60%, #228B22 100%); }
            #ui { position: absolute; top: 15px; left: 15px; color: white; text-shadow: 2px 2px 4px #000; font-size: 28px; font-weight: bold; pointer-events: none; z-index: 10; }
        </style>
    </head>
    <body oncontextmenu="return false;">
        <div id="game-container">
            <div id="ui">Score: <span id="score">0</span></div>
            <canvas id="gameCanvas" width="800" height="600"></canvas>
        </div>

        <script>
            const canvas = document.getElementById('gameCanvas');
            const ctx = canvas.getContext('2d');
            const scoreElement = document.getElementById('score');

            let score = 0;
            let isZoomed = false;
            let targets = [];
            const mouse = { x: 400, y: 300 };
            let lastTargetTime = 0;
            const TARGET_DURATION = 2500;

            // 마우스 위치 업데이트
            window.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                mouse.x = e.clientX - rect.left;
                mouse.y = e.clientY - rect.top;
            });

            // 우클릭: 줌 토글 (브라우저 메뉴 차단 포함)
            window.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                isZoomed = !isZoomed;
                return false;
            });

            // 좌클릭: 발사
            window.addEventListener('mousedown', (e) => {
                if (e.button === 0) { // Left click
                    checkHit();
                }
            });

            function createTarget() {
                const x = 100 + Math.random() * 600;
                const y = 380 + Math.random() * 50; 
                targets.push({
                    x: x,
                    y: y,
                    radius: 20,
                    createdAt: Date.now()
                });
            }

            function checkHit() {
                const now = Date.now();
                // 사격 중심점 (줌일 때는 화면 중앙 고정, 아닐 때는 마우스 위치)
                const shootX = isZoomed ? 400 : mouse.x;
                const shootY = isZoomed ? 300 : mouse.y;

                for (let i = targets.length - 1; i >= 0; i--) {
                    const t = targets[i];
                    let tx = t.x;
                    let ty = t.y;

                    if (isZoomed) {
                        // 줌 모드에서의 타겟 렌더링 위치 계산
                        tx = (t.x - mouse.x) * 2 + 400;
                        ty = (t.y - mouse.y) * 2 + 300;
                    }

                    const dist = Math.sqrt((shootX - tx)**2 + (shootY - ty)**2);
                    const hitLimit = t.radius * (isZoomed ? 2.0 : 1.0);

                    if (dist < hitLimit) {
                        targets.splice(i, 1);
                        score += 100;
                        scoreElement.innerText = score;
                        break;
                    }
                }
            }

            function drawTarget(t, zoomedMode = false) {
                let x = t.x;
                let y = t.y;
                let r = t.radius;

                if (zoomedMode) {
                    x = (t.x - mouse.x) * 2 + 400;
                    y = (t.y - mouse.y) * 2 + 300;
                    r = t.radius * 2;
                }

                // 타겟 그리기
                ctx.beginPath();
                ctx.fillStyle = "red";
                ctx.arc(x, y, r, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = "white";
                ctx.lineWidth = r/5;
                ctx.stroke();

                ctx.beginPath();
                ctx.fillStyle = "white";
                ctx.arc(x, y, r * 0.6, 0, Math.PI * 2);
                ctx.fill();

                ctx.beginPath();
                ctx.fillStyle = "red";
                ctx.arc(x, y, r * 0.2, 0, Math.PI * 2);
                ctx.fill();
            }

            function drawGun() {
                ctx.save();
                if (isZoomed) {
                    // 1. 암전 배경 (스코프 밖)
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(400, 300, 280, 0, Math.PI * 2, true);
                    ctx.rect(0, 0, 800, 600);
                    ctx.fill();

                    // 2. 조준선 (Crosshair)
                    ctx.strokeStyle = "black";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(120, 300); ctx.lineTo(680, 300);
                    ctx.moveTo(400, 20); ctx.lineTo(400, 580);
                    ctx.stroke();

                    // 3. 스코프 테두리
                    ctx.strokeStyle = "#222";
                    ctx.lineWidth = 20;
                    ctx.beginPath();
                    ctx.arc(400, 300, 280, 0, Math.PI * 2);
                    ctx.stroke();
                } else {
                    // 일반 모드 총기 (오른쪽 아래)
                    ctx.fillStyle = "#333";
                    ctx.beginPath();
                    ctx.moveTo(800, 600);
                    ctx.lineTo(500, 600);
                    ctx.lineTo(600, 400);
                    ctx.lineTo(800, 350);
                    ctx.fill();
                    
                    // 총열 위쪽 가늠쇠
                    ctx.fillStyle = "#111";
                    ctx.fillRect(590, 390, 20, 30);
                }
                ctx.restore();
            }

            function gameLoop() {
                const now = Date.now();
                
                if (now - lastTargetTime > 1500) {
                    createTarget();
                    lastTargetTime = now;
                }

                targets = targets.filter(t => now - t.createdAt < TARGET_DURATION);

                ctx.clearRect(0, 0, 800, 600);
                
                // 배경 그리기 (하늘/땅)
                ctx.fillStyle = "#87CEEB";
                ctx.fillRect(0, 0, 800, 360);
                ctx.fillStyle = "#228B22";
                ctx.fillRect(0, 360, 800, 240);

                // 타겟 그리기 (줌 상태 반영)
                targets.forEach(t => drawTarget(t, isZoomed));

                drawGun();
                requestAnimationFrame(gameLoop);
            }

            gameLoop();
        </script>
    </body>
    </html>
    """
    
    components.html(game_html, height=650)

if __name__ == "__main__":
    main()
