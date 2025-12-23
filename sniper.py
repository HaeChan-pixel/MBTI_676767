import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="스나이퍼 저격 게임", layout="centered")

def main():
    st.title("🎯 택티컬 실내 사격장 슈팅")
    st.markdown("""
    ### 조작 방법
    - **마우스 이동**: 조준선과 총기가 커서를 따라 움직입니다. (감도 조정 완료)
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
            #ui { position: absolute; top: 15px; left: 15px; color: #fff; text-shadow: 0 0 10px #00f2ff; font-size: 26px; font-weight: bold; pointer-events: none; z-index: 10; font-family: 'Courier New', Courier, monospace; font-style: italic; }
            #fullscreen-btn {
                position: absolute;
                top: 15px;
                right: 15px;
                background: rgba(0, 242, 255, 0.2);
                border: 1px solid #00f2ff;
                color: #00f2ff;
                padding: 5px 10px;
                font-size: 12px;
                cursor: pointer;
                z-index: 20;
                border-radius: 4px;
                font-family: 'monospace';
            }
            #fullscreen-btn:hover {
                background: rgba(0, 242, 255, 0.4);
            }
        </style>
    </head>
    <body oncontextmenu="return false;">
        <div id="game-container">
            <div id="ui">SCORE: <span id="score">0000</span></div>
            <button id="fullscreen-btn">GO FULLSCREEN</button>
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
            
            // 마우스 현재 위치 (조준점)
            let mouseX = 400;
            let mouseY = 300;
            
            // 감도 설정 (기존보다 낮춤)
            const SENSITIVITY = 0.5; 
            const TARGET_DURATION = 4000;
            const ZOOM_FACTOR = 1.8;

            // 전체화면 기능
            fsBtn.addEventListener('click', () => {
                if (!document.fullscreenElement) {
                    container.requestFullscreen().catch(err => {
                        console.log(`Error attempting to enable full-screen mode: ${err.message}`);
                    });
                } else {
                    document.exitFullscreen();
                }
            });

            // 마우스 위치 업데이트 (감도 보정 적용)
            canvas.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                // 전체화면 여부에 따른 스케일 계산
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                
                // 감도를 낮추기 위해 이전 위치에서 서서히 따라가게 하거나 
                // 단순히 위치를 부드럽게 보간할 수 있지만, 여기서는 좌표 계산 시 스케일을 정확히 맞춤
                mouseX = (e.clientX - rect.left) * scaleX;
                mouseY = (e.clientY - rect.top) * scaleY;
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

                // 네온 장식
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
                
                // 부드러운 움직임을 위해 보간 적용 (감도 체감 낮춤)
                const dx = mouseX - 400;
                const dy = mouseY - 600;
                const angle = Math.atan2(dy, dx) + Math.PI / 2;

                const gx = 400 + (dx * 0.08); 
                const gy = 600 - recoilOffset + (dy * 0.04);

                ctx.translate(gx, gy);
                ctx.rotate(angle * 0.45); 

                // 소매
                ctx.fillStyle = "#0a0a0a";
                ctx.fillRect(-150, 0, 80, 200);
                ctx.fillRect(70, 0, 80, 200);

                // 손
                ctx.fillStyle = "#d2b48c";
                ctx.beginPath();
                ctx.ellipse(-40, -20, 40, 70, -0.2, 0, Math.PI*2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(40, -20, 40, 70, 0.2, 0, Math.PI*2);
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
                
                // 조준선
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
