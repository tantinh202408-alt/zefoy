"""Demo: pure requests + gen fingerprint + NewOCR + XHR submit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from zefoy import ZefoyClient


def main() -> None:
    client = ZefoyClient()

    def on_attempt(i, captcha, answer):
        out = ROOT / f"attempt_{i}.png"
        captcha.save(str(out))
        print(
            f"[{i}] NewOCR={answer!r} saved={out.name} token={captcha.captcha_token}"
        )

    result = client.solve_and_submit(max_attempts=5, on_attempt=on_attempt)
    print("success :", result.success)
    print("answer  :", result.answer)
    print("attempts:", result.attempts)
    print("session :", result.session_id)
    print("message :", result.message)
    if result.success and result.services:
        print()
        result.print_services(use_color=True)
    if result.html:
        (ROOT / "after_submit.html").write_text(result.html, encoding="utf-8")
        print("\nsaved after_submit.html")


if __name__ == "__main__":
    main()
