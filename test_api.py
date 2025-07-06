import yfinance as yf
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_yahoo_finance_api():
    """Yahoo Finance API 상태 테스트"""
    test_symbols = ['005930.KS', '000660.KS', '207940.KS']
    
    for symbol in test_symbols:
        try:
            logger.info(f"Testing {symbol}...")
            ticker = yf.Ticker(symbol)
            
            # 간단한 정보 요청
            info = ticker.info
            logger.info(f"✓ {symbol}: {info.get('longName', 'Unknown')}")
            
            # 짧은 대기
            time.sleep(2)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"✗ {symbol}: {error_msg}")
            
            if "429" in error_msg or "Too Many Requests" in error_msg:
                logger.warning("Rate limit detected! Waiting 30 seconds...")
                time.sleep(30)
            else:
                time.sleep(5)

if __name__ == "__main__":
    test_yahoo_finance_api() 