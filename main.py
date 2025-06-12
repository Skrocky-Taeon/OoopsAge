import os

# 환경 변수로 앱 버전 선택
app_version = os.environ.get('APP_VERSION', 'english')

if app_version == 'korean':
    from app_korean import app
    print("🇰🇷 한국어 버전 (나이맞히기) 실행 중...")
else:
    from app_simple import app
    print("🇺🇸 영어 버전 (Ooops Age) 실행 중...")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
