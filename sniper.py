import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="스나이퍼 저격 게임", layout="centered")

def main():
    st.title("🎯 1인칭 스나이퍼 저격 게임 (AWM Edition)")
    st.markdown("""
    ### 조작 방법
    - **마우스 왼쪽 클릭**: 발사 (발사 후 조준이 해제됩니다)
    - **마우스 오른쪽 클릭**: 줌 인/아웃 (AWM 전용 스코프)
    - **목표**: 디테일해진 로봇 표적을 맞추어 높은 점수를 기록하세요!
    """)

    # 게임 로직 (HTML/JS/Canvas)
    game_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; overflow: hidden; font-family: sans-serif; cursor: crosshair; user-select: none; background-color: #000; }
            #game-container { position: relative; width: 800px; height: 600px; background: #2c3e50; border: 5px solid #1a1a1a; margin: auto; border-radius: 10px; overflow: hidden; }
            canvas { display: block; }
            #ui { position: absolute; top: 15px; left: 15px; color: #00ffcc; text-shadow: 2px 2px 4px #000; font-size: 28px; font-weight: bold; pointer-events: none; z-index: 10; font-family: 'Courier New', Courier, monospace; }
        </style>
    </head>
    <body oncontextmenu="return false;">
        <div id="game-container">
            <div id="ui">SCORE: <span id="score">0</span></div>
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
            const mouse = { x: 400, y: 300 };
            const actualMouse = { x: 400, y: 300 }; // 감도 조절을 위한 실제 마우스 좌표
            let lastTargetTime = 0;
            const TARGET_DURATION = 3000;
            
            // 조준경 배율 하향 조정 (기존 1.4 -> 1.25)
            const ZOOM_FACTOR = 1.25;
            // 줌 상태 감도 (0.5 = 50% 감도)
            const ZOOM_SENSITIVITY = 0.6;

            window.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                const newX = e.clientX - rect.left;
                const newY = e.clientY - rect.top;

                if (isZoomed) {
                    // 줌 상태일 때는 이동 거리를 제한하여 감도를 낮춤
                    const dx = newX - actualMouse.x;
                    const dy = newY - actualMouse.y;
                    mouse.x += dx * ZOOM_SENSITIVITY;
                    mouse.y += dy * ZOOM_SENSITIVITY;
                } else {
                    mouse.x = newX;
                    mouse.y = newY;
                }
                actualMouse.x = newX;
                actualMouse.y = newY;
            });

            window.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                isZoomed = !isZoomed;
                return false;
            });

            window.addEventListener('mousedown', (e) => {
                if (e.button === 0) { 
                    flashOpacity = 1.0; 
                    recoilOffset = 25; 
                    checkHit();
                    
                    // 사격 후 볼트 액션 모사를 위해 줌 해제
                    if (isZoomed) {
                        setTimeout(() => {
                            isZoomed = false;
                        }, 100);
                    }
                }
            });

            function createTarget() {
                const x = 100 + Math.random() * 600;
                const y = 350 + Math.random() * 80; 
                targets.push({
                    x: x,
                    y: y,
                    radius: 25,
                    createdAt: Date.now()
                });
            }

            function checkHit() {
                const shootX = isZoomed ? 400 : mouse.x;
                const shootY = isZoomed ? 300 : mouse.y;

                for (let i = targets.length - 1; i >= 0; i--) {
                    const t = targets[i];
                    let tx = t.x;
                    let ty = t.y;

                    if (isZoomed) {
                        tx = (t.x - mouse.x) * ZOOM_FACTOR + 400;
                        ty = (t.y - mouse.y) * ZOOM_FACTOR + 300;
                    }

                    const dist = Math.sqrt((shootX - tx)**2 + (shootY - ty)**2);
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
                
                // 그림자
                ctx.fillStyle = "rgba(0,0,0,0.2)";
                ctx.beginPath();
                ctx.ellipse(x, y + r * 1.5, r, r * 0.3, 0, 0, Math.PI * 2);
                ctx.fill();

                // 몸체 (금속성 느낌)
                ctx.fillStyle = "#576574";
                ctx.strokeStyle = "#222f3e";
                ctx.lineWidth = 2;
                
                // 가슴/배
                ctx.beginPath();
                ctx.roundRect(x - r * 0.8, y - r * 0.2, r * 1.6, r * 1.2, 4);
                ctx.fill();
                ctx.stroke();

                // 머리 연결부
                ctx.fillStyle = "#222f3e";
                ctx.fillRect(x - r * 0.2, y - r * 0.4, r * 0.4, r * 0.3);

                // 머리
                ctx.fillStyle = "#8395a7";
                ctx.beginPath();
                ctx.roundRect(x - r * 0.6, y - r * 1.2, r * 1.2, r * 0.9, 5);
                ctx.fill();
                ctx.stroke();

                // 로봇 눈 (발로란트 봇 느낌 유지)
                ctx.fillStyle = "#ff9f43";
                ctx.shadowBlur = 8;
                ctx.shadowColor = "#ff9f43";
                ctx.beginPath();
                ctx.arc(x - r * 0.25, y - r * 0.8, r * 0.12, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(x + r * 0.25, y - r * 0.8, r * 0.12, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;

                // 안테나
                ctx.strokeStyle = "#222f3e";
                ctx.beginPath();
                ctx.moveTo(x, y - r * 1.2);
                ctx.lineTo(x + r * 0.4, y - r * 1.6);
                ctx.stroke();
                ctx.fillStyle = "red";
                ctx.beginPath();
                ctx.arc(x + r * 0.4, y - r * 1.6, r * 0.1, 0, Math.PI * 2);
                ctx.fill();

                // 팔
                ctx.fillStyle = "#576574";
                ctx.fillRect(x - r * 1.1, y, r * 0.3, r * 0.8); // 왼팔
                ctx.fillRect(x + r * 0.8, y, r * 0.3, r * 0.8); // 오른팔

                ctx.restore();
            }

            function drawTarget(t, zoomedMode = false) {
                let x = t.x;
                let y = t.y;
                let r = t.radius;

                if (zoomedMode) {
                    x = (t.x - mouse.x) * ZOOM_FACTOR + 400;
                    y = (t.y - mouse.y) * ZOOM_FACTOR + 300;
                    r = t.radius * ZOOM_FACTOR;
                }
                drawDetailedRobot(x, y, r);
            }

            function drawValorantBackground() {
                ctx.fillStyle = "#1e272e";
                ctx.fillRect(0, 0, 800, 300);
                ctx.fillStyle = "#2f3640";
                ctx.fillRect(0, 150, 800, 150);
                
                ctx.strokeStyle = "#3d444d";
                ctx.lineWidth = 1;
                for(let i=0; i<800; i+=100) {
                    ctx.beginPath();
                    ctx.moveTo(i, 150);
                    ctx.lineTo(i, 300);
                    ctx.stroke();
                }

                ctx.fillStyle = "#353b48";
                ctx.fillRect(0, 300, 800, 300);
                
                ctx.strokeStyle = "#4b525d";
                ctx.beginPath();
                ctx.moveTo(0, 300); ctx.lineTo(100, 600);
                ctx.moveTo(800, 300); ctx.lineTo(700, 600);
                ctx.stroke();
                
                ctx.fillStyle = "#e1b12c";
                ctx.fillRect(0, 300, 800, 5);
                ctx.fillRect(0, 580, 800, 20);
            }

            function drawMuzzleFlash() {
                if (flashOpacity <= 0) return;
                ctx.save();
                const fx = isZoomed ? 400 : 580;
                const fy = isZoomed ? 300 : 380 + recoilOffset;
                const grad = ctx.createRadialGradient(fx, fy, 0, fx, fy, isZoomed ? 60 : 40);
                grad.addColorStop(0, `rgba(255, 255, 180, ${flashOpacity})`);
                grad.addColorStop(0.4, `rgba(255, 150, 0, ${flashOpacity * 0.7})`);
                grad.addColorStop(1, `rgba(255, 50, 0, 0)`);
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(fx, fy, isZoomed ? 60 : 40, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
                flashOpacity -= 0.1; 
            }

            function drawGun() {
                ctx.save();
                if (isZoomed) {
                    // 스코프 뷰
                    ctx.fillStyle = "rgba(0, 0, 0, 0.95)";
                    ctx.beginPath();
                    ctx.arc(400, 300, 280, 0, Math.PI * 2, true);
                    ctx.rect(0, 0, 800, 600);
                    ctx.fill();

                    // 정밀한 AWM 스타일 조준선
                    ctx.strokeStyle = "rgba(0, 255, 204, 0.8)";
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    // 가로선
                    ctx.moveTo(150, 300); ctx.lineTo(650, 300);
                    // 세로선
                    ctx.moveTo(400, 50); ctx.lineTo(400, 550);
                    ctx.stroke();

                    // 거리 측정 눈금 (Mil-dot)
                    ctx.fillStyle = "#00ffcc";
                    for(let i = -150; i <= 150; i += 30) {
                        if(i === 0) continue;
                        ctx.beginPath();
                        ctx.arc(400 + i, 300, 2, 0, Math.PI * 2);
                        ctx.arc(400, 300 + i, 2, 0, Math.PI * 2);
                        ctx.fill();
                    }

                    // 중앙 정밀 도트
                    ctx.fillStyle = "#ff3333";
                    ctx.beginPath();
                    ctx.arc(400, 300, 3, 0, Math.PI * 2);
                    ctx.fill();

                    // 스코프 외곽 질감
                    ctx.strokeStyle = "#0a0a0a";
                    ctx.lineWidth = 25;
                    ctx.beginPath();
                    ctx.arc(400, 300, 280, 0, Math.PI * 2);
                    ctx.stroke();
                } else {
                    // AWM (에땁) 디자인 렌더링
                    const gx = 620;
                    const gy = 480 + recoilOffset;

                    // 그림자
                    ctx.shadowBlur = 20;
                    ctx.shadowColor = "black";

                    // 총 몸체 (Olive Drab 색상)
                    ctx.fillStyle = "#4b5320"; // 군용 국방색
                    ctx.beginPath();
                    ctx.moveTo(gx + 250, gy + 150);
                    ctx.lineTo(gx - 180, gy + 80);  // 긴 총열 아래
                    ctx.lineTo(gx - 180, gy + 60);  // 총구 끝
                    ctx.lineTo(gx - 50, gy + 50);   // 총열 상단
                    ctx.lineTo(gx + 50, gy - 20);   // 몸체 상단
                    ctx.lineTo(gx + 250, gy - 50);
                    ctx.closePath();
                    ctx.fill();

                    // 검정색 금속 부품 (방아쇠울, 하단부)
                    ctx.fillStyle = "#1e1e1e";
                    ctx.fillRect(gx + 20, gy + 50, 100, 40);
                    
                    // 스코프 (AWM 특유의 거대한 조준경)
                    ctx.fillStyle = "#111";
                    ctx.beginPath();
                    ctx.roundRect(gx + 20, gy - 60, 140, 45, 5);
                    ctx.fill();
                    // 조준경 앞뒤 렌즈 캡 느낌
                    ctx.fillRect(gx + 15, gy - 65, 20, 55);
                    ctx.fillRect(gx + 145, gy - 65, 15, 55);
                    
                    // 총구 브레이크 (AWM 특유의 끝부분)
                    ctx.fillStyle = "#111";
                    ctx.fillRect(gx - 200, gy + 55, 30, 30);
                }
                ctx.restore();
                
                if (recoilOffset > 0) recoilOffset *= 0.85;
            }

            function gameLoop() {
                const now = Date.now();
                if (now - lastTargetTime > 1400) {
                    createTarget();
                    lastTargetTime = now;
                }
                targets = targets.filter(t => now - t.createdAt < TARGET_DURATION);

                ctx.clearRect(0, 0, 800, 600);
                drawValorantBackground();
                targets.forEach(t => drawTarget(t, isZoomed));
                
                drawMuzzleFlash();
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
