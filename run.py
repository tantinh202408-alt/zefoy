import os
try:
    import requests,colorama,prettytable
except:
    os.system("pip install requests")
    os.system("pip install colorama")
    os.system("pip install prettytable")
try:
    import bs4              
except Exception:
    os.system("pip install beautifulsoup4")
try:
    import Crypto              
except Exception:
    os.system("pip install pycryptodome")

import threading, requests, ctypes, random, json, time, base64, sys, re, shutil
from prettytable import PrettyTable
import random
from time import strftime
from colorama import init, Fore
from urllib.parse import urlparse, unquote, quote
from string import ascii_letters, digits

from pathlib import Path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from zefoy.captcha import ZefoyCaptcha, DEFAULT_USER_AGENT
from zefoy.fingerprint import apply_session_guard_cookies, build_captcha_encoded
from zefoy.newocr import NewOcrWeb
from zefoy.submit import is_captcha_page
from zefoy.ocr import solve_image
from bs4 import BeautifulSoup
import unicodedata


# ── Setup Terminal, UTF-8 and Size ──────────────────────────────────────────
def setup_terminal():
    if sys.platform.startswith('win'):
        os.system('chcp 65001 > nul 2>&1')
        os.system('mode con: cols=80 lines=42 > nul 2>&1')
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
        try:
            ctypes.windll.kernel32.SetConsoleTitleW("ZEFOY BOT - SANG DEV")
        except Exception:
            pass
    init(autoreset=True)

setup_terminal()

# ── Developer Information ───────────────────────────────────────────────────
DEV_NAME = "sang dev"
DEV_TIKTOK = "@sangnguyendev"
DEV_YOUTUBE = "@sangdevshop"
DEV_TOOL = "AUTO TIKTOK ZEFOY"
DEV_VERSION = "2026 VIP Edition"

# ── License Key Verification ────────────────────────────────────────────────
API_CHECK_KEY = "https://sangdev.online/api/key/check"
KEY_FILE = "key.txt"

def get_box_width():
    term_w = shutil.get_terminal_size((70, 24)).columns
    return max(44, min(term_w - 2, 70))

def show_banner(key_status=None, extra_lines=None):
    os.system("cls" if os.name == "nt" else "clear")
    box_w = get_box_width()
    inner_w = box_w - 2

    logo_wide = [
        "███████╗ █████╗ ███╗   ██╗ ██████╗     ██████╗ ███████╗██╗   ██╗",
        "██╔════╝██╔══██╗████╗  ██║██╔════╝     ██╔══██╗██╔════╝██║   ██║",
        "███████╗███████║██╔██╗ ██║██║  ███╗    ██║  ██║█████╗  ██║   ██║",
        "╚════██║██╔══██║██║╚██╗██║██║   ██║    ██║  ██║██╔══╝  ╚██╗ ██╔╝",
        "███████║██║  ██║██║ ╚████║╚██████╔╝    ██████╔╝███████╗ ╚████╔╝ ",
        "╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝     ╚═════╝ ╚══════╝  ╚═══╝  ",
    ]

    logo_compact = [
        r"  ___ ___ _  _  ___   ___  _____   __ ",
        r" / __/   \ \| |/ __| |   \| __\ \ / / ",
        r" \__ \ - | .` | (_ | | |) | _| \ V /  ",
        r" |___/_|_|_|\_|\___| |___/|___| \_/   ",
    ]

    colors = [
        "\033[38;5;51m",  # Bright Cyan
        "\033[38;5;45m",  # Sky Blue
        "\033[38;5;39m",  # Deep Sky Blue
        "\033[38;5;33m",  # Blue
        "\033[38;5;75m",  # Steel Blue
        "\033[38;5;117m", # Light Cyan
    ]
    c_frame = "\033[38;5;39m"
    c_white = "\033[1;37m"
    c_green = "\033[1;32m"
    c_yellow = "\033[1;33m"
    c_cyan = "\033[1;36m"
    c_red = "\033[1;31m"
    c_magenta = "\033[1;35m"
    c_reset = "\033[0m"

    print(f"\n{c_frame}  ╔" + "═" * inner_w + "╗")
    if inner_w >= 64:
        for i, line in enumerate(logo_wide):
            c = colors[i % len(colors)]
            print(f"  {c_frame}║{c}" + line.center(inner_w) + f"{c_frame}║")
    else:
        for i, line in enumerate(logo_compact):
            c = colors[i % len(colors)]
            print(f"  {c_frame}║{c}" + line.center(inner_w) + f"{c_frame}║")

    print(f"  {c_frame}╠" + "═" * inner_w + "╣")
    title_str = "TOOL AUTO TIKTOK ZEFOY · 2026"
    print(f"  {c_frame}║{c_yellow}" + title_str.center(inner_w) + f"{c_frame}║")
    print(f"  {c_frame}╠" + "═" * inner_w + "╣")
    
    val_w = max(10, inner_w - 18)
    print(f"  {c_frame}║  {c_white}[+] Developer :{c_green} " + f"{DEV_NAME}"[:val_w].ljust(val_w) + f"{c_frame}║")
    print(f"  {c_frame}║  {c_white}[+] TikTok    :{c_cyan} " + f"{DEV_TIKTOK}"[:val_w].ljust(val_w) + f"{c_frame}║")
    print(f"  {c_frame}║  {c_white}[+] YouTube   :{c_red} " + f"{DEV_YOUTUBE}"[:val_w].ljust(val_w) + f"{c_frame}║")
    
    if key_status == 'vip':
        status_txt = "KEY VIP (Cam on ban da ung ho!)"
        print(f"  {c_frame}║  {c_white}[+] Ban quyen :{c_magenta} " + f"{status_txt}"[:val_w].ljust(val_w) + f"{c_frame}║")
    elif key_status == 'free':
        status_txt = "KEY FREE (Che do dung thu)"
        print(f"  {c_frame}║  {c_white}[+] Ban quyen :{c_cyan} " + f"{status_txt}"[:val_w].ljust(val_w) + f"{c_frame}║")
    else:
        status_txt = "Dang cho xac thuc key..."
        print(f"  {c_frame}║  {c_white}[+] Ban quyen :{c_yellow} " + f"{status_txt}"[:val_w].ljust(val_w) + f"{c_frame}║")

    if extra_lines:
        print(f"  {c_frame}╠" + "═" * inner_w + "╣")
        for label, val, val_c in extra_lines:
            vw = max(10, inner_w - len(label) - 6)
            print(f"  {c_frame}║  {c_white}{label}:{val_c} " + f"{val}"[:vw].ljust(vw) + f"{c_frame}║")

    print(f"  {c_frame}╚" + "═" * inner_w + f"╝{c_reset}\n")

