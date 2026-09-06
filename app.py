# -*- coding: utf-8 -*-
"""
Web Dashboard & Server for Zefoy Bot on Render.com / Cloud Platforms
Developed by Sang Dev (@sangnguyendev | sangdev.online)
"""

import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
import requests

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from run import Zefoy, KEY_FILE, check_key_api, is_vip_key

app = Flask(__name__)

DEFAULT_SERVICES = [
    {"name": "Favorites", "status": "Online", "available": True},
    {"name": "Views", "status": "Offline / Soon will be update", "available": False},
    {"name": "Hearts", "status": "Offline / Soon will be update", "available": False},
    {"name": "Followers", "status": "Offline / Soon will be update", "available": False},
    {"name": "Shares", "status": "Offline / Soon will be update", "available": False},
    {"name": "Comments Hearts", "status": "Offline / Soon will be update", "available": False},
]

# --- In-Memory State Manager ---
class BotManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.bot = None
        self.thread = None
        self.is_running = False
        self.status = "Chưa khởi động"
        self.timer = 0
        self.last_sent = 0
        self.total_sent = 0
        self.video_url = os.environ.get("TIKTOK_URL", "")
        self.service = os.environ.get("ZEFOY_SERVICE", "Favorites")
        self.key = self._get_initial_key()
        self.logs = []
        self.video_stats = {}
        self.services_list = list(DEFAULT_SERVICES)
        self.start_time = time.time()

    def _get_initial_key(self):
        env_k = os.environ.get("ZEFOY_KEY", "").strip()
        if env_k:
            return env_k
        if os.path.exists(KEY_FILE):
            try:
                return open(KEY_FILE, "r", encoding="utf-8").read().strip()
            except Exception:
                pass
        return ""

    def add_log(self, text):
        now = datetime.now().strftime("%H:%M:%S")
        with self.lock:
            self.logs.append(f"[{now}] {text}")
            if len(self.logs) > 100:
                self.logs.pop(0)

    def on_status(self, status, last_sent, total_sent):
        with self.lock:
            self.status = status
            self.last_sent = last_sent
            self.total_sent = total_sent
        self.add_log(f"Trạng thái: {status}")

    def on_timer(self, seconds):
        with self.lock:
            self.timer = seconds

    def _worker(self, url, service, key):
        try:
            self.add_log(f"Bắt đầu phiên Zefoy cho dịch vụ: {service}")
            self.add_log(f"URL: {url}")
            
            bot = Zefoy(
                url=url,
                service=service,
                license_key=key,
                headless=True,
                on_status=self.on_status,
                on_timer=self.on_timer,
                on_log=self.add_log
            )
            with self.lock:
                self.bot = bot
                self.video_url = bot.url

            self.add_log("Đang lấy và giải Captcha tự động...")
            captcha_ok, ans = bot.send_captcha()
            if not captcha_ok:
                self.add_log("Giải Captcha thất bại, vui lòng thử lại!")
                with self.lock:
                    self.is_running = False
                    self.status = "Lỗi Captcha"
                return

            self.add_log(f"Captcha đã giải: {ans}. Đang chạy vòng lặp bot...")
            bot.run()

        except Exception as e:
            self.add_log(f"Lỗi tiến trình bot: {e}")
        finally:
            with self.lock:
                self.is_running = False
                self.status = "Đã dừng"
                self.timer = 0
            self.add_log("Tiến trình Zefoy đã kết thúc.")

    def start(self, url, service, key, restart_if_running=True):
        with self.lock:
            if self.is_running:
                if restart_if_running:
                    self.add_log("Phát hiện yêu cầu mới, đang khởi động lại bot cho dịch vụ/URL mới...")
                    if self.bot:
                        self.bot.is_running = False
                    self.is_running = False
                    self.status = "Đang khởi động lại..."
                    time.sleep(0.5)
                else:
                    return False, "Bot đang chạy rồi! Truy cập /stop để dừng tiến trình cũ trước."
            self.is_running = True
            self.status = "Đang khởi động..."
            self.video_url = url
            self.service = service
            self.key = key or self.key
            self.last_sent = 0
            self.total_sent = 0
            self.timer = 0

        self.thread = threading.Thread(target=self._worker, args=(url, service, self.key), daemon=True)
        self.thread.start()
        return True, "Khởi động bot thành công"

    def stop(self):
        with self.lock:
            if not self.is_running:
                return False, "Bot hiện không chạy"
            if self.bot:
                self.bot.is_running = False
            self.is_running = False
            self.status = "Đang dừng..."
            self.timer = 0
        self.add_log("Người dùng yêu cầu dừng bot.")
        return True, "Đã gửi lệnh dừng bot"

    def get_state(self):
        with self.lock:
            return {
                "is_running": self.is_running,
                "status": self.status,
                "timer": self.timer,
                "last_sent": self.last_sent,
                "total_sent": self.total_sent,
                "video_url": self.video_url,
                "service": self.service,
                "key": self.key,
                "logs": self.logs[-40:],
                "uptime": int(time.time() - self.start_time)
            }

