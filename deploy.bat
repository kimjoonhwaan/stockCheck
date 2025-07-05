@echo off
echo 📦 주식 정보 대시보드 배포 시작...

echo.
echo 🔧 가상환경 활성화...
call venv\Scripts\activate

echo.
echo 📥 패키지 업데이트...
pip install -r requirements.txt

echo.
echo 🚀 프로덕션 서버 시작...
echo 서버 주소: http://0.0.0.0:8000
echo 중지하려면 Ctrl+C를 누르세요
echo.

waitress-serve --host=0.0.0.0 --port=8000 wsgi:app

pause 