def check_key_api(key: str):
    try:
        url = f"{API_CHECK_KEY}?key={quote(key.strip())}"
        res = requests.get(url, headers={"user-agent": DEFAULT_USER_AGENT}, timeout=15)
        if res.status_code == 200:
            try:
                data = res.json()
                return True, data
            except Exception:
                return False, {"message": "Dữ liệu máy chủ trả về không hợp lệ."}
        else:
            return False, {"message": f"Lỗi phản hồi HTTP {res.status_code}"}
    except Exception as e:
        return False, {"message": f"Không thể kết nối máy chủ xác thực: {e}"}

def is_vip_key(key: str, data: dict) -> bool:
    if (
        data.get("is_vip") is True
        or data.get("vip") is True
        or "vip" in str(data.get("type", "")).lower()
        or "vip" in str(data.get("plan", "")).lower()
        or "vip" in str(data.get("tier", "")).lower()
        or "vip" in str(data.get("role", "")).lower()
        or "vip" in key.lower()
    ):
        return True
    return False

def verify_license_key(key=None, headless=False):
    if not headless:
        show_banner(None)
    c_frame = "\033[38;5;39m"
    c_white = "\033[1;37m"
    c_green = "\033[1;32m"
    c_yellow = "\033[1;33m"
    c_cyan = "\033[1;36m"
    c_red = "\033[1;31m"
    c_reset = "\033[0m"

    # 1. Direct parameter
    if key:
        ok, data = check_key_api(key)
        if ok and isinstance(data, dict) and (data.get("valid") is True or data.get("status") in (True, "success") or (data.get("success") is True and data.get("valid") is not False and data.get("reason") is None)):
            vip = is_vip_key(key, data)
            return key, vip
        elif headless:
            return key, False

    # 2. Environment variable
    env_key = os.environ.get("ZEFOY_KEY", "").strip()
    if env_key:
        ok, data = check_key_api(env_key)
        if ok and isinstance(data, dict) and (data.get("valid") is True or data.get("status") in (True, "success") or (data.get("success") is True and data.get("valid") is not False and data.get("reason") is None)):
            vip = is_vip_key(env_key, data)
            return env_key, vip

    saved_key = ""
    if os.path.exists(KEY_FILE):
        try:
            saved_key = open(KEY_FILE, "r", encoding="utf-8").read().strip()
        except Exception:
            saved_key = ""

    if saved_key:
        if not headless:
            print(f"  {c_cyan}[*] {c_white}Đang tự động kiểm tra key đã lưu: {c_yellow}{saved_key}{c_reset}")
        ok, data = check_key_api(saved_key)
        is_valid = False
        if ok and isinstance(data, dict):
            if data.get("valid") is True or data.get("status") in (True, "success") or (data.get("success") is True and data.get("valid") is not False and data.get("reason") is None):
                is_valid = True

        if is_valid:
            vip = is_vip_key(saved_key, data)
            return saved_key, vip
        else:
            err_msg = data.get("message") if isinstance(data, dict) else "Key không hợp lệ"
            if not headless:
                print(f"  {c_red}[!] Key đã lưu không hợp lệ ({err_msg}). Vui lòng nhập key mới!{c_reset}\n")

    if headless:
        return "FREE-MEMBER", False

    while True:
        print(f"  {c_frame}┌──[ {c_white}NHẬP KEY BẢN QUYỀN SANG DEV {c_frame}]")
        user_key = input(f"  {c_frame}└──▶ {c_yellow}").strip()
        if not user_key:
            print(f"  {c_red}[!] Vui lòng không để trống mã Key!{c_reset}\n")
            continue

        print(f"  {c_cyan}[*] {c_white}Đang xác thực Key với hệ thống sangdev.online...{c_reset}")
        ok, data = check_key_api(user_key)
        is_valid = False
        if ok and isinstance(data, dict):
            if data.get("valid") is True or data.get("status") in (True, "success") or (data.get("success") is True and data.get("valid") is not False and data.get("reason") is None):
                is_valid = True

        if is_valid:
            try:
                open(KEY_FILE, "w", encoding="utf-8").write(user_key)
            except Exception:
                pass
            vip = is_vip_key(user_key, data)
            return user_key, vip
        else:
            err_msg = (data.get("message") if isinstance(data, dict) else None) or "Mã Key không tồn tại trên hệ thống hoặc đã hết hạn."
            print(f"  {c_red}[✖] XÁC THỰC THẤT BẠI: {err_msg}{c_reset}")
            print(f"  {c_white}► Lấy hoặc mua key tại: {c_cyan}https://sangdev.online{c_reset}\n")
            time.sleep(1)

