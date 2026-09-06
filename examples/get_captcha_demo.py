"""Demo: fetch zefoy captcha and save captcha.png"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from zefoy import ZefoyCaptcha


def main() -> None:
    client = ZefoyCaptcha()
    captcha = client.get()
    out = ROOT / "captcha.png"
    captcha.save(str(out))
    print("session_id :", captcha.session_id)
    print("token      :", captcha.captcha_token)
    print("image_url  :", captcha.image_url)
    print("saved      :", out, f"({len(captcha.image_bytes)} bytes)")


if __name__ == "__main__":
    main()
