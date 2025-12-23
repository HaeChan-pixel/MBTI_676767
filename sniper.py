import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="스나이퍼 저격 게임", layout="centered")

def main():
    st.title("🎯 1인칭 스나이퍼 저격 게임 (AWM Edition)")
    st.markdown("""
    ### 조작 방법
    - **화면 클릭**: 게임 시작 (마우스 커서 고정)
    - **마우스 왼쪽 클릭**: 발사 (발사 후 조준 해제)
    - **마우스 오른쪽 클릭**: 줌 인/아웃
    - **ESC**: 마우스 커서 해제
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
            <div id="msg">화면을 클릭하여 조준을 시작하세요 (ESC로 해제)</div>
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
            
            // 시야 위치 (상대적 오프셋)
            const view = { x: 0, y: 0 };
            
            const TARGET_DURATION = 4000;
            const ZOOM_FACTOR = 1.3;
            const SENSITIVITY = 0.6;
            const ZOOM_SENSITIVITY = 0.2;

            canvas.addEventListener('click', () => {
                canvas.requestPointerLock();
            });

            document.addEventListener('mousemove', (e) => {
                if (document.pointerLockElement === canvas) {
                    const sens = isZoomed ? ZOOM_SENSITIVITY : SENSITIVITY;
                    // 마우스 이동만큼 시야를 반대 방향으로 밀어줌
                    view.x -= e.movementX * sens;
                    view.y -= e.movementY * sens;
                    
                    // 시야 제한
                    view.x = Math.max(-1000, Math.min(1000, view.x));
                    view.y = Math.max(-300, Math.min(300, view.y));
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
                    recoilOffset = 50; 
                    checkHit();
                    
                    if (isZoomed) {
                        setTimeout(() => { isZoomed = false; }, 80);
                    }
                }
            });

            function createTarget() {
                // 월드 좌표계 상의 타겟 위치
                const x = (Math.random() - 0.5) * 1600;
                const y = Math.random() * 100 + 50; 
                targets.push({
                    x: x,
                    y: y,
                    radius: 30,
                    createdAt: Date.now()
                });
            }

            function checkHit() {
                for (let i = targets.length - 1; i >= 0; i--) {
                    const t = targets[i];
                    // 화면 중앙 조준점과 타겟의 상대 거리 계산
                    // 타겟의 화면상 위치: t.x + view.x + centerX
                    const tx = t.x + view.x + centerX;
                    const ty = t.y + view.y + centerY;

                    const dist = Math.sqrt((centerX - tx)**2 + (centerY - ty)**2);
                    const hitLimit = t.radius; // 판정은 줌 여부와 상관없이 월드 크기 기준

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
                
                // 머리
                ctx.fillStyle = "#95a5a6";
                ctx.strokeStyle = "#2c3e50";
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.roundRect(-renderR*0.6, -renderR*1.2, renderR*1.2, renderR*0.8, 4);
                ctx.fill();
                ctx.stroke();

                // 눈
                ctx.fillStyle = "#e74c3c";
                ctx.beginPath();
                ctx.arc(-renderR*0.25, -renderR*0.9, renderR*0.15, 0, Math.PI*2);
                ctx.arc(renderR*0.25, -renderR*0.9, renderR*0.15, 0, Math.PI*2);
                ctx.fill();

                // 몸체
                ctx.fillStyle = "#7f8c8d";
                ctx.beginPath();
                ctx.roundRect(-renderR*0.9, -renderR*0.4, renderR*1.8, renderR*1.5, 4);
                ctx.fill();
                ctx.stroke();

                ctx.restore();
            }

            function drawWorld() {
                ctx.save();
                
                const currentZoom = isZoomed ? ZOOM_FACTOR : 1.0;
                
                // 배경 하늘
                ctx.fillStyle = "#2c3e50";
                ctx.fillRect(0, 0, 800, 600);

                // 지평선 및 바닥 (시야 반영)
                const horizonY = 300 + view.y;
                
                ctx.fillStyle = "#34495e";
                ctx.beginPath();
                ctx.rect(0, horizonY, 800, 600 - horizonY);
                ctx.fill();

                // 바닥 그리드 (원근감 효과)
                ctx.strokeStyle = "rgba(255,255,255,0.1)";
                ctx.lineWidth = 1;
                for(let i = -2000; i <= 2000; i += 200) {
                    ctx.beginPath();
                    ctx.moveTo(i + view.x + centerX, horizonY);
                    ctx.lineTo((i + view.x) * 2 + centerX, 600);
                    ctx.stroke();
                }

                ctx.restore();
            }

            function drawGun() {
                ctx.save();
                if (isZoomed) {
                    // 스코프 UI
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, 280, 0, Math.PI * 2, true);
                    ctx.rect(0, 0, 800, 600);
                    ctx.fill();

                    ctx.strokeStyle = "rgba(255, 0, 0, 0.5)";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(centerX - 280, centerY); ctx.lineTo(centerX + 280, centerY);
                    ctx.moveTo(centerX, centerY - 280); ctx.lineTo(centerX, centerY + 280);
                    ctx.stroke();
                } else {
                    // 1인칭 AWM 총기 모델링
                    const gx = centerX;
                    const gy = 600 - recoilOffset;

                    // 몸체 (Olive Drab)
                    ctx.fillStyle = "#4b5320";
                    ctx.beginPath();
                    ctx.moveTo(gx - 150, 600);
                    ctx.lineTo(gx - 60, 420);
                    ctx.lineTo(gx + 140, 420);
                    ctx.lineTo(gx + 250, 600);
                    ctx.fill();

                    // 스코프 본체
                    ctx.fillStyle = "#111";
                    ctx.beginPath();
                    ctx.roundRect(gx - 50, 360, 100, 70, 10);
                    ctx.fill();

                    // 렌즈
                    ctx.fillStyle = "#050505";
                    ctx.beginPath();
                    ctx.arc(gx, 395, 30, 0, Math.PI*2);
                    ctx.fill();
                    ctx.strokeStyle = "#333";
                    ctx.lineWidth = 4;
                    ctx.stroke();

                    // 총열 상단 (스코프 앞쪽)
                    ctx.fillStyle = "#2c3111";
                    ctx.beginPath();
                    ctx.moveTo(gx - 30, 360);
                    ctx.lineTo(gx - 10, 320);
                    ctx.lineTo(gx + 10, 320);
                    ctx.lineTo(gx + 30, 360);
                    ctx.fill();
                }
                ctx.restore();
                
                if (recoilOffset > 0) recoilOffset *= 0.8;
            }

            function drawMuzzleFlash() {
                if (flashOpacity <= 0) return;
                ctx.save();
                const fy = isZoomed ? centerY : 350 - recoilOffset;
                const grad = ctx.createRadialGradient(centerX, fy, 0, centerX, fy, isZoomed ? 100 : 150);
                grad.addColorStop(0, `rgba(255, 200, 50, ${flashOpacity})`);
                grad.addColorStop(1, "rgba(255, 100, 0, 0)");
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(centerX, fy, isZoomed ? 100 : 150, 0, Math.PI*2);
                ctx.fill();
                ctx.restore();
                flashOpacity -= 0.15;
            }

            function gameLoop() {
                const now = Date.now();
                if (now - lastTargetTime > 1200) {
                    createTarget();
                    lastTargetTime = now;
                }
                targets = targets.filter(t => now - t.createdAt < TARGET_DURATION);

                ctx.clearRect(0, 0, 800, 600);
                
                drawWorld();

                // 타겟 렌더링
                targets.forEach(t => {
                    const tx = t.x + view.x + centerX;
                    const ty = t.y + view.y + centerY;
                    drawRobot(tx, ty, t.radius, isZoomed);
                });
                
                drawMuzzleFlash();
                drawGun();
                
                // 지향 사격 조준점
                if (!isZoomed && document.pointerLockElement === canvas) {
                    ctx.fillStyle = "rgba(0, 255, 204, 0.7)";
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