class Zefoy:
    def __init__(self, url=None, service=None, license_key=None, headless=False, on_status=None, on_timer=None, on_log=None):
        self.headless = headless
        self.on_status = on_status
        self.on_timer = on_timer
        self.on_log = on_log
        self.is_running = True
        self.current_status = "Đang khởi tạo..."

        self.license_key, self.is_vip = verify_license_key(key=license_key, headless=headless)
        self.key_status = "vip" if self.is_vip else "free"
        
        if not self.headless:
            # Clear screen and re-render banner with key status
            show_banner(self.key_status)
            if self.is_vip:
                print("  \033[1;35m[★] CẢM ƠN BẠN ĐÃ MUA & ỦNG HỘ KEY VIP CỦA SANG DEV!\033[0m")
                print("  \033[1;32m[+] Kích hoạt thành công toàn bộ đặc quyền VIP!\033[0m\n")
            else:
                print("  \033[1;32m[+] Kích hoạt thành công chế độ Free Member (Dùng thử)!\033[0m\n")

        self.base_url = 'https://zefoy.com/'
        self.headers = {'user-agent': DEFAULT_USER_AGENT}
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': DEFAULT_USER_AGENT,
            'accept-language': 'en-US,en;q=0.9',
        })
        self.captcha_1 = None
        self.captcha_ = {}
        self.service = service or 'Favorites'
        self.video_key = None
        self.services = {}
        self.services_ids = {}
        self.services_inputs = {}
        self.services_status = {}
        self.url = url or os.environ.get("TIKTOK_URL", "")
        self.text = f'Tool Zefoy | dev: {DEV_NAME}'
        self.last_sent = 0
        self.total_sent = 0
        
        if not self.url and not self.headless:
            print(f"  \033[1;36m┌──[ \033[1;37mNHẬP LINK VIDEO TIKTOK \033[1;36m]")
            url1 = input(f"  \033[1;36m└──▶ \033[1;33m").strip()
            print()
            self.url = url1
        
        if self.url and ('vm.tiktok.com' in self.url or 'vt.tiktok.com' in self.url):
            self.get_video_id(self.url)


    def render_dashboard(self, status="Đang xử lý..."):
        self.current_status = status
        if self.on_status:
            try:
                self.on_status(status, self.last_sent, self.total_sent)
            except Exception:
                pass
        if self.on_log:
            try:
                self.on_log(status)
            except Exception:
                pass
        if not self.headless:
            show_banner(
                self.key_status,
                extra_lines=[
                    ("[+] Video URL ", str(self.url), Fore.YELLOW),
                    ("[+] Dịch vụ   ", str(self.service), Fore.GREEN),
                    ("[+] Đã gửi    ", f"+{self.last_sent} (Tổng: {self.total_sent})", Fore.CYAN),
                    ("[+] Trạng thái", str(status), Fore.YELLOW),
                ]
            )

    def get_captcha(self):
