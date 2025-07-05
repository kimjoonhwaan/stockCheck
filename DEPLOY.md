# 🚀 주식 정보 대시보드 배포 가이드

## 🎯 배포 옵션

### 1. 로컬 네트워크 배포 (현재 상태)
```bash
# 가상환경 활성화
venv\Scripts\activate

# 서버 실행
python app.py
```
- **접속 주소**: `http://127.0.0.1:5000` (로컬)
- **네트워크 접속**: `http://192.168.35.96:5000` (같은 네트워크)

### 2. 프로덕션 서버 (Gunicorn)
```bash
# 패키지 설치
pip install gunicorn

# 프로덕션 서버 실행
gunicorn --bind 0.0.0.0:8000 --workers 4 wsgi:app
```
- **접속 주소**: `http://localhost:8000`
- **Windows**: `deploy.bat` 파일 실행

### 3. 도커 배포

#### 3.1 도커 빌드 & 실행
```bash
# 도커 이미지 빌드
docker build -t stock-dashboard .

# 컨테이너 실행
docker run -p 8000:5000 -v $(pwd)/stock_data.db:/app/stock_data.db stock-dashboard
```

#### 3.2 도커 컴포즈 (권장)
```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down

# 로그 확인
docker-compose logs -f
```
- **접속 주소**: `http://localhost:8000`

### 4. 클라우드 배포

#### 4.1 Heroku 배포
```bash
# Heroku CLI 설치 후
heroku login
heroku create your-stock-dashboard
git add .
git commit -m "Initial deployment"
git push heroku main
```

#### 4.2 Railway 배포
1. GitHub에 코드 푸시
2. Railway 연결: https://railway.app
3. 자동 배포 완료

#### 4.3 Render 배포
1. GitHub에 코드 푸시
2. Render 연결: https://render.com
3. 무료 플랜 이용 가능

### 5. VPS 서버 배포

#### 5.1 Ubuntu 서버 설정
```bash
# 패키지 업데이트
sudo apt update && sudo apt upgrade -y

# Python 설치
sudo apt install python3 python3-pip python3-venv -y

# 프로젝트 클론
git clone <your-repo-url>
cd connectDB

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 서비스 실행
gunicorn --bind 0.0.0.0:8000 --workers 4 wsgi:app
```

#### 5.2 systemd 서비스 등록
```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/stock-dashboard.service
```

```ini
[Unit]
Description=Stock Dashboard
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/connectDB
Environment=PATH=/home/ubuntu/connectDB/venv/bin
ExecStart=/home/ubuntu/connectDB/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable stock-dashboard
sudo systemctl start stock-dashboard
```

### 6. Nginx 리버스 프록시 설정

#### 6.1 Nginx 설치
```bash
sudo apt install nginx -y
```

#### 6.2 설정 파일 생성
```bash
sudo nano /etc/nginx/sites-available/stock-dashboard
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 사이트 활성화
sudo ln -s /etc/nginx/sites-available/stock-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. SSL 인증서 설정 (Let's Encrypt)
```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx -y

# SSL 인증서 설치
sudo certbot --nginx -d your-domain.com
```

## 🔧 환경 변수 설정

### 프로덕션 환경 변수
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
export DATABASE_URL=sqlite:///stock_data.db
```

### .env 파일 생성
```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///stock_data.db
```

## 📊 데이터베이스 백업

### 자동 백업 스크립트
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp stock_data.db "backups/stock_data_$DATE.db"
```

### 크론탭 설정
```bash
# 매일 자정에 백업
0 0 * * * /path/to/backup.sh
```

## 🔍 모니터링 및 로깅

### 로그 설정
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 헬스 체크 엔드포인트
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

## 🛡️ 보안 고려사항

1. **방화벽 설정**: 필요한 포트만 열기
2. **HTTPS 사용**: SSL 인증서 설정
3. **API 키 보안**: 환경 변수 사용
4. **정기 업데이트**: 패키지 보안 업데이트
5. **접근 제한**: IP 화이트리스트 설정

## 📈 성능 최적화

1. **Gunicorn 워커 수 조정**: CPU 코어 수 * 2 + 1
2. **데이터베이스 최적화**: 인덱스 생성
3. **캐싱**: Redis 또는 Memcached 사용
4. **CDN 사용**: 정적 파일 서빙

## 🆘 문제 해결

### 일반적인 오류
1. **포트 충돌**: 다른 포트 사용
2. **권한 오류**: 사용자 권한 확인
3. **메모리 부족**: 워커 수 조정
4. **DB 락**: 동시 접근 제한

### 로그 확인
```bash
# 애플리케이션 로그
tail -f app.log

# 시스템 로그
sudo journalctl -u stock-dashboard -f

# 도커 로그
docker logs stock-dashboard
```

## 📞 지원

배포 관련 문제가 있으시면 다음을 확인해주세요:
1. 로그 파일
2. 포트 사용 상태
3. 방화벽 설정
4. 환경 변수 설정

---

🎉 **축하합니다!** 주식 정보 대시보드가 성공적으로 배포되었습니다! 