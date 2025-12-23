import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="스나이퍼 저격 게임", layout="centered")

def main():
    st.title("🎯 1인칭 스나이퍼 저격 게임")
    st.markdown("""
    ### 조작 방법
    - **마우스 왼쪽 클릭**: 발사 (화염 임팩트 및 총기 반동)
    - **마우스 오른쪽 클릭**: 줌 인/아웃 (지향사격/조준사격 전환)
    - **목표**: 로봇 표적을 맞추어 점수를 올리세요!
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
            let recoilOffset = 0; // 사격 시 총기 반동
            const mouse = { x: 400, y: 300 };
            let lastTargetTime = 0;
            const TARGET_DURATION = 2500;
            
            const ZOOM_FACTOR = 1.4;

            window.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                mouse.x = e.clientX - rect.left;
                mouse.y = e.clientY - rect.top;
            });

            window.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                isZoomed = !isZoomed;
                return false;
            });

            window.addEventListener('mousedown', (e) => {
                if (e.button === 0) { 
                    flashOpacity = 1.0; 
                    recoilOffset = 15; // 반동 수치
                    checkHit();
                }
            });

            function createTarget() {
                const x = 100 + Math.random() * 600;
                const y = 350 + Math.random() * 80; 
                targets.push({
                    x: x,
                    y: y,
                    radius: 22,
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

            function drawRobotHead(x, y, r) {
                ctx.save();
                ctx.fillStyle = "#bdc3c7";
                ctx.strokeStyle = "#7f8c8d";
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.roundRect(x - r, y - r, r * 2, r * 2, 5);
                ctx.fill();
                ctx.stroke();

                ctx.fillStyle = "#34495e";
                ctx.beginPath();
                ctx.roundRect(x - r * 0.7, y - r * 0.4, r * 1.4, r * 0.8, 2);
                ctx.fill();

                ctx.fillStyle = "#00f2ff";
                ctx.shadowBlur = 10;
                ctx.shadowColor = "#00f2ff";
                ctx.beginPath();
                ctx.arc(x - r * 0.35, y, r * 0.15, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(x + r * 0.35, y, r * 0.15, 0, Math.PI * 2);
                ctx.fill();
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
                drawRobotHead(x, y, r);
            }

            function drawValorantBackground() {
                // 천장 및 상단 벽
                ctx.fillStyle = "#1e272e";
                ctx.fillRect(0, 0, 800, 300);
                
                // 중간 구조물 벽
                ctx.fillStyle = "#2f3640";
                ctx.fillRect(0, 150, 800, 150);
                
                // 그리드 패턴
                ctx.strokeStyle = "#3d444d";
                ctx.lineWidth = 1;
                for(let i=0; i<800; i+=100) {
                    ctx.beginPath();
                    ctx.moveTo(i, 150);
                    ctx.lineTo(i, 300);
                    ctx.stroke();
                }

                // 바닥 영역
                ctx.fillStyle = "#353b48";
                ctx.fillRect(0, 300, 800, 300);
                
                // 바닥 원근 선
                ctx.strokeStyle = "#4b525d";
                ctx.beginPath();
                ctx.moveTo(0, 300); ctx.lineTo(100, 600);
                ctx.moveTo(800, 300); ctx.lineTo(700, 600);
                ctx.stroke();
                
                // 노란색 안전선
                ctx.fillStyle = "#e1b12c";
                ctx.fillRect(0, 300, 800, 5);
                ctx.fillRect(0, 580, 800, 20);
            }

            function drawMuzzleFlash() {
                if (flashOpacity <= 0) return;
                
                ctx.save();
                // 줌 상태일 때는 중앙, 아닐 때는 총구 끝 위치 (약 580, 380)
                const fx = isZoomed ? 400 : 580;
                const fy = isZoomed ? 300 : 380 + recoilOffset;
                
                const grad = ctx.createRadialGradient(fx, fy, 0, fx, fy, isZoomed ? 80 : 50);
                grad.addColorStop(0, `rgba(255, 255, 180, ${flashOpacity})`);
                grad.addColorStop(0.4, `rgba(255, 120, 0, ${flashOpacity * 0.7})`);
                grad.addColorStop(1, `rgba(255, 50, 0, 0)`);
                
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(fx, fy, isZoomed ? 80 : 50, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.restore();
                flashOpacity -= 0.12; 
            }

            function drawGun() {
                ctx.save();
                if (isZoomed) {
                    // 스코프 뷰
                    ctx.fillStyle = "rgba(0, 0, 0, 0.92)";
                    ctx.beginPath();
                    ctx.arc(400, 300, 280, 0, Math.PI * 2, true);
                    ctx.rect(0, 0, 800, 600);
                    ctx.fill();

                    // 조준선
                    ctx.strokeStyle = "#00ffcc";
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(120, 300); ctx.lineTo(680, 300);
                    ctx.moveTo(400, 20); ctx.lineTo(400, 580);
                    ctx.stroke();

                    // 중앙 정밀 도트
                    ctx.fillStyle = "#ff3333";
                    ctx.beginPath();
                    ctx.arc(400, 300, 2, 0, Math.PI * 2);
                    ctx.fill();

                    // 스코프 외곽 링
                    ctx.strokeStyle = "#111";
                    ctx.lineWidth = 20;
                    ctx.beginPath();
                    ctx.arc(400, 300, 280, 0, Math.PI * 2);
                    ctx.stroke();
                } else {
                    // 지향사격 총기 렌더링 (오른쪽 아래)
                    const gx = 650;
                    const gy = 450 + recoilOffset; // 반동 적용

                    ctx.shadowBlur = 15;
                    ctx.shadowColor = "black";

                    // 총 몸통 (스나이퍼 라이플 실루엣)
                    ctx.fillStyle = "#1e272e";
                    ctx.beginPath();
                    ctx.moveTo(gx + 200, gy + 200); // 오른쪽 아래 끝
                    ctx.lineTo(gx - 100, gy + 130); // 총열 아래
                    ctx.lineTo(gx - 80, gy - 60);   // 총구 끝 상단
                    ctx.lineTo(gx + 200, gy - 100); // 상단 뒤쪽
                    ctx.closePath();
                    ctx.fill();

                    // 스코프 마운트 부분
                    ctx.fillStyle = "#2f3640";
                    ctx.fillRect(gx + 50, gy - 110, 80, 30);
                    
                    // 총열 세부 묘사
                    ctx.fillStyle = "#111";
                    ctx.fillRect(gx - 90, gy - 65, 25, 40); // 가늠쇠 뭉치
                    
                    // 텍스처 느낌의 라인
                    ctx.strokeStyle = "#3d444d";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(gx + 50, gy);
                    ctx.lineTo(gx + 150, gy - 20);
                    ctx.stroke();
                }
                ctx.restore();
                
                // 반동 회복
                if (recoilOffset > 0) recoilOffset *= 0.8;
            }

            function gameLoop() {
                const now = Date.now();
                if (now - lastTargetTime > 1200) {
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
