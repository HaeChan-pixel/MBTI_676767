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
            #game-container { position: relative; width: 800px; height: 600px; background: #2c3e50; border: 5px solid #1a1a1a; margin: auto; border-radius: 10px; overflow: hidden; }
            canvas { display: block; }
            #ui { position: absolute; top: 15px; left: 15px; color: #00ffcc; text-shadow: 2px 2px 4px #000; font-size: 28px; font-weight: bold; pointer-events: none; z-index: 10; font-family: 'Courier New', Courier, monospace; }
            #msg { position: absolute; bottom: 10px; width: 100%; text-align: center; color: white; font-size: 14px; pointer-events: none; }
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
            
            // 화면 중앙 고정 좌표
            const centerX = 400;
            const centerY = 300;
            
            // 시야(카메라) 위치 - 마우스 이동에 따라 변함
            const view = { x: 0, y: 0 };
            
            const TARGET_DURATION = 3000;
            const ZOOM_FACTOR = 1.25;
            const SENSITIVITY = 0.5;
            const ZOOM_SENSITIVITY = 0.2;

            // 포인터 락 설정 (커서 고정)
            canvas.addEventListener('click', () => {
                canvas.requestPointerLock();
            });

            document.addEventListener('mousemove', (e) => {
                if (document.pointerLockElement === canvas) {
                    const sens = isZoomed ? ZOOM_SENSITIVITY : SENSITIVITY;
                    view.x -= e.movementX * sens;
                    view.y -= e.movementY * sens;
                    
                    // 시야 제한 (너무 멀리 돌아가지 않도록)
                    if (view.x > 800) view.x = 800;
                    if (view.x < -800) view.x = -800;
                    if (view.y > 400) view.y = 400;
                    if (view.y < -400) view.y = -400;
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
                    recoilOffset = 40; // 반동 적용
                    checkHit();
                    
                    if (isZoomed) {
                        setTimeout(() => { isZoomed = false; }, 100);
                    }
                }
            });

            function createTarget() {
                const x = Math.random() * 1400 - 700;
                const y = Math.random() * 200 + 50; 
                targets.push({
                    x: x,
                    y: y,
                    radius: 25,
                    createdAt: Date.now()
                });
            }

            function checkHit() {
                for (let i = targets.length - 1; i >= 0; i--) {
                    const t = targets[i];
                    let tx = t.x + view.x + centerX;
                    let ty = t.y + view.y + centerY;

                    if (isZoomed) {
                        tx = (tx - centerX) * ZOOM_FACTOR + centerX;
                        ty = (ty - centerY) * ZOOM_FACTOR + centerY;
                    }

                    const dist = Math.sqrt((centerX - tx)**2 + (centerY - ty)**2);
                    const hitLimit = t.radius * (isZoomed ? ZOOM_FACTOR : 1.0);

                    if (dist < hitLimit) {
                        targets.splice(i, 1);
                        score += 100;
                        scoreElement.innerText = score;
                        break;
                    }
                }
            }

            function drawDetailedRobot(x, y, r) {
                ctx.save();
                ctx.translate(x, y);
                
                // 몸체
                ctx.fillStyle = "#576574";
                ctx.strokeStyle = "#222f3e";
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.roundRect(-r * 0.8, -r * 0.2, r * 1.6, r * 1.2, 4);
                ctx.fill();
                ctx.stroke();

                // 머리
                ctx.fillStyle = "#8395a7";
                ctx.beginPath();
                ctx.roundRect(-r * 0.6, -r * 1.2, r * 1.2, r * 0.9, 5);
                ctx.fill();
                ctx.stroke();

                // 눈
                ctx.fillStyle = "#ff9f43";
                ctx.shadowBlur = 8;
                ctx.shadowColor = "#ff9f43";
                ctx.beginPath();
                ctx.arc(-r * 0.25, -r * 0.8, r * 0.12, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(r * 0.25, -r * 0.8, r * 0.12, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }

            function drawBackground() {
                ctx.save();
                ctx.translate(view.x, view.y);

                // 배경 하늘
                ctx.fillStyle = "#1e272e";
                ctx.fillRect(-2000, -1000, 4000, 1300);
                
                // 정면 벽
                ctx.fillStyle = "#2f3640";
                ctx.fillRect(-2000, 0, 4000, 300);
                
                // 그리드 패턴
                ctx.strokeStyle = "#3d444d";
                ctx.lineWidth = 2;
                for(let i=-2000; i<2000; i+=200) {
                    ctx.strokeRect(i, 0, 200, 300);
                }

                // 바닥
                ctx.fillStyle = "#353b48";
                ctx.fillRect(-2000, 300, 4000, 2000);
                
                // 바닥 안전선
                ctx.fillStyle = "#e1b12c";
                ctx.fillRect(-2000, 300, 4000, 10);

                ctx.restore();
            }

            function drawMuzzleFlash() {
                if (flashOpacity <= 0) return;
                ctx.save();
                const fx = centerX;
                const fy = centerY + (isZoomed ? 0 : 80) - recoilOffset;
                const grad = ctx.createRadialGradient(fx, fy, 0, fx, fy, isZoomed ? 80 : 120);
                grad.addColorStop(0, `rgba(255, 255, 180, ${flashOpacity})`);
                grad.addColorStop(0.4, `rgba(255, 150, 0, ${flashOpacity * 0.7})`);
                grad.addColorStop(1, `rgba(255, 50, 0, 0)`);
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(fx, fy, isZoomed ? 80 : 120, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
                flashOpacity -= 0.1; 
            }

            function drawGun() {
                ctx.save();
                if (isZoomed) {
                    // 스코프 모드
                    ctx.fillStyle = "rgba(0, 0, 0, 0.98)";
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, 280, 0, Math.PI * 2, true);
                    ctx.rect(0, 0, 800, 600);
                    ctx.fill();

                    // 조준선
                    ctx.strokeStyle = "#00ffcc";
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(centerX - 280, centerY); ctx.lineTo(centerX + 280, centerY);
                    ctx.moveTo(centerX, centerY - 280); ctx.lineTo(centerX, centerY + 280);
                    ctx.stroke();

                    // 중앙 점
                    ctx.fillStyle = "red";
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, 2, 0, Math.PI * 2);
                    ctx.fill();
                } else {
                    // 1인칭 AWM 렌더링
                    const gx = centerX;
                    const gy = 600 - recoilOffset;

                    ctx.shadowBlur = 20;
                    ctx.shadowColor = "black";
                    
                    // 총 몸체
                    ctx.fillStyle = "#3d441a"; 
                    ctx.beginPath();
                    ctx.moveTo(gx - 120, 600);
                    ctx.lineTo(gx - 50, 450);
                    ctx.lineTo(gx + 130, 450);
                    ctx.lineTo(gx + 220, 600);
                    ctx.fill();

                    // 총열 상단
                    ctx.fillStyle = "#2c3111";
                    ctx.beginPath();
                    ctx.moveTo(gx - 40, 450);
                    ctx.lineTo(gx - 15, 380);
                    ctx.lineTo(gx + 15, 380);
                    ctx.lineTo(gx + 40, 450);
                    ctx.fill();

                    // 스코프 뭉치
                    ctx.fillStyle = "#111";
                    ctx.beginPath();
                    ctx.roundRect(gx - 45, 385, 90, 65, 10);
                    ctx.fill();
                    
                    // 스코프 렌즈
                    ctx.fillStyle = "#0a0a0a";
                    ctx.beginPath();
                    ctx.arc(gx, 415, 28, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = "#222";
                    ctx.lineWidth = 4;
                    ctx.stroke();
                }
                ctx.restore();
                
                // 반동 회복
                if (recoilOffset > 0) recoilOffset *= 0.85;
                if (recoilOffset < 0.1) recoilOffset = 0;
            }

            function gameLoop() {
                const now = Date.now();
                if (now - lastTargetTime > 1500) {
                    createTarget();
                    lastTargetTime = now;
                }
                targets = targets.filter(t => now - t.createdAt < TARGET_DURATION);

                ctx.clearRect(0, 0, 800, 600);
                
                drawBackground();

                targets.forEach(t => {
                    let tx = t.x + view.x + centerX;
                    let ty = t.y + view.y + centerY;
                    let r = t.radius;
                    if (isZoomed) {
                        tx = (tx - centerX) * ZOOM_FACTOR + centerX;
                        ty = (ty - centerY) * ZOOM_FACTOR + centerY;
                        r *= ZOOM_FACTOR;
                    }
                    drawDetailedRobot(tx, ty, r);
                });
                
                drawMuzzleFlash();
                drawGun();
                
                // 지향 사격 조준점
                if (!isZoomed && document.pointerLockElement === canvas) {
                    ctx.fillStyle = "rgba(0, 255, 204, 0.5)";
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
                    ctx.fill();
                }

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
