import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="스나이퍼 저격 게임", layout="centered")

def main():
    st.title("🎯 택티컬 실내 사격장 슈팅")
    st.markdown("""
    ### 조작 방법
    - **화면 클릭**: 사격 시작 (마우스 고정)
    - **마우스 이동**: 시야 조절 (화면이 마우스에 따라 움직입니다)
    - **마우스 왼쪽 클릭**: 발사
    - **마우스 오른쪽 클릭**: 줌 인/아웃
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
            #game-container { position: relative; width: 800px; height: 600px; background: #000; border: 4px solid #444; margin: auto; border-radius: 8px; overflow: hidden; }
            canvas { display: block; }
            #ui { position: absolute; top: 15px; left: 15px; color: #fff; text-shadow: 0 0 10px #00ffcc; font-size: 24px; font-weight: bold; pointer-events: none; z-index: 10; font-family: 'monospace'; }
            #msg { position: absolute; bottom: 20px; width: 100%; text-align: center; color: #00ffcc; font-size: 16px; pointer-events: none; z-index: 5; text-transform: uppercase; letter-spacing: 2px; }
        </style>
    </head>
    <body oncontextmenu="return false;">
        <div id="game-container">
            <div id="ui">SCORE: <span id="score">0000</span></div>
            <div id="msg">CLICK TO START MISSION</div>
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
            
            // 시야 위치 (마우스 이동에 의해 변화함)
            const view = { x: 0, y: 0 };
            
            const TARGET_DURATION = 5000;
            const ZOOM_FACTOR = 1.4;
            const SENSITIVITY = 1.2;
            const ZOOM_SENSITIVITY = 0.4;

            canvas.addEventListener('click', () => {
                canvas.requestPointerLock();
                document.getElementById('msg').style.display = 'none';
            });

            document.addEventListener('mousemove', (e) => {
                if (document.pointerLockElement === canvas) {
                    const sens = isZoomed ? ZOOM_SENSITIVITY : SENSITIVITY;
                    // 마우스 이동 데이터를 누적하여 시야 좌표 업데이트
                    view.x -= e.movementX * sens;
                    view.y -= e.movementY * sens;
                    
                    // 시야 제한 (사격장 범위를 벗어나지 않게)
                    view.x = Math.max(-800, Math.min(800, view.x));
                    view.y = Math.max(-200, Math.min(200, view.y));
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
                    recoilOffset = 35; 
                    checkHit();
                }
            });

            function createTarget() {
                // 월드 내 무작위 위치에 타겟 생성
                const x = (Math.random() - 0.5) * 1200;
                const y = Math.random() * 50 + 20; 
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
                    // 타겟의 화면상 위치 계산
                    const tx = t.x + view.x + centerX;
                    const ty = t.y + view.y + centerY;

                    const dist = Math.sqrt((centerX - tx)**2 + (centerY - ty)**2);
                    const hitLimit = t.radius;

                    if (dist < hitLimit) {
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
                
                // 타겟 판 (사람 형태의 실루엣)
                ctx.fillStyle = "#fff";
                ctx.strokeStyle = "#444";
                ctx.lineWidth = 2;
                
                // 머리
                ctx.beginPath();
                ctx.arc(0, -r*0.8, r*0.4, 0, Math.PI*2);
                ctx.fill();
                ctx.stroke();
                
                // 몸통
                ctx.beginPath();
                ctx.ellipse(0, 0, r*0.7, r, 0, 0, Math.PI*2);
                ctx.fill();
                ctx.stroke();

                // 조준점 표시
                ctx.strokeStyle = "rgba(255, 0, 0, 0.3)";
                ctx.beginPath();
                ctx.arc(0, 0, r*0.3, 0, Math.PI*2);
                ctx.stroke();
                
                ctx.restore();
            }

            function drawIndoorRange() {
                ctx.save();
                ctx.translate(view.x, view.y);

                // 바닥
                ctx.fillStyle = "#1a1a1a";
                ctx.fillRect(-2000, 300, 4000, 1000);
                
                // 천장
                ctx.fillStyle = "#222";
                ctx.fillRect(-2000, -1000, 4000, 1300);

                // 좌우 벽
                const wallGradLeft = ctx.createLinearGradient(-800, 0, -200, 0);
                wallGradLeft.addColorStop(0, "#111");
                wallGradLeft.addColorStop(1, "#333");
                ctx.fillStyle = wallGradLeft;
                ctx.fillRect(-1200, -1000, 400, 2000);

                const wallGradRight = ctx.createLinearGradient(400, 0, 1000, 0);
                wallGradRight.addColorStop(0, "#333");
                wallGradRight.addColorStop(1, "#111");
                ctx.fillStyle = wallGradRight;
                ctx.fillRect(800, -1000, 400, 2000);

                // 네온 조명 라인 (이미지 스타일)
                ctx.strokeStyle = "#00f2ff";
                ctx.lineWidth = 4;
                ctx.shadowBlur = 10;
                ctx.shadowColor = "#00f2ff";
                
                // 좌측 라인
                ctx.beginPath();
                ctx.moveTo(-750, -200); ctx.lineTo(-750, 400); ctx.lineTo(-400, 400);
                ctx.stroke();
                
                // 우측 라인
                ctx.beginPath();
                ctx.moveTo(750, -200); ctx.lineTo(750, 400); ctx.lineTo(400, 400);
                ctx.stroke();

                // 천장 조명
                ctx.fillStyle = "#fff";
                ctx.shadowBlur = 20;
                ctx.shadowColor = "#fff";
                for(let i=0; i<3; i++) {
                    ctx.fillRect(-150, -400 + (i*150), 300, 40);
                }

                ctx.restore();
            }

            function drawHandsAndGun() {
                ctx.save();
                const gx = centerX;
                const gy = 600 - recoilOffset + Math.sin(Date.now()/300)*3;

                // 줌 상태일 때는 총을 투명하게 하거나 조준선만 강조
                if (isZoomed) {
                    ctx.globalAlpha = 0.2;
                }

                // 소매
                ctx.fillStyle = "#1e1e1e";
                ctx.beginPath();
                ctx.moveTo(gx - 180, 600);
                ctx.lineTo(gx - 100, 450);
                ctx.lineTo(gx - 20, 450);
                ctx.lineTo(gx - 20, 600);
                ctx.fill();

                ctx.beginPath();
                ctx.moveTo(gx + 180, 600);
                ctx.lineTo(gx + 100, 450);
                ctx.lineTo(gx + 20, 450);
                ctx.lineTo(gx + 20, 600);
                ctx.fill();

                // 피부 (양손 파지)
                ctx.fillStyle = "#e0ac69";
                ctx.beginPath();
                ctx.ellipse(gx - 40, gy - 20, 45, 80, -0.2, 0, Math.PI*2); // 왼손
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(gx + 40, gy - 20, 45, 80, 0.2, 0, Math.PI*2); // 오른손
                ctx.fill();

                // 권총 (뒷면)
                ctx.fillStyle = "#1a1a1a";
                ctx.fillRect(gx - 30, gy - 140, 60, 120); // 슬라이드 뒤
                ctx.fillStyle = "#000";
                ctx.fillRect(gx - 35, gy - 145, 70, 40); // 가늠쇠 뭉치
                
                // 가늠쇠 포인트
                ctx.fillStyle = "#fff";
                ctx.fillRect(gx - 2, gy - 150, 4, 6);

                ctx.restore();
                
                // 조준선 (이미지 스타일의 청록색 십자선)
                ctx.save();
                ctx.strokeStyle = "#00f2ff";
                ctx.lineWidth = 2;
                ctx.shadowBlur = 10;
                ctx.shadowColor = "#00f2ff";
                
                // 원형 조준선
                ctx.beginPath();
                ctx.arc(centerX, centerY, isZoomed ? 60 : 50, 0, Math.PI*2);
                ctx.stroke();
                
                // 십자선
                ctx.beginPath();
                ctx.moveTo(centerX - 30, centerY); ctx.lineTo(centerX - 10, centerY);
                ctx.moveTo(centerX + 30, centerY); ctx.lineTo(centerX + 10, centerY);
                ctx.moveTo(centerX, centerY - 30); ctx.lineTo(centerX, centerY - 10);
                ctx.moveTo(centerX, centerY + 30); ctx.lineTo(centerX, centerY + 10);
                ctx.stroke();

                // 중앙 도트
                ctx.fillStyle = "red";
                ctx.beginPath();
                ctx.arc(centerX, centerY, 2, 0, Math.PI*2);
                ctx.fill();
                
                ctx.restore();

                if (recoilOffset > 0) recoilOffset *= 0.85;
            }

            function drawMuzzleFlash() {
                if (flashOpacity <= 0) return;
                ctx.save();
                const fy = isZoomed ? centerY : centerY + 50;
                const grad = ctx.createRadialGradient(centerX, fy, 0, centerX, fy, 120);
                grad.addColorStop(0, `rgba(255, 255, 150, ${flashOpacity})`);
                grad.addColorStop(1, "rgba(255, 100, 0, 0)");
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(centerX, fy, 120, 0, Math.PI*2);
                ctx.fill();
                ctx.restore();
                flashOpacity -= 0.2;
            }

            function gameLoop() {
                const now = Date.now();
                if (now - lastTargetTime > 1800) {
                    createTarget();
                    lastTargetTime = now;
                }
                targets = targets.filter(t => now - t.createdAt < TARGET_DURATION);

                ctx.clearRect(0, 0, 800, 600);
                
                // 배경 드로잉
                drawIndoorRange();

                // 타겟 드로잉
                targets.forEach(t => {
                    const tx = t.x + view.x + centerX;
                    const ty = t.y + view.y + centerY;
                    drawTargetBoard(tx, ty, t.radius);
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
