import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="스나이퍼 저격 게임", layout="centered")

def main():
    st.title("🎯 택티컬 실내 사격장 슈팅")
    st.markdown("""
    ### 조작 방법
    - **마우스 이동**: 조준선과 총기가 커서를 따라 움직입니다. (초정밀 감도 적용)
    - **마우스 왼쪽 클릭**: 발사 (총구 화염 이펙트)
    - **마우스 오른쪽 클릭**: 정밀 조준 (줌)
    - **전체화면**: 게임 화면 우측 상단의 'FULLSCREEN' 버튼을 클릭하세요.
    """)

    # 게임 로직 (HTML/JS/Canvas)
    game_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; overflow: hidden; font-family: sans-serif; cursor: none; user-select: none; background-color: #000; }
            #game-container { 
                position: relative; 
                width: 800px; 
                height: 600px; 
                background: #000; 
                border: 4px solid #333; 
                margin: auto; 
                border-radius: 8px; 
                overflow: hidden; 
                display: flex;
                flex-direction: column;
            }
            #game-container:fullscreen {
                width: 100vw;
                height: 100vh;
                border: none;
                border-radius: 0;
            }
            canvas { display: block; width: 100%; height: 100%; }
            #ui { 
                position: absolute; 
                top: 20px; 
                left: 20px; 
                color: #00f2ff; 
                text-shadow: 0 0 15px rgba(0, 242, 255, 0.7); 
                font-size: 32px; 
                font-weight: 900; 
                pointer-events: none; 
                z-index: 10; 
                font-family: 'Courier New', Courier, monospace; 
                letter-spacing: 2px;
            }
            #fullscreen-btn {
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(0, 242, 255, 0.1);
                border: 1px solid rgba(0, 242, 255, 0.5);
                color: #00f2ff;
                padding: 6px 12px;
                font-size: 11px;
                cursor: pointer;
                z-index: 20;
                border-radius: 4px;
                font-family: 'monospace';
                text-transform: uppercase;
                transition: all 0.2s;
            }
            #fullscreen-btn:hover {
                background: rgba(0, 242, 255, 0.3);
                border-color: #00f2ff;
            }
        </style>
    </head>
    <body oncontextmenu="return false;">
        <div id="game-container">
            <div id="ui">SCORE: <span id="score">0000</span></div>
            <button id="fullscreen-btn">Fullscreen</button>
            <canvas id="gameCanvas" width="800" height="600"></canvas>
        </div>

        <script>
            const container = document.getElementById('game-container');
            const canvas = document.getElementById('gameCanvas');
            const ctx = canvas.getContext('2d');
            const scoreElement = document.getElementById('score');
            const fsBtn = document.getElementById('fullscreen-btn');

            let score = 0;
            let isZoomed = false;
            let targets = [];
            let flashOpacity = 0; 
            let recoilOffset = 0; 
            
            // 마우스 현재 위치
            let mouseX = 400;
            let mouseY = 300;
            // 부드러운 움직임을 위한 보간용 위치
            let lerpX = 400;
            let lerpY = 300;
            
            // 감도 보정 계수 (낮을수록 부드럽고 묵직함)
            const SENSITIVITY_LERP = 0.15; 
            const TARGET_DURATION = 4000;

            // 전체화면 기능
            fsBtn.addEventListener('click', () => {
                if (!document.fullscreenElement) {
                    container.requestFullscreen().catch(err => {
                        console.log(`Error: ${err.message}`);
                    });
                } else {
                    document.exitFullscreen();
                }
            });

            canvas.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                
                mouseX = (e.clientX - rect.left) * scaleX;
                mouseY = (e.clientY - rect.top) * scaleY;
            });

            canvas.addEventListener('mousedown', (e) => {
                if (e.button === 0) fire();
                if (e.button === 2) isZoomed = !isZoomed;
            });

            function fire() {
                flashOpacity = 1.0; 
                recoilOffset = 55; 
                checkHit();
            }

            function createTarget() {
                const x = Math.random() * 600 + 100;
                const y = Math.random() * 200 + 100; 
                targets.push({
                    x: x,
                    y: y,
                    radius: 35,
                    createdAt: Date.now()
                });
            }

            function checkHit() {
                for (let i = targets.length - 1; i >= 0; i--) {
                    const t = targets[i];
                    const dist = Math.sqrt((mouseX - t.x)**2 + (mouseY - t.y)**2);
                    if (dist < t.radius) {
                        targets.splice(i, 1);
                        score += 100;
                        scoreElement.innerText = score.toString().padStart(4, '0');
                        break;
                    }
                }
            }

            function drawTargetBoard(x, y, r) {
                ctx.save();
                ctx.translate(x, y);
                
                // 타겟 본체
                ctx.fillStyle = "#e0e0e0";
                ctx.beginPath();
                ctx.moveTo(-r*0.5, r);
                ctx.lineTo(-r*0.7, -r*0.5);
                ctx.quadraticCurveTo(0, -r*1.5, r*0.7, -r*0.5);
                ctx.lineTo(r*0.5, r);
                ctx.fill();
                
                // 타겟 내부 선
                ctx.strokeStyle = "#bbb";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.arc(0, -r*0.3, r*0.4, 0, Math.PI*2);
                ctx.stroke();
                
                ctx.restore();
            }

            function drawRangeBackground() {
                // 바닥 (콘크리트)
                ctx.fillStyle = "#1a1a1a";
                ctx.fillRect(0, 350, 800, 250);
                // 천장
                ctx.fillStyle = "#252525";
                ctx.fillRect(0, 0, 800, 150);
                // 정면 벽
                ctx.fillStyle = "#2c2c2c";
                ctx.fillRect(0, 150, 800, 200);

                // 네온 효과 장식
                ctx.strokeStyle = "#00f2ff";
                ctx.lineWidth = 3;
                ctx.shadowBlur = 15;
                ctx.shadowColor = "#00f2ff";
                
                // 좌측 라인
                ctx.beginPath();
                ctx.moveTo(0, 350); ctx.lineTo(180, 350); ctx.lineTo(180, 150);
                ctx.stroke();
                
                // 우측 라인
                ctx.beginPath();
                ctx.moveTo(800, 350); ctx.lineTo(620, 350); ctx.lineTo(620, 150);
                ctx.stroke();
                
                ctx.shadowBlur = 0;
            }

            function drawHandsAndGun() {
                // 마우스 위치로 서서히 이동 (감도 완화)
                lerpX += (mouseX - lerpX) * SENSITIVITY_LERP;
                lerpY += (mouseY - lerpY) * SENSITIVITY_LERP;

                ctx.save();
                
                const dx = lerpX - 400;
                const dy = lerpY - 600;
                const angle = Math.atan2(dy, dx) + Math.PI / 2;

                // 총기 위치 (마우스 방향으로 살짝 이동)
                const gx = 400 + (dx * 0.05); 
                const gy = 600 - recoilOffset + (dy * 0.03);

                ctx.translate(gx, gy);
                ctx.rotate(angle * 0.4); 

                if(isZoomed) ctx.globalAlpha = 0.2;

                // 소매 (전술복)
                ctx.fillStyle = "#050505";
                ctx.fillRect(-140, 0, 70, 250);
                ctx.fillRect(70, 0, 70, 250);

                // 손 (파지법)
                ctx.fillStyle = "#c69c6d";
                ctx.beginPath();
                ctx.ellipse(-35, -15, 35, 65, -0.2, 0, Math.PI*2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(35, -15, 35, 65, 0.2, 0, Math.PI*2);
                ctx.fill();

                // 권총 몸체
                ctx.fillStyle = "#151515";
                ctx.fillRect(-28, -135, 56, 115);
                ctx.fillStyle = "#000";
                ctx.fillRect(-31, -140, 62, 35); // 슬라이드 상단
                
                // 가늠쇠 포인트
                ctx.fillStyle = "#fff";
                ctx.fillRect(-2, -145, 4, 6);

                ctx.restore();
                
                // 조준선 (마우스 실제 위치)
                ctx.save();
                ctx.translate(mouseX, mouseY);
                if(isZoomed) ctx.scale(1.4, 1.4);

                ctx.strokeStyle = "#00f2ff";
                ctx.lineWidth = 3;
                ctx.shadowBlur = 10;
                ctx.shadowColor = "#00f2ff";
                
                // 원형 조준망
                ctx.beginPath();
                ctx.arc(0, 0, 38, 0, Math.PI*2);
                ctx.stroke();
                
                // 십자선
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(-45, 0); ctx.lineTo(-8, 0);
                ctx.moveTo(45, 0); ctx.lineTo(8, 0);
                ctx.moveTo(0, -45); ctx.lineTo(0, -8);
                ctx.moveTo(0, 45); ctx.lineTo(0, 8);
                ctx.stroke();

                // 중앙 도트
                ctx.fillStyle = "red";
                ctx.shadowBlur = 5;
                ctx.shadowColor = "red";
                ctx.beginPath();
                ctx.arc(0, 0, 2.5, 0, Math.PI*2);
                ctx.fill();
                
                ctx.restore();

                if (recoilOffset > 0) recoilOffset *= 0.82;
            }

            function drawMuzzleFlash() {
                if (flashOpacity <= 0) return;
                ctx.save();
                
                // 현재 총구의 가변 위치 계산
                const dx = lerpX - 400;
                const dy = lerpY - 600;
                const fx = 400 + (dx * 0.2);
                const fy = 600 + (dy * 0.4) - recoilOffset;

                const grad = ctx.createRadialGradient(fx, fy, 0, fx, fy, 130);
                grad.addColorStop(0, `rgba(255, 255, 220, ${flashOpacity})`);
                grad.addColorStop(0.3, `rgba(255, 180, 50, ${flashOpacity * 0.7})`);
                grad.addColorStop(1, "rgba(255, 100, 0, 0)");
                
                ctx.fillStyle = grad;
                ctx.globalCompositeOperation = "lighter";
                ctx.beginPath();
                ctx.arc(fx, fy, 130, 0, Math.PI*2);
                ctx.fill();
                
                ctx.restore();
                flashOpacity -= 0.12;
            }

            function gameLoop() {
                const now = Date.now();
                if (now - lastTargetTime > 1400) {
                    createTarget();
                    lastTargetTime = now;
                }
                targets = targets.filter(t => now - t.createdAt < TARGET_DURATION);

                ctx.clearRect(0, 0, 800, 600);
                drawRangeBackground();

                targets.forEach(t => {
                    drawTargetBoard(t.x, t.y, t.radius);
                });
                
                drawMuzzleFlash();
                drawHandsAndGun();

                requestAnimationFrame(gameLoop);
            }

            let lastTargetTime = 0;
            gameLoop();
        </script>
    </body>
    </html>
    """
    
    components.html(game_html, height=650)

if __name__ == "__main__":
    main()
