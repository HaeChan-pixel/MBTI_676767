import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="스나이퍼 저격 게임", layout="centered")

def main():
    st.title("🎯 택티컬 실내 사격장 슈팅")
    st.markdown("""
    ### 조작 방법
    - **화면 클릭**: 사격 시작 (마우스 고정 필수!)
    - **마우스 이동**: 화면이 마우스 방향을 따라 실시간으로 움직입니다.
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
            body { margin: 0; overflow: hidden; font-family: sans-serif; cursor: crosshair; user-select: none; background-color: #000; }
            #game-container { position: relative; width: 800px; height: 600px; background: #000; border: 4px solid #333; margin: auto; border-radius: 8px; overflow: hidden; }
            canvas { display: block; }
            #ui { position: absolute; top: 15px; left: 15px; color: #fff; text-shadow: 0 0 10px #00f2ff; font-size: 26px; font-weight: bold; pointer-events: none; z-index: 10; font-family: 'Courier New', Courier, monospace; font-style: italic; }
            #msg { position: absolute; top: 50%; width: 100%; text-align: center; color: #00f2ff; font-size: 20px; pointer-events: none; z-index: 5; text-transform: uppercase; letter-spacing: 3px; transform: translateY(-50%); animation: blink 1.5s infinite; }
            @keyframes blink { 0% { opacity: 0.2; } 50% { opacity: 1; } 100% { opacity: 0.2; } }
        </style>
    </head>
    <body oncontextmenu="return false;">
        <div id="game-container">
            <div id="ui">SCORE: <span id="score">0000</span></div>
            <div id="msg">CLICK TO LOCK MOUSE & START</div>
            <canvas id="gameCanvas" width="800" height="600"></canvas>
        </div>

        <script>
            const canvas = document.getElementById('gameCanvas');
            const ctx = canvas.getContext('2d');
            const scoreElement = document.getElementById('score');
            const msgElement = document.getElementById('msg');

            let score = 0;
            let isZoomed = false;
            let targets = [];
            let casings = []; // 바닥 탄피 효과
            let flashOpacity = 0; 
            let recoilOffset = 0; 
            
            const centerX = 400;
            const centerY = 300;
            
            // 시야 위치 - 초기값 0
            let viewX = 0;
            let viewY = 0;
            
            const TARGET_DURATION = 4000;
            const ZOOM_FACTOR = 1.5;
            const SENSITIVITY = 1.5; // 민감도 상향
            const ZOOM_SENSITIVITY = 0.5;

            // 마우스 고정 이벤트
            canvas.addEventListener('mousedown', (e) => {
                if (document.pointerLockElement !== canvas) {
                    canvas.requestPointerLock();
                } else if (e.button === 0) {
                    fire();
                }
            });

            document.addEventListener('pointerlockchange', () => {
                if (document.pointerLockElement === canvas) {
                    msgElement.style.display = 'none';
                } else {
                    msgElement.style.display = 'block';
                }
            });

            // 마우스 이동 로직 (화면 이동의 핵심)
            document.addEventListener('mousemove', (e) => {
                if (document.pointerLockElement === canvas) {
                    const sens = isZoomed ? ZOOM_SENSITIVITY : SENSITIVITY;
                    
                    // 마우스 이동량을 view 좌표에 누적
                    viewX -= e.movementX * sens;
                    viewY -= e.movementY * sens;
                    
                    // 이동 범위 제한 (사격장 내부)
                    viewX = Math.max(-1000, Math.min(1000, viewX));
                    viewY = Math.max(-250, Math.min(250, viewY));
                }
            });

            window.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                if (document.pointerLockElement === canvas) {
                    isZoomed = !isZoomed;
                }
                return false;
            });

            function fire() {
                flashOpacity = 1.0; 
                recoilOffset = 40; 
                
                // 탄피 생성
                casings.push({
                    x: centerX + 50,
                    y: 550,
                    vx: 5 + Math.random() * 5,
                    vy: -10 - Math.random() * 5,
                    rotation: 0,
                    rv: Math.random() * 0.5
                });

                checkHit();
            }

            function createTarget() {
                const x = (Math.random() - 0.5) * 1600;
                const y = (Math.random() * 80) - 20; 
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
                    // 월드 좌표를 화면 좌표로 환산
                    const tx = t.x + viewX + centerX;
                    const ty = t.y + viewY + centerY;

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
                
                // 그림자
                ctx.shadowBlur = 15;
                ctx.shadowColor = "rgba(0,0,0,0.5)";

                // 타겟 실루엣 (흰색/회색)
                ctx.fillStyle = "#e0e0e0";
                ctx.beginPath();
                ctx.moveTo(-r*0.5, r);
                ctx.lineTo(-r*0.7, -r*0.5);
                ctx.quadraticCurveTo(0, -r*1.5, r*0.7, -r*0.5);
                ctx.lineTo(r*0.5, r);
                ctx.fill();

                // 조준 원형 라인
                ctx.strokeStyle = "#999";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.arc(0, -r*0.2, r*0.4, 0, Math.PI*2);
                ctx.stroke();
                ctx.beginPath();
                ctx.arc(0, -r*0.2, r*0.2, 0, Math.PI*2);
                ctx.stroke();

                ctx.restore();
            }

            function drawRangeBackground() {
                ctx.save();
                ctx.translate(viewX, viewY);

                // 바닥 (어두운 회색 콘크리트)
                ctx.fillStyle = "#1e1e1e";
                ctx.fillRect(-2000, 300, 4000, 1000);
                
                // 천장
                ctx.fillStyle = "#2a2a2a";
                ctx.fillRect(-2000, -1000, 4000, 1300);

                // 벽면 텍스처 (이미지의 콘크리트 패널 느낌)
                ctx.fillStyle = "#333";
                ctx.fillRect(-1500, -200, 3000, 500); // 정면 벽
                
                // 벽면 수직 라인 (패널 구분)
                ctx.strokeStyle = "#222";
                ctx.lineWidth = 2;
                for(let i=-1500; i<=1500; i+=300) {
                    ctx.beginPath();
                    ctx.moveTo(i, -200); ctx.lineTo(i, 300);
                    ctx.stroke();
                }

                // 사진의 핵심: 청록색 네온 장식 라인
                ctx.strokeStyle = "#00f2ff";
                ctx.lineWidth = 4;
                ctx.shadowBlur = 15;
                ctx.shadowColor = "#00f2ff";
                
                // 좌측 지그재그 라인
                ctx.beginPath();
                ctx.moveTo(-1200, 300); ctx.lineTo(-800, 300); ctx.lineTo(-800, -100); ctx.lineTo(-400, -100);
                ctx.stroke();
                
                // 우측 지그재그 라인
                ctx.beginPath();
                ctx.moveTo(1200, 300); ctx.lineTo(800, 300); ctx.lineTo(800, -100); ctx.lineTo(400, -100);
                ctx.stroke();

                // 천장 매립형 조명 (사진의 긴 사각형 조명)
                ctx.shadowBlur = 20;
                ctx.shadowColor = "#fff";
                ctx.fillStyle = "#fff";
                for(let i=0; i<3; i++) {
                    ctx.fillRect(-200, -600 + (i*200), 400, 60);
                }

                ctx.restore();
            }

            function drawCasings() {
                ctx.save();
                ctx.fillStyle = "#d4af37"; // 금색 탄피
                casings.forEach((c, i) => {
                    ctx.save();
                    ctx.translate(c.x, c.y);
                    ctx.rotate(c.rotation);
                    ctx.fillRect(-2, -5, 4, 10);
                    ctx.restore();
                    
                    // 물리 효과
                    c.x += c.vx;
                    c.y += c.vy;
                    c.vy += 0.8; // 중력
                    c.rotation += c.rv;
                    
                    if (c.y > 580) { // 바닥 충돌
                        c.y = 580;
                        c.vy *= -0.3;
                        c.vx *= 0.8;
                    }
                });
                if (casings.length > 20) casings.shift();
                ctx.restore();
            }

            function drawHandsAndGun() {
                ctx.save();
                const bounce = Math.sin(Date.now()/400)*2;
                const gx = centerX;
                const gy = 600 - recoilOffset + bounce;

                if (isZoomed) {
                    ctx.globalAlpha = 0.3;
                }

                // 소매 (검은색 전술복)
                ctx.fillStyle = "#0a0a0a";
                ctx.beginPath();
                ctx.moveTo(gx - 200, 600); ctx.lineTo(gx - 110, 480); ctx.lineTo(gx - 40, 480); ctx.lineTo(gx - 40, 600);
                ctx.fill();
                ctx.beginPath();
                ctx.moveTo(gx + 200, 600); ctx.lineTo(gx + 110, 480); ctx.lineTo(gx + 40, 480); ctx.lineTo(gx + 40, 600);
                ctx.fill();

                // 양손 파지
                ctx.fillStyle = "#d2b48c";
                ctx.beginPath();
                ctx.ellipse(gx - 45, gy - 20, 50, 85, -0.15, 0, Math.PI*2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(gx + 45, gy - 20, 50, 85, 0.15, 0, Math.PI*2);
                ctx.fill();

                // 권총 몸체 (이미지 상의 검은색 핸드건 뒷모습)
                ctx.fillStyle = "#1a1a1a";
                ctx.fillRect(gx - 35, gy - 160, 70, 140);
                ctx.fillStyle = "#000";
                ctx.fillRect(gx - 38, gy - 165, 76, 45); // 슬라이드 상단
                
                // 가늠쇠 조준점
                ctx.fillStyle = "#fff";
                ctx.fillRect(gx - 3, gy - 172, 6, 8);

                ctx.restore();
                
                // 조준 리티클 (청록색 네온 원형)
                ctx.save();
                ctx.strokeStyle = "#00f2ff";
                ctx.lineWidth = 3;
                ctx.shadowBlur = 12;
                ctx.shadowColor = "#00f2ff";
                
                const rSize = isZoomed ? 70 : 55;
                ctx.beginPath();
                ctx.arc(centerX, centerY, rSize, 0, Math.PI*2);
                ctx.stroke();
                
                // 십자 가이드
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(centerX - rSize - 15, centerY); ctx.lineTo(centerX - rSize + 5, centerY);
                ctx.moveTo(centerX + rSize + 15, centerY); ctx.lineTo(centerX + rSize - 5, centerY);
                ctx.moveTo(centerX, centerY - rSize - 15); ctx.lineTo(centerX, centerY - rSize + 5);
                ctx.moveTo(centerX, centerY + rSize + 15); ctx.lineTo(centerX, centerY + rSize - 5);
                ctx.stroke();

                // 중앙 레드 닷
                ctx.fillStyle = "red";
                ctx.shadowBlur = 5;
                ctx.shadowColor = "red";
                ctx.beginPath();
                ctx.arc(centerX, centerY, 3, 0, Math.PI*2);
                ctx.fill();
                
                ctx.restore();

                if (recoilOffset > 0) recoilOffset *= 0.82;
            }

            function drawMuzzleFlash() {
                if (flashOpacity <= 0) return;
                ctx.save();
                const fy = isZoomed ? centerY : centerY + 40;
                const grad = ctx.createRadialGradient(centerX, fy, 0, centerX, fy, 150);
                grad.addColorStop(0, `rgba(255, 255, 200, ${flashOpacity})`);
                grad.addColorStop(0.5, `rgba(255, 100, 0, ${flashOpacity * 0.5})`);
                grad.addColorStop(1, "rgba(255, 100, 0, 0)");
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(centerX, fy, 150, 0, Math.PI*2);
                ctx.fill();
                ctx.restore();
                flashOpacity -= 0.15;
            }

            function gameLoop() {
                const now = Date.now();
                if (now - lastTargetTime > 1600) {
                    createTarget();
                    lastTargetTime = now;
                }
                targets = targets.filter(t => now - t.createdAt < TARGET_DURATION);

                ctx.clearRect(0, 0, 800, 600);
                
                drawRangeBackground();

                targets.forEach(t => {
                    const tx = t.x + viewX + centerX;
                    const ty = t.y + viewY + centerY;
                    drawTargetBoard(tx, ty, t.radius);
                });
                
                drawCasings();
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
