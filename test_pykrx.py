from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pykrx_api():
    """pykrx API 테스트"""
    logger.info("=== pykrx API 테스트 시작 ===")
    
    try:
        # 1. 삼성전자 종목명 가져오기
        logger.info("1. 삼성전자 종목명 테스트...")
        company_name = stock.get_market_ticker_name('005930')
        logger.info(f"✓ 삼성전자 종목명: {company_name}")
        
        # 2. 코스피 종목 리스트 가져오기
        logger.info("2. 코스피 종목 리스트 테스트...")
        today = datetime.now().strftime('%Y%m%d')
        tickers = stock.get_market_ticker_list(today, market='KOSPI')
        logger.info(f"✓ 코스피 종목 수: {len(tickers)}개")
        logger.info(f"✓ 처음 5개 종목: {tickers[:5]}")
        
        # 3. 삼성전자 주가 데이터 가져오기
        logger.info("3. 삼성전자 주가 데이터 테스트...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        df = stock.get_market_ohlcv(start_str, end_str, '005930')
        logger.info(f"✓ 삼성전자 주가 데이터: {len(df)}개 레코드")
        logger.info(f"✓ 최근 데이터:\n{df.tail(3)}")
        
        # 4. 시가총액 데이터 가져오기
        logger.info("4. 시가총액 데이터 테스트...")
        market_cap_df = stock.get_market_cap(today, today, '005930')
        if not market_cap_df.empty:
            market_cap = market_cap_df.iloc[0]['시가총액']
            logger.info(f"✓ 삼성전자 시가총액: {market_cap:,}원")
        
        # 5. 상위 10개 종목 시가총액 순위
        logger.info("5. 시가총액 상위 종목 테스트...")
        all_caps = stock.get_market_cap(today, market='KOSPI')
        top_10 = all_caps.nlargest(10, '시가총액')
        logger.info(f"✓ 시가총액 상위 10개 종목:")
        for i, (symbol, row) in enumerate(top_10.iterrows(), 1):
            name = stock.get_market_ticker_name(symbol)
            market_cap = row['시가총액']
            logger.info(f"   {i}. {name}({symbol}): {market_cap:,}원")
        
        logger.info("=== pykrx API 테스트 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"pykrx API 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    test_pykrx_api() 