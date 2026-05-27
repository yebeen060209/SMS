#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SubSaver - 스마트 구독 과소비 예방 및 관리 시스템 실행기
--------------------------------------------------
이 스크립트는 로컬 웹 서버를 실행하고 브라우저를 자동으로 열어 
독창적인 Glassmorphism 대시보드를 바로 탐색할 수 있도록 돕습니다.
"""

import os
import sys
import webbrowser
import http.server
import socketserver
import threading
import time


PORT = 8000
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DIRECTORY = os.path.join(CURRENT_DIR, "subscription_manager")
if not os.path.exists(DIRECTORY):
    DIRECTORY = os.path.join(CURRENT_DIR, "antigravity_assignment", "subscription_manager")


class SubSaverHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve from the subscription_manager subfolder
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def log_message(self, format, *args):
        # Custom silent logging to keep terminal clean
        pass

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), SubSaverHTTPHandler) as httpd:
            print(f"[✔] 로컬 웹 서버가 포트 {PORT}에서 활성화되었습니다.")
            httpd.serve_forever()
    except Exception as e:
        print(f"[X] 서버 기동 실패: {e}")
        print("이미 포트 8000이 사용 중일 수 있습니다.")

if __name__ == "__main__":
    print("=" * 65)
    print("      SubSaver - 스마트 구독 경제 과소비 예방 시스템 실행기")
    print("=" * 65)
    

    # FALLBACK to HTML Server
    if not os.path.exists(DIRECTORY):
        print(f"[X] 오류: 대시보드 디렉토리 ({DIRECTORY})를 찾을 수 없습니다.")
        sys.exit(1)
        
    print("[1] 로컬 백그라운드 웹 서버를 시작하는 중...")
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait half a second for server to bind
    time.sleep(0.5)
    
    url = f"http://localhost:{PORT}/index.html"
    print(f"[2] 브라우저를 통해 대시보드 웹 어플리케이션에 접속합니다...")
    print(f"    접속 주소: {url}")
    print("-" * 65)
    
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[!] 브라우저 자동 호출 실패: {e}")
        print(f"    웹 브라우저를 열고 직접 주소창에 {url} 을 입력해 주세요.")
        
    print("\n[알림] 대시보드 사용을 마치신 후, 이곳에서 [Ctrl + C]를 누르시면 서버가 정상 안전 종료됩니다.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[▶] 웹 서버를 정상 종료합니다. SubSaver를 이용해 주셔서 감사합니다!")
        sys.exit(0)

