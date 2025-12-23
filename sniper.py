import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="스나이퍼 저격 게임", layout="centered")

def main():
    st.title("🎯 택티컬 실내 사격장 슈팅")
    st.markdown("""
    ### 조작 방법
    - **마우스 이동**: 조준선과 총기가 커서를 따라 움직입니다.
    - **마우스 왼쪽 클릭**: 발사 (총구 화염 이펙트)
    - **마우스 오른쪽 클릭**: 정밀 조준 (줌)
    """)

    # 게임 로직 (HTML/JS/Canvas)
    game_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; overflow: hidden; font-family: sans-serif; cursor: none; user-select: none; background-color: #000; }
            #game-container { position: relative; width: 800px; height: 600px; background: #000; border: 4px solid #333; margin: auto; border-radius: 8px; overflow: hidden; }
            canvas { display: block; }
            #ui { position: absolute; top: 15px; left: 15px; color: #fff; text-shadow: 0 0 10px #00f2ff; font-size: 26px; font-weight: bold; pointer-events: none; z-index: 10; font-family: 'Courier New', Courier, monospace; font-style: italic; }
        </style>
    </head>
    <body oncontextmenu="return false;">
        <div id="game-container">
            <div id="ui">SCORE: <span id="score">0000</span></div>
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
            
            // 마우스 현재 위치 (조준점)
            let mouseX = 400;
            let mouseY = 300;
            
            const TARGET_DURATION = 4000;
            const ZOOM_FACTOR = 1.8;

            // 마우스 위치 업데이트
            canvas.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                mouseX = e.clientX - rect.left;
                mouseY = e.clientY - rect.top;
            });

            canvas.addEventListener('mousedown', (e) => {
                if (e.button === 0) fire();
                if (e.button === 2) isZoomed = !isZoomed;
            });

            function fire() {
                flashOpacity = 1.0; 
                recoilOffset = 50; 
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
                ctx.fillStyle = "#e0e0e0";
                ctx.beginPath();
                ctx.moveTo(-r*0.5, r);
                ctx.lineTo(-r*0.7, -r*0.5);
                ctx.quadraticCurveTo(0, -r*1.5, r*0.7, -r*0.5);
                ctx.lineTo(r*0.5, r);
                ctx.fill();
                ctx.strokeStyle = "#999";
                ctx.stroke();
                ctx.restore();
            }

            function drawRangeBackground() {
                // 바닥
                ctx.fillStyle = "#1e1e1e";
                ctx.fillRect(0, 350, 800, 250);
                // 천장
                ctx.fillStyle = "#2a2a2a";
                ctx.fillRect(0, 0, 800, 150);
                // 벽면
                ctx.fillStyle = "#333";
                ctx.fillRect(0, 150, 800, 200);

                // 네온 장식 (이미지 스타일)
                ctx.strokeStyle = "#00f2ff";
                ctx.lineWidth = 4;
                ctx.shadowBlur = 15;
                ctx.shadowColor = "#00f2ff";
                ctx.beginPath();
                ctx.moveTo(0, 350); ctx.lineTo(200, 350); ctx.lineTo(200, 150);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(800, 350); ctx.lineTo(600, 350); ctx.lineTo(600, 150);
                ctx.stroke();
                ctx.shadowBlur = 0;
            }

            function drawHandsAndGun() {
                ctx.save();
                
                // 마우스 위치에 따른 총기 각도 계산
                const dx = mouseX - 400;
                const dy = mouseY - 600;
                const angle = Math.atan2(dy, dx) + Math.PI / 2;

                const gx = 400 + (dx * 0.1); // 중심에서 살짝 이동
                const gy = 600 - recoilOffset + (dy * 0.05);

                ctx.translate(gx, gy);
                ctx.rotate(angle * 0.5); // 너무 급격하지 않게 회전

                // 소매
                ctx.fillStyle = "#0a0a0a";
                ctx.fillRect(-150, 0, 80, 200);
                ctx.fillRect(70, 0, 80, 200);

                // 손
                ctx.fillStyle = "#d2b48c";
                ctx.beginPath();
                ctx.ellipse(-40, -20, 40, 70, -0.2, 0, Math.PI*2); // 왼손
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(40, -20, 40, 70, 0.2, 0, Math.PI*2); // 오른손
                ctx.fill();

                // 권총
                ctx.fillStyle = "#1a1a1a";
                ctx.fillRect(-30, -140, 60, 120);
                ctx.fillStyle = "#000";
                ctx.fillRect(-33, -145, 66, 40);
                
                // 가늠쇠
                ctx.fillStyle = "#fff";
                ctx.fillRect(-2, -150, 4, 6);

                ctx.restore();
                
                // 조준선 (마우스 커서 위치에 고정)
                ctx.save();
                ctx.translate(mouseX, mouseY);
                if(isZoomed) ctx.scale(1.5, 1.5);

                ctx.strokeStyle = "#00f2ff";
                ctx.lineWidth = 3;
                ctx.shadowBlur = 10;
                ctx.shadowColor = "#00f2ff";
                
                ctx.beginPath();
                ctx.arc(0, 0, 40, 0, Math.PI*2);
                ctx.stroke();
                
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(-50, 0); ctx.lineTo(-10, 0);
                ctx.moveTo(50, 0); ctx.lineTo(10, 0);
                ctx.moveTo(0, -50); ctx.lineTo(0, -10);
                ctx.moveTo(0, 50); ctx.lineTo(0, 10);
                ctx.stroke();

                ctx.fillStyle = "red";
                ctx.beginPath();
                ctx.arc(0, 0, 3, 0, Math.PI*2);
                ctx.fill();
                
                ctx.restore();

                if (recoilOffset > 0) recoilOffset *= 0.8;
            }

            function drawMuzzleFlash() {
                if (flashOpacity <= 0) return;
                ctx.save();
                // 총구 위치 추적 (마우스 방향)
                const dx = mouseX - 400;
                const dy = mouseY - 600;
                const fx = 400 + (dx * 0.3);
                const fy = 600 + (dy * 0.5) - recoilOffset;

                const grad = ctx.createRadialGradient(fx, fy, 0, fx, fy, 120);
                grad.addColorStop(0, `rgba(255, 255, 200, ${flashOpacity})`);
                grad.addColorStop(0.4, `rgba(255, 150, 50, ${flashOpacity * 0.8})`);
                grad.addColorStop(1, "rgba(255, 100, 0, 0)");
                
                ctx.fillStyle = grad;
                ctx.globalCompositeOperation = "lighter";
                ctx.beginPath();
                ctx.arc(fx, fy, 120, 0, Math.PI*2);
                ctx.fill();
                
                ctx.restore();
                flashOpacity -= 0.15;
            }

            function gameLoop() {
                const now = Date.now();
                if (now - lastTargetTime > 1500) {
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
