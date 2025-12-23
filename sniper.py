import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="스나이퍼 저격 게임", layout="centered")

def main():
    st.title("🎯 1인칭 핸드건 슈팅 게임")
    st.markdown("""
    ### 조작 방법
    - **화면 클릭**: 조준 시작 (마우스 커서 고정)
    - **마우스 이동**: 시야 조절
    - **마우스 왼쪽 클릭**: 발사
    - **마우스 오른쪽 클릭**: 정밀 조준 (줌)
    - **ESC**: 마우스 해제
    """)

    # 게임 로직 (HTML/JS/Canvas)
    game_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; overflow: hidden; font-family: sans-serif; cursor: none; user-select: none; background-color: #000; }
            #game-container { position: relative; width: 800px; height: 600px; background: #1a1a1a; border: 5px solid #333; margin: auto; border-radius: 10px; overflow: hidden; }
            canvas { display: block; background: #2c3e50; }
            #ui { position: absolute; top: 15px; left: 15px; color: #00ffcc; text-shadow: 2px 2px 4px #000; font-size: 28px; font-weight: bold; pointer-events: none; z-index: 10; font-family: 'Courier New', Courier, monospace; }
            #msg { position: absolute; bottom: 10px; width: 100%; text-align: center; color: white; font-size: 14px; pointer-events: none; z-index: 5; }
        </style>
    </head>
    <body oncontextmenu="return false;">
        <div id="game-container">
            <div id="ui">SCORE: <span id="score">0</span></div>
            <div id="msg">화면을 클릭하여 시작하세요</div>
            <canvas id="gameCanvas" width="800" height="600"></canvas>
        </div>

        <script>
            const canvas = document.getElementById('gameCanvas');
            const ctx = canvas.getContext('2d');
            const scoreElement = document.getElementById('score');

            let score = 0;
            let isZoomed = false;
            let targets = [];
            let flashOpacity = 0; 
            let recoilOffset = 0; 
            
            const centerX = 400;
            const centerY = 300;
            
            // 시야 위치
            const view = { x: 0, y: 0 };
            
            const TARGET_DURATION = 4000;
            const ZOOM_FACTOR = 1.5;
            const SENSITIVITY = 0.8;
            const ZOOM_SENSITIVITY = 0.3;

            canvas.addEventListener('click', () => {
                canvas.requestPointerLock();
            });

            document.addEventListener('mousemove', (e) => {
                if (document.pointerLockElement === canvas) {
                    const sens = isZoomed ? ZOOM_SENSITIVITY : SENSITIVITY;
                    // 마우스 이동만큼 시야 좌표 업데이트
                    view.x -= e.movementX * sens;
                    view.y -= e.movementY * sens;
                    
                    // 시야 제한 (무한대로 돌아가지 않도록)
                    view.x = Math.max(-1200, Math.min(1200, view.x));
                    view.y = Math.max(-400, Math.min(400, view.y));
                }
            });

            window.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                if (document.pointerLockElement === canvas) {
                    isZoomed = !isZoomed;
                }
                return false;
            });

            window.addEventListener('mousedown', (e) => {
                if (document.pointerLockElement === canvas && e.button === 0) { 
                    flashOpacity = 1.0; 
                    recoilOffset = 40; 
                    checkHit();
                }
            });

            function createTarget() {
                const x = (Math.random() - 0.5) * 2000;
                const y = Math.random() * 200 - 100; 
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
                    // 화면 중앙 조준점과 타겟의 현재 화면상 위치 비교
                    const tx = t.x + view.x + centerX;
                    const ty = t.y + view.y + centerY;

                    // 판정 시 줌 상태에 따른 좌표 보정
                    let finalTx = tx;
                    let finalTy = ty;
                    if (isZoomed) {
                        finalTx = (tx - centerX) * ZOOM_FACTOR + centerX;
                        finalTy = (ty - centerY) * ZOOM_FACTOR + centerY;
                    }

                    const dist = Math.sqrt((centerX - finalTx)**2 + (centerY - finalTy)**2);
                    const hitLimit = t.radius * (isZoomed ? ZOOM_FACTOR : 1.0);

                    if (dist < hitLimit) {
                        targets.splice(i, 1);
                        score += 100;
                        scoreElement.innerText = score;
                        break;
                    }
                }
            }

            function drawRobot(x, y, r, zoomed) {
                ctx.save();
                let renderX = x;
                let renderY = y;
                let renderR = r;

                if (zoomed) {
                    renderX = (x - centerX) * ZOOM_FACTOR + centerX;
                    renderY = (y - centerY) * ZOOM_FACTOR + centerY;
                    renderR = r * ZOOM_FACTOR;
                }

                ctx.translate(renderX, renderY);
                // 단순 로봇 렌더링
                ctx.fillStyle = "#bdc3c7";
                ctx.fillRect(-renderR, -renderR, renderR*2, renderR*2);
                ctx.fillStyle = "#e74c3c";
                ctx.beginPath();
                ctx.arc(0, -renderR*0.5, renderR*0.3, 0, Math.PI*2);
                ctx.fill();
                ctx.restore();
            }

            function drawWorld() {
                ctx.save();
                // 하늘
                ctx.fillStyle = "#2c3e50";
                ctx.fillRect(0, 0, 800, 600);

                // 바닥 (시야 반영)
                const horizonY = 300 + view.y;
                ctx.fillStyle = "#7f8c8d";
                ctx.fillRect(0, horizonY, 800, 600 - horizonY);

                // 바닥 격자
                ctx.strokeStyle = "rgba(255,255,255,0.1)";
                for(let i = -2000; i <= 2000; i += 200) {
                    ctx.beginPath();
                    ctx.moveTo(i + view.x + centerX, horizonY);
                    ctx.lineTo((i + view.x) * 3 + centerX, 600);
                    ctx.stroke();
                }
                ctx.restore();
            }

            function drawHandsAndGun() {
                ctx.save();
                const bounce = Math.sin(Date.now() / 200) * 2; // 숨쉬는 효과
                const gx = centerX;
                const gy = 600 - recoilOffset + bounce;

                if (isZoomed) {
                    // 정밀 조준 UI
                    ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
                    ctx.fillRect(0, 0, 800, 600);
                    ctx.strokeStyle = "#00ffcc";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(centerX - 40, centerY); ctx.lineTo(centerX + 40, centerY);
                    ctx.moveTo(centerX, centerY - 40); ctx.lineTo(centerX, centerY + 40);
                    ctx.stroke();
                }

                // 사람 손 (피부색)
                ctx.fillStyle = "#ffdbac";
                
                // 오른손
                ctx.beginPath();
                ctx.ellipse(gx + 60, gy - 20, 40, 80, Math.PI / 10, 0, Math.PI * 2);
                ctx.fill();
                
                // 왼손 (권총을 아래에서 받쳐 잡는 모습)
                ctx.beginPath();
                ctx.ellipse(gx - 40, gy + 10, 45, 70, -Math.PI / 6, 0, Math.PI * 2);
                ctx.fill();

                // 권총 (글록 스타일)
                ctx.fillStyle = "#2c3e50";
                // 슬라이드
                ctx.fillRect(gx - 30, gy - 130, 60, 120);
                // 가늠쇠
                ctx.fillStyle = "#000";
                ctx.fillRect(gx - 5, gy - 140, 10, 10);
                
                // 소매 (옷)
                ctx.fillStyle = "#34495e";
                ctx.fillRect(gx + 40, gy + 30, 100, 150);
                ctx.fillRect(gx - 140, gy + 30, 100, 150);

                ctx.restore();
                
                if (recoilOffset > 0) recoilOffset *= 0.8;
            }

            function drawMuzzleFlash() {
                if (flashOpacity <= 0) return;
                ctx.save();
                const fy = centerY + (isZoomed ? 0 : 150) - recoilOffset;
                const grad = ctx.createRadialGradient(centerX, fy, 0, centerX, fy, 100);
                grad.addColorStop(0, `rgba(255, 255, 200, ${flashOpacity})`);
                grad.addColorStop(1, "rgba(255, 150, 0, 0)");
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(centerX, fy, 100, 0, Math.PI*2);
                ctx.fill();
                ctx.restore();
                flashOpacity -= 0.2;
            }

            function gameLoop() {
                const now = Date.now();
                if (now - lastTargetTime > 1500) {
                    createTarget();
                    lastTargetTime = now;
                }
                targets = targets.filter(t => now - t.createdAt < TARGET_DURATION);

                ctx.clearRect(0, 0, 800, 600);
                drawWorld();

                targets.forEach(t => {
                    const tx = t.x + view.x + centerX;
                    const ty = t.y + view.y + centerY;
                    drawRobot(tx, ty, t.radius, isZoomed);
                });
                
                drawMuzzleFlash();
                drawHandsAndGun();
                
                // 조준점 (지향사격)
                if (!isZoomed && document.pointerLockElement === canvas) {
                    ctx.fillStyle = "rgba(0, 255, 204, 0.6)";
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, 4, 0, Math.PI * 2);
                    ctx.fill();
                }

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
