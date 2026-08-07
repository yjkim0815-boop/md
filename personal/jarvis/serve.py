"""Dominic Jarvis 로컬 호스팅.

    python serve.py            이 PC 에서만  (127.0.0.1:8708)
    python serve.py --lan      같은 Wi-Fi 공개 (0.0.0.0:8708)
    python serve.py --port 9000

주의: 인증이 없다. --lan 으로 띄우면 같은 네트워크의 누구나 주소만 알면
      history.js(대화 원문)를 읽을 수 있다. 회사망에서는 기본값(로컬 전용)을 쓸 것.
종료: 이 창에서 Ctrl+C.
"""

import argparse
import http.server
import os
import socket
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PORT = 8708


class Handler(http.server.SimpleHTTPRequestHandler):
    """루트 접속을 dashboard.html 로 보내고, 캐시를 끈다."""

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_GET(self):
        if self.path in ("/", ""):
            self.path = "/dashboard.html"
        return super().do_GET()

    def end_headers(self):
        # data.js 는 0.1초마다 다시 읽는다. 304 가 끼면 화면이 멈춘다.
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        # 폴링이 초당 10회라 기본 로그를 켜두면 창이 도배된다.
        pass


def lan_ip() -> str:
    """기본 경로로 나가는 인터페이스의 IPv4 를 얻는다(패킷은 실제로 보내지 않는다)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="Dominic Jarvis 호스팅")
    ap.add_argument("--lan", action="store_true", help="같은 Wi-Fi 에 공개 (기본은 이 PC 전용)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--no-open", action="store_true", help="브라우저 자동 실행 안 함")
    args = ap.parse_args()

    host = "0.0.0.0" if args.lan else "127.0.0.1"
    url = f"http://localhost:{args.port}/dashboard.html"

    print("=" * 52)
    print("  Dominic Jarvis")
    print("=" * 52)
    print(f"  이 PC   {url}")
    if args.lan:
        print(f"  폰      http://{lan_ip()}:{args.port}/dashboard.html")
        print()
        print("  [주의] 인증 없음 — 같은 네트워크에서 대화 히스토리가 읽힙니다.")
    else:
        print("  (외부 비공개. 폰에서 보려면 --lan)")
    print()
    print("  종료: Ctrl+C")
    print("=" * 52)

    if not args.no_open:
        webbrowser.open(url)

    srv = http.server.ThreadingHTTPServer((host, args.port), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  종료했습니다.")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
