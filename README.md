# 🔔 코스피 주식 정보 대시보드

코스피 시총 상위 10개 기업의 주식 정보를 실시간으로 확인할 수 있는 웹 대시보드입니다.

## 📋 기능

- **실시간 주식 데이터**: yfinance API를 통해 주식 정보 수집
- **데이터베이스 저장**: SQLite를 사용한 주식 데이터 저장
- **시각화**: Chart.js를 통한 주가 변동 그래프
- **통계 분석**: 1년간 주가 수익률, 최고/최저가 분석
- **반응형 웹**: 모바일 및 데스크톱 지원

## 🏢 대상 기업 (코스피 시총 상위 10개)

1. 삼성전자 (005930.KS)
2. SK하이닉스 (000660.KS)
3. 삼성바이오로직스 (207940.KS)
4. 현대차 (005380.KS)
5. LG화학 (051910.KS)
6. 삼성SDI (006400.KS)
7. NAVER (035420.KS)
8. POSCO홀딩스 (005490.KS)
9. 삼성물산 (028260.KS)
10. 현대모비스 (012330.KS)

## 🚀 설치 및 실행

### 1. 필수 요구사항

- Python 3.7+
- pip (Python 패키지 관리자)

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 애플리케이션 실행

```bash
python app.py
```

### 4. 웹 브라우저 접속

```
http://localhost:5000
```

## 📊 사용 방법

### 1. 데이터 업데이트
- 웹 페이지에서 "📊 데이터 업데이트" 버튼 클릭
- 약 1-2분 소요 (10개 기업 데이터 수집)

### 2. 주식 정보 확인
- 왼쪽 패널에서 각 기업의 주식 정보 확인
- 현재가, 1년 수익률, 최고/최저가 표시

### 3. 차트 보기
- 오른쪽 패널에서 주식 선택
- 기간 선택 (1년/6개월/3개월/1개월)
- 주가 변동 그래프 확인

### 4. 통계 확인
- 상단에 전체 통계 표시
- 상승/하락/보합 종목 수 확인

## 🗂️ 프로젝트 구조

```
connectDB/
├── app.py              # Flask 메인 애플리케이션
├── database.py         # SQLite 데이터베이스 관리
├── stock_api.py        # 주식 API 데이터 수집
├── requirements.txt    # Python 패키지 의존성
├── templates/
│   └── index.html      # 웹 페이지 템플릿
├── static/
│   ├── style.css       # 스타일시트
│   └── script.js       # JavaScript 클라이언트
└── stock_data.db       # SQLite 데이터베이스 (자동 생성)
```

## 🔧 API 엔드포인트

- `GET /` - 메인 페이지
- `GET /api/stocks` - 전체 주식 목록 및 요약
- `GET /api/stocks/<symbol>` - 특정 주식 상세 정보
- `POST /api/update-data` - 주식 데이터 업데이트
- `GET /api/companies` - 등록된 회사 목록
- `GET /api/chart-data/<symbol>` - 차트 데이터

## 📈 데이터베이스 스키마

### companies 테이블
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    symbol TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    market_cap REAL,
    sector TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### stock_prices 테이블
```sql
CREATE TABLE stock_prices (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    date DATE NOT NULL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);
```

## 🛠️ 개발 환경 설정

### 개발 모드 실행
```bash
python app.py
```

### 데이터베이스 직접 조작
```python
from database import StockDatabase

db = StockDatabase()
companies = db.get_companies()
print(companies)
```

### 주식 데이터 직접 수집
```python
from stock_api import StockAPI

api = StockAPI()
api.update_all_kospi_data()
```

## 🔍 문제 해결

### 1. 패키지 설치 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 네트워크 오류
- 인터넷 연결 확인
- 방화벽 설정 확인
- VPN 사용 시 해제 후 재시도

### 3. 데이터베이스 오류
- stock_data.db 파일 삭제 후 재시작
- 데이터베이스 파일 권한 확인

## 📝 주의사항

- yfinance API는 무료 서비스로 요청 제한이 있을 수 있습니다
- 주식 데이터는 지연될 수 있으며 투자 결정의 근거로 사용하지 마세요
- 실제 투자 시에는 전문가와 상담하시기 바랍니다

## 🔄 업데이트 로그

### v1.0.0 (2024-01-01)
- 초기 버전 출시
- 코스피 상위 10개 기업 데이터 수집
- 웹 대시보드 및 차트 기능 구현

---

📧 문의사항이 있으시면 이슈를 등록해주세요. 