\
\
\
           
        if os.path.exists('session'):
            try:
                sid = open('session', encoding='utf-8').read().strip()
                if sid:
                    self.session.cookies.set("PHPSESSID", sid, domain='zefoy.com')
            except Exception:
                pass

        request = self.session.get(self.base_url, headers=self.headers, timeout=30)

                                               
        if not is_captcha_page(request.text):
            self._extract_video_key(request.text)
            return True

                                                                   
        if 'Enter Video URL' in request.text:
            self._extract_video_key(request.text)
            return True

        try:
                                       
            apply_session_guard_cookies(self.session)
            zc = ZefoyCaptcha(
                user_agent=self.headers['user-agent'],
                session=self.session,
            )
                                                   
            captcha = zc.get(refresh_session=False)
            captcha.save('captcha.png')

                                                         
            self.captcha_1 = 'captchalogin'
            self.captcha_ = {
                'captchalogin': '',
                'captcha_encoded': build_captcha_encoded(self.headers['user-agent']),
            }
            print('Solving captcha..')
            return False
        except Exception as e:
            print(f"\033[1;33mCannot solve captcha: {e}")
            time.sleep(2)
            return self.get_captcha()

    def _extract_video_key(self, html):
                                                                       
        try:
            if 'placeholder="Enter Video URL"' in html:
                self.video_key = html.split('" placeholder="Enter Video URL"')[0].split('name="')[-1]
                return
        except Exception:
            pass
                                                   
        m = re.search(
            r'<form[^>]+action="([^"]+)"[^>]*>[\s\S]*?<input[^>]+name="([^"]+)"',
            html,
            re.I,
        )
        if m:
            self.video_key = m.group(2)
            return
        m = re.search(r'name="([0-9a-f]{8,})"', html, re.I)
        if m:
            self.video_key = m.group(1)

    def send_captcha(self, new_session = False, retries = 0):
        if retries >= 8:
            msg = 'Đã thử giải Captcha 8 lần, tạm nghỉ 10s để giải phóng tài nguyên...'
            if self.on_log:
                self.on_log(msg)
            time.sleep(10)
            retries = 0

        if new_session:
            self.session = requests.Session()
            self.session.headers.update({
                'user-agent': self.headers['user-agent'],
                'accept-language': 'en-US,en;q=0.9',
            })
            if os.path.exists('session'):
                try:
                    os.remove('session')
                except Exception:
                    pass
            time.sleep(1)

        if self.get_captcha():
            msg = 'Đang kết nối session có sẵn...'
            if self.on_log:
                self.on_log(msg)
            if not self.headless:
                print(f'  \033[1;35m[*] \033[1;37m{msg}\033[0m')
            return (True, 'The session already exists')

        if self.on_log:
            self.on_log("Đang giải mã Captcha...")
        captcha_solve = self.solve_captcha('captcha.png')[1]
        captcha_solve = re.sub(r'[^a-zA-Z]', '', captcha_solve or '').lower()
        if not captcha_solve:
            msg = 'OCR rỗng, đang tải lại Captcha mới...'
            if self.on_log:
                self.on_log(msg)
            if not self.headless:
                print(f'  \033[1;31m[!] {msg}\033[0m')
            time.sleep(1.5)
            return self.send_captcha(new_session=True, retries=retries + 1)

        if self.on_log:
            self.on_log(f"Đã giải Captcha: {captcha_solve}, đang gửi xác thực...")

        encoded = self.captcha_.get('captcha_encoded') or build_captcha_encoded(
            self.headers['user-agent']
        )
        apply_session_guard_cookies(self.session)

        request = self.session.post(
            self.base_url,
            headers={
                'user-agent': self.headers['user-agent'],
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'x-requested-with': 'XMLHttpRequest',
                'origin': 'https://zefoy.com',
                'referer': 'https://zefoy.com/',
                'accept': '*/*',
            },
            data={
                'captchalogin': captcha_solve,
                'captcha_encoded': encoded,
            },
            timeout=30,
            allow_redirects=False,
        )
        xhr_body = (request.text or '').strip()

        ok = request.status_code == 200 and xhr_body.lower() == 'success'
        if not ok:
            if not is_captcha_page(xhr_body) and len(xhr_body) > 1000:
                ok = True

        if ok:
            sid = self.session.cookies.get('PHPSESSID')
            if sid:
                try:
                    open('session', 'w', encoding='utf-8').write(sid)
                except Exception:
                    pass
            msg = f"Giải Captcha thành công: {captcha_solve}"
            if self.on_log:
                self.on_log(msg)
            if not self.headless:
                print(f'  \033[1;32m[✓] \033[1;37m{msg}\033[0m')
            panel = self.session.get(self.base_url, headers=self.headers, timeout=30)
            self._extract_video_key(panel.text)
            return (True, captcha_solve)

        msg = f"Captcha không khớp ({captcha_solve}), đang thử lại..."
        if self.on_log:
            self.on_log(msg)
        time.sleep(1.5)
        return self.send_captcha(new_session=True, retries=retries + 1)

    def solve_captcha(self, path_to_file = None, b64 = None, delete_tag = ['\n','\r']):
        if path_to_file:
            task = path_to_file
            with open(task, 'rb') as f:
                img = f.read()
        else:
            img = base64.b64decode(b64)
            open('temp.png', 'wb').write(img)
            task = 'temp.png'

        solved_text = ""
        # 1. Local RapidOCR first (super fast, <0.1s)
        try:
            solved_text = solve_image(img, use_fallbacks=False)
        except Exception:
            solved_text = ""

        # 2. Fallback to NewOCR Web if local OCR is empty or short
        if not solved_text or len(solved_text) < 3:
            try:
                result = NewOcrWeb().ocr(img)
                solved_text = result.text or ''
            except Exception as e:
                print(f'  \033[1;33m[!] NewOCR lỗi: {e}\033[0m')
                solved_text = ''

        for x in delete_tag:
            solved_text = solved_text.replace(x, '')
        try:
            solved_text = unicodedata.normalize('NFKC', solved_text)
        except Exception:
            pass
        solved_text = re.sub(r'[^a-zA-Z]', '', solved_text).lower()
        return (True, solved_text)

    def _decode_response(self, body):
        if not body:
            return ''
        text = body.strip()
        if text.lower() == 'success':
            return 'success'
        rev = text[::-1]
        for candidate in (unquote(rev), rev, unquote(text), text):
            try:
                dec = base64.b64decode(candidate).decode('utf-8', errors='replace')
                if dec and ('<' in dec or 'Please wait' in dec or 'successfully' in dec.lower()):
                    return dec
            except Exception:
                continue
        return text

    def _parse_timer(self, html):
        if not html:
            return None
        m = re.search(r'remainingTimelogin\s*=\s*(-?\d+)', html)
        if m:
            v = int(m.group(1))
            return v if v > 0 else None
        m = re.search(r'var\s+ltm\s*=\s*(-?\d+)', html)
        if m:
            v = int(m.group(1))
            return v if v > 0 else None
        m = re.search(r'ltm\s*=\s*(-?\d+)', html)
        if m:
            v = int(m.group(1))
            return v if v > 0 else None
        m = re.search(r'(\d+)\s*minute(?:s|\(s\))?\s*(\d+)\s*second', html, re.I)
        if m:
            v = int(m.group(1)) * 60 + int(m.group(2))
            return v if v > 0 else None
        m = re.search(r'(\d+)\s*minute(?:s|\(s\))?', html, re.I)
        if m and ('wait' in html.lower() or 'before' in html.lower()):
            v = int(m.group(1)) * 60
            m_sec = re.search(r'(\d+)\s*second', html, re.I)
            if m_sec:
                v += int(m_sec.group(1))
            return v if v > 0 else None
        m = re.search(r'Please wait\s+(\d+)\s+seconds?', html, re.I)
        if m:
            v = int(m.group(1))
            return v if v > 0 else None
        m = re.search(r'(\d+)\s*seconds?(?:\(s\))?\s*(?:before|for|to)', html, re.I)
        if m:
            v = int(m.group(1))
            return v if v > 0 else None
        m = re.search(r'(\d+)\s*seconds?\s*(?:for your next|before trying)', html, re.I)
        if m:
            v = int(m.group(1))
            return v if v > 0 else None
        return None

    def _wait_timer(self, seconds):
        if seconds is None or seconds <= 0:
            return
        if seconds >= 5000:
            if self.on_log:
                self.on_log('[!] IP BLOCKED / Thời gian chờ quá lớn')
            if not self.headless:
                print('  \033[31m[!] IP BLOCKED / Thời gian chờ quá lớn\033[0m')
            time.sleep(5)
            return
        # Pad +2 seconds to ensure server cooldown is 100% finished
        end = time.time() + seconds + 2
        try:
            while time.time() < end and getattr(self, 'is_running', True):
                left = max(0, int(end - time.time()))
                if self.on_timer:
                    try:
                        self.on_timer(left)
                    except Exception:
                        pass
                if not self.headless:
                    print(f'  \033[1;35m[⏳ Cooldown]\033[1;37m Chờ server mở lại: \033[1;32m{left:02d}\033[1;37m giây...   \033[0m', end='\r', flush=True)
                time.sleep(1)
            if self.on_timer:
                try:
                    self.on_timer(0)
                except Exception:
                    pass
        except KeyboardInterrupt:
            if not self.headless:
                print('\n  \033[1;33m[!] Đã dừng tiến trình.\033[0m')
            raise
        if not self.headless:
            print(' ' * 60, end='\r')

    def _post_service(self, fields):
        action = self.services_ids.get(self.service)
        if not action:
            self.get_status_services()
            action = self.services_ids.get(self.service)
        if not action:
            raise RuntimeError('Service action not found: %s' % self.service)

        url = action if str(action).startswith('http') else f'{self.base_url}{action.lstrip("/")}'
        apply_session_guard_cookies(self.session)

        request = self.session.post(
            url,
            headers={
                'user-agent': self.headers['user-agent'],
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'x-requested-with': 'XMLHttpRequest',
                'origin': 'https://zefoy.com',
                'referer': 'https://zefoy.com/',
                'accept': '*/*',
            },
            data=fields,
            timeout=30,
        )
        return self._decode_response(request.text)

    def _extract_confirm_fields(self, html):
        if not html:
            return None
        try:
            soup = BeautifulSoup(html, 'html.parser')
            form = soup.find('form')
            if form:
                fields = {}
                for inp in form.find_all('input'):
                    name = inp.get('name')
                    if name and name.lower() not in ('ocr', 'preview'):
                        fields[name] = inp.get('value', '')
                
                # Check for select elements (like select_lmt: 25, 50, 75, 100)
                for sel in form.find_all('select'):
                    name = sel.get('name')
                    if name:
                        max_val = None
                        max_num = -1
                        for opt in sel.find_all('option'):
                            v = opt.get('value', '').strip()
                            if not v or opt.has_attr('disabled'):
                                continue
                            if v.isdigit():
                                num = int(v)
                                if num > max_num:
                                    max_num = num
                                    max_val = v
                            elif not max_val:
                                max_val = v
                        if max_val:
                            fields[name] = max_val

                if fields:
                    return fields
        except Exception:
            pass

        m = re.search(
            r'<input[^>]+type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']+)["\']',
            html,
            re.I,
        )
        if m:
            fields = {m.group(1): m.group(2)}
            m_lmt = re.search(r'name=["\'](select_lmt)["\'][\s\S]*?value=["\'](\d+)["\']', html, re.I)
            if m_lmt:
                fields[m_lmt.group(1)] = m_lmt.group(2)
            return fields

        m = re.search(
            r'<input[^>]+name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']+)["\']',
            html,
            re.I,
        )
        if m:
            name, value = m.group(1), m.group(2)
            if name.lower() not in ('submit', 'ocr', 'preview'):
                return {name: value}

        return None

    def get_status_services(self):
        request = self.session.get(self.base_url, headers=self.headers, timeout=30).text
        self.services = {}
        self.services_ids = {}
        self.services_inputs = getattr(self, 'services_inputs', {})
        self.services_status = {}

        for x in re.findall(r'<h5 class="card-title">.+</h5>\n.+\n.+', request):
            try:
                self.services[x.split('<h5 class="card-title">')[1].split('<')[0].strip()] = x.split('d-sm-inline-block">')[1].split('</small>')[0].strip()
            except Exception:
                pass
        for x in re.findall(r'<h5 class="card-title mb-3">.+</h5>\n<form action=".+">', request):
            try:
                self.services_ids[x.split('title mb-3">')[1].split('<')[0].strip()] = x.split('<form action="')[1].split('">')[0].strip()
            except Exception:
                pass
        for x in re.findall(r'<h5 class="card-title">.+</h5>\n.+<button .+', request):
            try:
                self.services_status[x.split('<h5 class="card-title">')[1].split('<')[0].strip()] = False if 'disabled class' in x else True
            except Exception:
                pass

        try:
            from zefoy.services import parse_services
            for svc in parse_services(request):
                self.services[svc.title] = svc.raw_status or svc.status
                self.services_status[svc.title] = bool(svc.available)
                if svc.action:
                    self.services_ids[svc.title] = svc.action
                if svc.input_name:
                    self.services_inputs[svc.title] = svc.input_name
                    self.video_key = svc.input_name
        except Exception:
            pass

        if len(self.services_ids) <= 1:
            for m in re.finditer(
                r'<form action="([^"]+)">[\s\S]*?name="([^"]+)"[^>]*placeholder="Enter Video',
                request,
                re.I,
            ):
                prev = request[max(0, m.start() - 400):m.start()]
                tm = re.findall(r'<h5[^>]*>([^<]+)</h5>', prev)
                title = tm[-1].strip() if tm else m.group(1)[:12]
                self.services_ids[title] = m.group(1)
                self.services_inputs[title] = m.group(2)
                self.video_key = m.group(2)
                if title not in self.services:
                    self.services[title] = 'unknown'
                    self.services_status[title] = True

        self._extract_video_key(request)
        return (self.services, self.services_status)


    def get_table(self, i = 1):
        show_banner(getattr(self, 'key_status', 'vip' if getattr(self, 'is_vip', False) else 'free'))
        print(f"  \033[1;36m[+] Video URL: \033[1;32m{self.url}\033[0m\n")
        table = PrettyTable(field_names=["STT", "DICH VU (SERVICE)", "TRANG THAI (STATUS)"])
        table.align["STT"] = "c"
        table.align["DICH VU (SERVICE)"] = "l"
        table.align["TRANG THAI (STATUS)"] = "c"
        while True:
            if len(self.get_status_services()[0]) > 1:
                break
            else:
                print('  \033[1;33m[*] Đang tải danh sách dịch vụ, vui lòng chờ...\033[0m')
                self.send_captcha()
                time.sleep(2)
        for service in self.services:
            status = self.services[service]
            online = ('ago updated' in status) or ('Online' in status) or (
                self.services_status.get(service) is True and 'soon' not in status.lower()
            )
            color = Fore.GREEN if online else Fore.RED
            status_text = f"{color}[ONLINE] {status}{Fore.RESET}" if online else f"{color}[OFFLINE] {status}{Fore.RESET}"
            table.add_row([f"{Fore.CYAN}{i}{Fore.RESET}", f"{Fore.WHITE}{service}{Fore.RESET}", status_text])
            i += 1
        online_n = len([x for x in self.services_status if self.services_status[x]])
        table.title = f"{Fore.CYAN}ZEFOY SERVICES | ONLINE: {Fore.GREEN}{online_n}{Fore.CYAN} | DEV: {Fore.YELLOW}{DEV_NAME.upper()}{Fore.RESET}"
        print(table)

    def find_video(self):
        if self.service is None:
            return (False, "You didn't choose the service")

        self.render_dashboard("Đang kiểm tra dịch vụ và tìm video...")

        while True:
            if self.service not in self.services_ids:
                self.render_dashboard("Đang lấy danh sách dịch vụ...")
                self.get_status_services()
                time.sleep(0.5)
                if self.service not in self.services_ids:
                    return (False, "Service action not found")

            search_key = getattr(self, 'services_inputs', {}).get(self.service) or self.video_key
            if not search_key:
                self.get_status_services()
                search_key = getattr(self, 'services_inputs', {}).get(self.service) or self.video_key
            if not search_key:
                return (False, "video_key not found")

            try:
                self.render_dashboard("Đang gửi yêu cầu tìm video...")
                html = self._post_service({search_key: self.url})
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.render_dashboard(f"Lỗi kết nối ({e}), đang thử lại...")
                time.sleep(2)
                continue

            if 'Session expired' in html or is_captcha_page(html):
                self.render_dashboard("Phiên hết hạn, đang giải Captcha mới...")
                self.send_captcha(new_session=True)
                continue

            if 'service is currently not working' in html.lower():
                self.render_dashboard(f"Dịch vụ {self.service} đang bảo trì!")
                return (False, 'The service is currently unavailable, please try again later.')

            if 'Too many requests' in html:
                self.render_dashboard("Quá nhiều yêu cầu, tạm nghỉ 4s...")
                time.sleep(4)
                continue

            wait = self._parse_timer(html)
            if wait is not None and wait > 0:
                self.render_dashboard(f"Đang chờ cooldown {wait}s...")
                self._wait_timer(wait)
                continue

            if (
                'onsubmit="fcde' in html
                or "onsubmit='fcde" in html
                or 'onsubmit="showHideElements' in html
                or 'wbutton' in html
                or re.search(r'type=["\']hidden["\'][^>]*value=["\']\d+', html, re.I)
                or re.search(r'value=["\']\d{10,}["\']', html)
                or '<form' in html
            ):
                fields = self._extract_confirm_fields(html)
                if fields:
                    self.video_info = fields
                    self.render_dashboard("Tìm thấy video thành công!")
                    return (True, fields)

            if 'An error occurred' in html and not re.search(r'value=["\']\d+', html):
                return (False, 'invalid video')

            if 'Checking Timer...' in html:
                wait = self._parse_timer(html) or 3
                self.render_dashboard(f"Đang đồng bộ server {wait}s...")
                self._wait_timer(wait)
                continue

            time.sleep(1)

    def _parse_sent_amount(self, html):
        if not html:
            return None, None, None
        m = re.search(
            r'Successfully\s+(\d+)\s*([a-zA-Z ]*?)\s*sent\.?',
            html,
            re.I,
        )
        if m:
            amount = int(m.group(1))
            kind = (m.group(2) or '').strip().lower() or 'items'
            msg = re.sub(r'\s+', ' ', m.group(0)).strip()
            return amount, kind, msg

        m = re.search(r'(\d+)\s*(views?|hearts?|likes?|shares?|followers?|favorites?)\s*sent', html, re.I)
        if m:
            return int(m.group(1)), m.group(2).lower(), m.group(0).strip()
        m = re.search(r'sent\s+(\d+)\s*(views?|hearts?|likes?)', html, re.I)
        if m:
            return int(m.group(1)), m.group(2).lower(), m.group(0).strip()

        # Handle messages without explicit numbers (e.g. "Favorites successfully sent.")
        m = re.search(r'(views?|hearts?|likes?|shares?|followers?|favorites?)\s+successfully\s+sent', html, re.I)
        if m:
            kind = m.group(1).lower()
            amt = 100
            if isinstance(getattr(self, 'video_info', None), dict):
                try:
                    amt = int(self.video_info.get('select_lmt', 100) or 100)
                except Exception:
                    amt = 100
            return amt, kind, f"{kind.capitalize()} successfully sent (+{amt})"

        if 'successfully sent' in html.lower():
            amt = 100
            if isinstance(getattr(self, 'video_info', None), dict):
                try:
                    amt = int(self.video_info.get('select_lmt', 100) or 100)
                except Exception:
                    amt = 100
            return amt, str(self.service).lower(), f"Tăng thành công (+{amt})"

        return None, None, None

    def use_service(self):
        found = self.find_video()
        if not found or found[0] is False:
            return False
        if not getattr(self, 'video_info', None):
            return False

        if isinstance(self.video_info, dict):
            post_payload = self.video_info
        elif isinstance(self.video_info, (list, tuple)) and len(self.video_info) >= 2:
            post_payload = {self.video_info[0]: self.video_info[1]}
        else:
            return False

        try:
            self.render_dashboard(f"Đang gửi lệnh tăng {self.service}...")
            res = self._post_service(post_payload)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            time.sleep(1)
            return ""

        if 'Session expired' in res or is_captcha_page(res):
            self.render_dashboard("Session hết hạn, đang tạo phiên mới...")
            self.send_captcha(new_session=True)
            return ""
        if 'Too many requests' in res:
            self.render_dashboard("Gửi quá nhanh, tạm nghỉ 4s...")
            time.sleep(4)
            return ""
        if 'service is currently not working' in res.lower():
            return '\033[31mThe service is currently unavailable, please try again later'

        amount, kind, sent_msg = self._parse_sent_amount(res)
        if amount is not None:
            self.last_sent = amount
            self.total_sent += amount
            self.render_dashboard(f"Tăng thành công: +{amount} {kind}!")
            wait = self._parse_timer(res)
            if wait:
                self._wait_timer(wait)
            return sent_msg

        msg = None
        m = re.search(r"color:\s*green;?'?[^>]*>\s*([^<]+)", res, re.I)
        if m and 'Checking Timer' not in m.group(1):
            msg = m.group(1).strip()
        if not msg:
            m = re.search(
                r'<span[^>]*>([^<]*(?:Successfully|sent)[^<]*)</span>',
                res,
                re.I,
            )
            if m and 'Checking Timer' not in m.group(1):
                msg = m.group(1).strip()

        if msg:
            amt = 100
            if isinstance(getattr(self, 'video_info', None), dict):
                try:
                    amt = int(self.video_info.get('select_lmt', 100) or 100)
                except Exception:
                    amt = 100
            self.last_sent = amt
            self.total_sent += amt
            self.render_dashboard(f"Tăng thành công: +{amt} ({msg})")
            wait = self._parse_timer(res)
            if wait:
                self._wait_timer(wait)
            return msg

        wait = self._parse_timer(res)
        if wait:
            self.render_dashboard(f"Đang chờ cooldown {wait}s...")
            self._wait_timer(wait)
            return f'cooldown {wait}s'

        return ""

    def get_video_info(self):
        try:
            vid = urlparse(self.url).path.rpartition("/")[2]
            if not vid or not vid.isdigit():
                return {'viewCount': 0, 'likeCount': 0, 'commentCount': 0, 'shareCount': 0, 'favoritesCount': 0, 'followersCount': 0}
            req = requests.get(
                f'https://tiktok.livecounts.io/video/stats/{vid}',
                headers={
                    'authority': 'tiktok.livecounts.io',
                    'origin': 'https://livecounts.io',
                    'user-agent': self.headers['user-agent']
                },
                timeout=5
            )
            if req.status_code == 200:
                data = req.json()
                if 'viewCount' in data:
                    return data
        except Exception:
            pass
        return {'viewCount': 0, 'likeCount': 0, 'commentCount': 0, 'shareCount': 0, 'favoritesCount': 0, 'followersCount': 0}

    def get_video_id(self, url_ = None, set_url=True):
        if url_ is None:
            url_ = self.url
        if url_[-1] == '/':
            url_ = url_[:-1]
        url = urlparse(url_).path.rpartition('/')[2]
        if url.isdigit():
            self.url = url_
            return url_
        try:
            r = requests.head(url_, headers={'user-agent': DEFAULT_USER_AGENT}, allow_redirects=True, timeout=10)
            if 'tiktok.com/@' in r.url:
                clean_url = r.url.split('?')[0]
                if set_url:
                    self.url = clean_url
                    print(f'  \033[1;36m[i] Định dạng link video --> \033[1;32m{self.url}\033[0m')
                return clean_url
        except Exception:
            pass
        try:
            request = requests.get(f'https://api.tokcount.com/?type=videoID&username=https://vm.tiktok.com/{url}',headers={'origin': 'https://tokcount.com','authority': 'api.tokcount.com','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}, timeout=10)
            if request.status_code == 200 and request.text:
                json_ = request.json()
                if 'author' in json_ and 'id' in json_:
                    if set_url:
                        self.url = f'https://www.tiktok.com/@{json_["author"]}/video/{json_["id"]}'
                        print(f'  \033[1;36m[i] Định dạng link video --> \033[1;32m{self.url}\033[0m')
                    return self.url
        except Exception:
            pass
        return False

    def check_config(self):
        pass

    def update_name(self):
        while True:
            try:
                video_info = self.get_video_info()
                if video_info.get('viewCount', 0) > 0:
                    self.text = f"SANG DEV | Views: {video_info['viewCount']} | Hearts: {video_info['likeCount']} | Comments: {video_info['commentCount']}"
                    if sys.platform.startswith('win'):
                        ctypes.windll.kernel32.SetConsoleTitleW(self.text)
            except Exception:
                pass
            time.sleep(15)


    def select_service(self):
        self.get_status_services()
        if self.service and self.service in self.services:
            return
        if self.headless:
            # Pick first active service
            for s_name, s_val in self.services_status.items():
                if s_val == 1:
                    self.service = s_name
                    return
            return

        while True:
            self.get_table()
            print(f"\n  \033[1;36m┌──[ \033[1;37mCHỌN DỊCH VỤ (Nhập STT) \033[1;36m]")
            service_id = input(f"  \033[1;36m└──▶ \033[1;33m").strip()
            if service_id.isdigit():
                service_id = int(service_id)
                if service_id in range(1, len(self.services) + 1):
                    services_list = list(self.services.keys())
                    self.service = services_list[service_id - 1]
                    print(f"  \033[1;32m[✓] Đã chọn dịch vụ: \033[1;33m{self.service}\033[0m\n")
                    break
                else:
                    print(f"  \033[1;31m[!] Số thứ tự không hợp lệ, vui lòng chọn lại!\033[0m\n")
            else:
                print(f"  \033[1;31m[!] Vui lòng chỉ nhập số!\033[0m\n")

    def run(self):
        self.select_service()
        while getattr(self, 'is_running', True):
            try:
                out = self.use_service()
                if out is False:
                    time.sleep(1.5)
                elif out and 'currently unavailable' in str(out).lower():
                    time.sleep(5)
                else:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                if not self.headless:
                    print('\n  \033[1;33m[!] Đã dừng chương trình.\033[0m')
                raise SystemExit(0)
            except Exception as e:
                if self.on_log:
                    self.on_log(f'LỖI | {e}')
                if not self.headless:
                    print(f'  \033[1;31m[!] LỖI | {e}\033[0m')
                time.sleep(3)

if __name__ == "__main__":
    try:
        Z = Zefoy()
        threading.Thread(target=Z.check_config, daemon=True).start()
        threading.Thread(target=Z.update_name, daemon=True).start()
        Z.send_captcha()
        Z.run()
    except KeyboardInterrupt:
        print('\n  \033[1;33m[!] Đã dừng chương trình.\033[0m')
        raise SystemExit(0)
