import os

# 환경 변수로 앱 버전 선택
app_version = os.environ.get('APP_VERSION', 'english')

if app_version == 'korean':
    from app_korean import app
else:
    from app_simple import app

# Vercel에서 필요한 app 객체 노출
application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