manager = BotManager()

# Keep-Alive pinger to prevent Render Free tier from sleeping after 15 minutes of inactivity
def _start_keep_alive():
    external_url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("KEEP_ALIVE_URL")
    if not external_url:
        return

    def _pinger():
        ping_endpoint = external_url.rstrip("/") + "/ping"
        print(f"[*] Bật chế độ chống Sleep Render (Keep-Alive): {ping_endpoint}")
        time.sleep(60)  # Wait 1 minute after server start
        while True:
            try:
                requests.get(ping_endpoint, timeout=10)
            except Exception:
                pass
            time.sleep(600)  # Ping every 10 minutes (Render sleeps at 15m)

    t = threading.Thread(target=_pinger, daemon=True)
    t.start()

_start_keep_alive()

# Auto-start check on module load (supports Gunicorn, Waitress, Werkzeug)
if os.environ.get("AUTO_START", "").lower() in ("true", "1", "yes"):
    _initial_url = os.environ.get("TIKTOK_URL", "").strip()
    if _initial_url:
        print("[*] Phát hiện AUTO_START=true, tự động khởi chạy bot...")
        try:
            manager.start(
                url=_initial_url,
                service=os.environ.get("ZEFOY_SERVICE", "Favorites"),
                key=os.environ.get("ZEFOY_KEY", "")
            )
        except Exception as _e:
            print(f"[!] Lỗi auto-start: {_e}")


# --- Web UI Template ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zefoy Auto Bot Dashboard | Sang Dev</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090d16;
            --card-bg: rgba(16, 24, 40, 0.75);
            --border: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(56, 189, 248, 0.4);
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.25);
            --emerald: #10b981;
            --emerald-glow: rgba(16, 185, 129, 0.25);
            --rose: #f43f5e;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --mono: 'JetBrains Mono', monospace;
            --sans: 'Plus Jakarta Sans', sans-serif;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--bg);
            background-image: 
                radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.12) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.08) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-main);
            font-family: var(--sans);
            min-height: 100vh;
            padding: 24px 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .container {
            width: 100%;
            max-width: 900px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        header {
            text-align: center;
            padding: 10px 0 16px 0;
        }

        .badge-header {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: var(--accent);
            padding: 4px 14px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }

        h1 {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #ffffff 40%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-top: 6px;
        }

        .card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            transition: border-color 0.2s ease;
        }

        .card:hover {
            border-color: var(--border-hover);
        }

        .grid-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 16px;
        }

        .stat-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }

        .stat-label {
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .stat-val {
            font-size: 1.8rem;
            font-weight: 800;
            font-family: var(--mono);
        }

        .stat-val.accent { color: var(--accent); text-shadow: 0 0 15px var(--accent-glow); }
        .stat-val.emerald { color: var(--emerald); text-shadow: 0 0 15px var(--emerald-glow); }
        .stat-val.rose { color: var(--rose); }

        .form-group {
            margin-bottom: 16px;
        }

        label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: #cbd5e1;
        }

        input, select {
            width: 100%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 10px;
            padding: 12px 14px;
            color: var(--text-main);
            font-size: 0.95rem;
            font-family: inherit;
            outline: none;
            transition: all 0.2s;
        }

        input:focus, select:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }

        .btn-group {
            display: flex;
            gap: 12px;
            margin-top: 20px;
        }

        button {
            flex: 1;
            padding: 14px;
            border-radius: 10px;
            border: none;
            font-size: 1rem;
            font-weight: 700;
            font-family: inherit;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn-start {
            background: linear-gradient(135deg, #0284c7, #0ea5e9);
            color: white;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.35);
        }

        .btn-start:hover:not(:disabled) {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(14, 165, 233, 0.5);
        }

        .btn-stop {
            background: rgba(244, 63, 94, 0.15);
            border: 1px solid rgba(244, 63, 94, 0.4);
            color: #fb7185;
        }

        .btn-stop:hover:not(:disabled) {
            background: rgba(244, 63, 94, 0.25);
        }

        button:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        .console {
            background: #040711;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            font-family: var(--mono);
            font-size: 0.85rem;
            height: 250px;
            overflow-y: auto;
            color: #a5f3fc;
            display: flex;
            flex-direction: column;
            gap: 6px;
            scrollbar-width: thin;
        }

        .log-item {
            line-height: 1.4;
            word-break: break-all;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 10px;
        }

        .status-pill.running {
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .status-pill.idle {
            background: rgba(148, 163, 184, 0.12);
            color: #cbd5e1;
            border: 1px solid rgba(148, 163, 184, 0.3);
        }

        .pulsing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: currentColor;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.85); }
            100% { opacity: 1; transform: scale(1); }
        }

        footer {
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-muted);
            padding: 16px 0;
        }

        footer a {
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge-header">⚡ SANG DEV CLOUD BOT</div>
            <h1>Zefoy Automation Dashboard</h1>
            <p class="subtitle">Hệ thống tăng tương tác TikTok tự động 24/7 trên Render</p>
            <div style="margin-top: 12px;">
                <a href="/docs" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); color: var(--accent); padding: 6px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; text-decoration: none;">📖 Xem Tài Liệu API & Hướng Dẫn Chi Tiết</a>
            </div>
        </header>

        <!-- Stats Grid -->
        <div class="card">
            <div class="grid-stats">
                <div class="stat-box">
                    <div class="stat-label">Trạng thái</div>
                    <div id="statStatus" class="stat-val" style="font-size: 1.1rem; line-height: 2.2rem;">Đang tải...</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Thời gian chờ (Timer)</div>
                    <div id="statTimer" class="stat-val accent">00s</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Gửi lần gần nhất</div>
                    <div id="statLast" class="stat-val emerald">+0</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Tổng đã gửi</div>
                    <div id="statTotal" class="stat-val emerald">0</div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; flex-wrap: wrap; gap: 10px;">
                <div id="botBadge" class="status-pill idle">
                    <span class="pulsing-dot"></span>
                    <span id="botStateText">Chưa khởi động</span>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-muted);">
                    Uptime: <span id="statUptime" style="font-family: var(--mono); color: var(--text-main);">0s</span>
                </div>
            </div>
        </div>

        <!-- Controls -->
        <div class="card">
            <div class="form-group">
                <label for="tiktokUrl">🔗 Link Video TikTok (hỗ trợ vt.tiktok.com, vm.tiktok.com, tiktok.com/@user/video/...)</label>
                <input type="text" id="tiktokUrl" placeholder="https://www.tiktok.com/@user/video/..." value="{{ video_url }}">
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div class="form-group">
                    <label for="serviceSelect">🎯 Chọn Dịch Vụ</label>
                    <select id="serviceSelect">
                        <option value="Favorites" {% if service == 'Favorites' %}selected{% endif %}>Favorites (Yêu thích - Khuyên dùng)</option>
                        <option value="Views" {% if service == 'Views' %}selected{% endif %}>Views (Lượt xem)</option>
                        <option value="Hearts" {% if service == 'Hearts' %}selected{% endif %}>Hearts (Tim)</option>
                        <option value="Shares" {% if service == 'Shares' %}selected{% endif %}>Shares (Chia sẻ)</option>
                        <option value="Comments Hearts" {% if service == 'Comments Hearts' %}selected{% endif %}>Comments Hearts (Tim bình luận)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="licenseKey">🔑 License Key Sang Dev</label>
                    <input type="text" id="licenseKey" placeholder="VIP-XXXX-XXXX-XXXX" value="{{ key }}">
                </div>
            </div>

            <div class="btn-group">
                <button id="btnStart" class="btn-start" onclick="startBot()">
                    ▶ Bắt Đầu Chạy
                </button>
                <button id="btnStop" class="btn-stop" onclick="stopBot()" disabled>
                    ⏹ Dừng Lại
                </button>
            </div>
        </div>

        <!-- Real-time Console Log -->
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <label style="margin: 0;">📟 Nhật Ký Hoạt Động (Live Terminal Logs)</label>
                <span style="font-size: 0.75rem; color: var(--text-muted);">Tự động làm mới</span>
            </div>
            <div id="consoleBox" class="console">
                <div class="log-item">[System] Đang kết nối tới máy chủ Render...</div>
            </div>
        </div>

        <footer>
            Bản quyền thuộc về <a href="https://sangdev.online" target="_blank">Sang Dev</a> | Kênh Telegram: <strong>@sangnguyendev</strong>
        </footer>
    </div>

    <script>
        let isRunning = false;

        async function updateStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();

                isRunning = data.is_running;
                
                // Update stats
                document.getElementById('statStatus').innerText = data.status || 'Chờ lệnh';
                document.getElementById('statTimer').innerText = (data.timer > 0 ? data.timer + 's' : '00s');
                document.getElementById('statLast').innerText = '+' + (data.last_sent || 0);
                document.getElementById('statTotal').innerText = data.total_sent || 0;
                
                const upMin = Math.floor(data.uptime / 60);
                const upSec = data.uptime % 60;
                document.getElementById('statUptime').innerText = `${upMin}m ${upSec}s`;

                // Update badge and buttons
                const badge = document.getElementById('botBadge');
                const badgeText = document.getElementById('botStateText');
                const btnStart = document.getElementById('btnStart');
                const btnStop = document.getElementById('btnStop');

                if (isRunning) {
                    badge.className = 'status-pill running';
                    badgeText.innerText = 'Bot đang chạy';
                    btnStart.disabled = true;
                    btnStop.disabled = false;
                } else {
                    badge.className = 'status-pill idle';
                    badgeText.innerText = 'Bot đã dừng';
                    btnStart.disabled = false;
                    btnStop.disabled = true;
                }

                // Update logs
                const consoleBox = document.getElementById('consoleBox');
                if (data.logs && data.logs.length > 0) {
                    consoleBox.innerHTML = data.logs.map(l => `<div class="log-item">${escapeHtml(l)}</div>`).join('');
                    consoleBox.scrollTop = consoleBox.scrollHeight;
                }

            } catch (err) {
                console.error("Lỗi cập nhật:", err);
            }
        }

        async function startBot() {
            const url = document.getElementById('tiktokUrl').value.trim();
            const service = document.getElementById('serviceSelect').value;
            const key = document.getElementById('licenseKey').value.trim();

            if (!url) {
                alert('Vui lòng nhập Link Video TikTok!');
                return;
            }

            document.getElementById('btnStart').disabled = true;

            try {
                const res = await fetch('/api/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, service, key })
                });
                const resData = await res.json();
                if (!resData.success) {
                    alert('Lỗi: ' + resData.message);
                }
                updateStatus();
            } catch (e) {
                alert('Lỗi kết nối tới server: ' + e);
            }
        }

        async function stopBot() {
            document.getElementById('btnStop').disabled = true;
            try {
                const res = await fetch('/api/stop', { method: 'POST' });
                const resData = await res.json();
                updateStatus();
            } catch (e) {
                alert('Lỗi khi dừng bot: ' + e);
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.innerText = text;
            return div.innerHTML;
        }

        // Poll every 3s to optimize server load
        setInterval(updateStatus, 3000);
        updateStatus();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    state = manager.get_state()
    return render_template_string(
        HTML_TEMPLATE,
        video_url=state["video_url"],
        service=state["service"],
        key=state["key"]
    )

@app.route("/docs")
@app.route("/api/docs")
def api_docs():
    docs_file = _ROOT / "docs.html"
    if docs_file.exists():
        return docs_file.read_text(encoding="utf-8")
    return "Tài liệu không tìm thấy", 404

def mask_key(k):
    if not k:
        return ""
    if len(k) <= 8:
        return "****"
    return k[:4] + "****" + k[-4:]

@app.route("/api/status")
@app.route("/status")
def api_status():
    state = manager.get_state()
    # Mask key if caller doesn't provide the matching key in query parameter
    req_key = request.args.get("key", "").strip()
    if req_key != manager.key:
        state["key"] = mask_key(state.get("key", ""))
    state["online_services"] = [s["name"] for s in manager.services_list if s.get("available")]
    return jsonify(state)

@app.route("/api/services")
@app.route("/services")
@app.route("/api/online")
def api_services():
    services = manager.services_list
    online_names = [s["name"] for s in services if s.get("available")]
    return jsonify({
        "success": True,
        "online_count": len(online_names),
        "online": online_names,
        "services": services
    })

@app.route("/run", methods=["GET", "POST"])
@app.route("/api/start", methods=["GET", "POST"])
@app.route("/run/<path:key>/<service>", methods=["GET", "POST"])
@app.route("/run/<service>", methods=["GET", "POST"])
def api_run(key=None, service=None):
    # 1. URL parameter
    url = (request.args.get("url") or "").strip()
    if not url and request.is_json:
        url = ((request.get_json(silent=True) or {}).get("url") or "").strip()
    if not url and request.form:
        url = (request.form.get("url") or "").strip()

    # 2. Service parameter
    req_service = service or request.args.get("service") or request.args.get("type")
    if not req_service and request.is_json:
        req_service = (request.get_json(silent=True) or {}).get("service")
    if not req_service and request.form:
        req_service = request.form.get("service")
    service_name = req_service or manager.service or "Favorites"

    # Normalize service name
    s_low = service_name.lower().replace(" ", "").replace("_", "")
    for s in manager.services_list:
        if s["name"].lower().replace(" ", "").replace("_", "") == s_low:
            service_name = s["name"]
            break

    # 3. Key parameter
    req_key = key or request.args.get("key")
    if not req_key and request.is_json:
        req_key = (request.get_json(silent=True) or {}).get("key")
    if not req_key and request.form:
        req_key = request.form.get("key")
    key_val = req_key or manager.key

    if not url:
        return jsonify({
            "success": False,
            "message": "Vui lòng truyền tham số url! Ví dụ: /run?key=VIP-XXX&service=Favorites&url=https://www.tiktok.com/@user/video/123",
            "usage_examples": [
                f"{request.host_url}run?key={key_val or 'VIP-KEY'}&service={service_name}&url=https://www.tiktok.com/@user/video/...",
                f"{request.host_url}run/{key_val or 'VIP-KEY'}/{service_name}?url=https://www.tiktok.com/@user/video/...",
                f"{request.host_url}run?url=https://www.tiktok.com/@user/video/..."
            ]
        }), 400

    ok, msg = manager.start(url=url, service=service_name, key=key_val)
    return jsonify({
        "success": ok,
        "message": msg,
        "url": url,
        "service": service_name,
        "key": key_val,
        "dashboard": request.host_url,
        "status_url": f"{request.host_url}api/status"
    }), (200 if ok else 400)

@app.route("/stop", methods=["GET", "POST"])
@app.route("/api/stop", methods=["GET", "POST"])
def api_stop():
    ok, msg = manager.stop()
    return jsonify({"success": ok, "message": msg, "status": manager.status})

@app.route("/ping")
@app.route("/health")
def ping():
    return jsonify({
        "status": "ok",
        "bot_running": manager.is_running,
        "uptime": int(time.time() - manager.start_time)
    }), 200

@app.route("/api/<path:user_input>", methods=["GET", "POST"])
def api_key_direct(user_input):
    user_input = user_input.strip()

    # Case 1: https://domain/api/{key}=url format
    if "=" in user_input and ("http://" in user_input or "https://" in user_input or "tiktok.com" in user_input):
        key_part, _, url_part = user_input.partition("=")
        key_val = key_part.strip()
        url = url_part.strip()
    else:
        key_val = user_input
        url = (request.args.get("url") or "").strip()

    if not url and request.is_json:
        url = ((request.get_json(silent=True) or {}).get("url") or "").strip()
    if not url and request.form:
        url = (request.form.get("url") or "").strip()

    req_service = request.args.get("service") or request.args.get("type")
    if not req_service and request.is_json:
        req_service = (request.get_json(silent=True) or {}).get("service")
    service_name = req_service or manager.service or "Favorites"

    for s in manager.services_list:
        if s["name"].lower().replace(" ", "").replace("_", "") == service_name.lower().replace(" ", "").replace("_", ""):
            service_name = s["name"]
            break

    # If URL is provided -> RUN BOT
    if url:
        ok, msg = manager.start(url=url, service=service_name, key=key_val)
        return jsonify({
            "success": ok,
            "message": msg,
            "key": mask_key(key_val),
            "service": service_name,
            "url": url,
            "status_url": f"{request.host_url}api/{key_val}"
        }), (200 if ok else 400)

    # If NO URL is provided -> RETURN STATUS FOR THIS KEY
    state = manager.get_state()
    is_owner = (key_val.lower() == (manager.key or "").lower())
    if not is_owner:
        return jsonify({
            "success": False,
            "message": "Key không khớp với bot đang chạy trên server!",
            "key_provided": mask_key(key_val)
        }), 403

    return jsonify({
        "success": True,
        "key": mask_key(key_val),
        "is_running": state["is_running"],
        "video_url": state["video_url"],
        "service": state["service"],
        "status": state["status"],
        "timer": state["timer"],
        "last_sent": state["last_sent"],
        "total_sent": state["total_sent"],
        "online_services": [s["name"] for s in manager.services_list if s.get("available")],
        "logs": state["logs"][-15:]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    # Auto switch to Gunicorn on Linux/Render even if user set Start Command as "python app.py"
    if sys.platform != "win32" and os.environ.get("RUN_WITH_WERKZEUG", "0") != "1":
        try:
            import gunicorn
            cmd = [
                "gunicorn",
                "--workers", "1",
                "--threads", "4",
                "--timeout", "120",
                "--keep-alive", "5",
                "--bind", f"0.0.0.0:{port}",
                "app:app"
            ]
            print(f"[*] Sang Dev Bot: Chuyển sang WSGI Gunicorn sản xuất ({port})...")
            os.execvp("gunicorn", cmd)
        except Exception as e:
            print(f"[!] Gunicorn fallback: {e}")

    print(f"[*] Sang Dev Zefoy Web Server đang khởi động tại cổng {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
