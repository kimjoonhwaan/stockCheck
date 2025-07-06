import FinanceDataReader as fdr
from datetime import datetime, timedelta
import logging
from stock_api_fdr import StockAPIFDR

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_finance_data_reader():
    """FinanceDataReader 테스트"""
    logger.info("=== FinanceDataReader 테스트 시작 ===")
    
    try:
        # 1. 삼성전자 데이터 가져오기 (기본)
        logger.info("1. 삼성전자 데이터 가져오기 (기본)...")
        df = fdr.DataReader('005930', '2024-01-01', '2024-12-31')
        logger.info(f"✓ 삼성전자 기본 데이터: {len(df)}개 레코드")
        logger.info(f"✓ 컬럼: {df.columns.tolist()}")
        logger.info(f"✓ 최근 데이터:\n{df.tail(3)}")
        
        # 2. KRX 소스로 삼성전자 데이터 가져오기
        logger.info("2. KRX 소스로 삼성전자 데이터 가져오기...")
        try:
            df_krx = fdr.DataReader('KRX:005930', '2024-01-01', '2024-12-31')
            logger.info(f"✓ 삼성전자 KRX 데이터: {len(df_krx)}개 레코드")
            logger.info(f"✓ KRX 컬럼: {df_krx.columns.tolist()}")
        except Exception as e:
            logger.error(f"KRX 소스 실패: {e}")
        
        # 3. NAVER 소스로 삼성전자 데이터 가져오기
        logger.info("3. NAVER 소스로 삼성전자 데이터 가져오기...")
        try:
            df_naver = fdr.DataReader('NAVER:005930', '2024-01-01', '2024-12-31')
            logger.info(f"✓ 삼성전자 NAVER 데이터: {len(df_naver)}개 레코드")
            logger.info(f"✓ NAVER 컬럼: {df_naver.columns.tolist()}")
        except Exception as e:
            logger.error(f"NAVER 소스 실패: {e}")
        
        # 4. 코스피 상장 종목 리스트
        logger.info("4. 코스피 상장 종목 리스트...")
        try:
            kospi_list = fdr.StockListing('KOSPI')
            logger.info(f"✓ 코스피 상장 종목 수: {len(kospi_list)}개")
            logger.info(f"✓ 상위 5개 종목:\n{kospi_list.head()}")
        except Exception as e:
            logger.error(f"코스피 리스트 실패: {e}")
        
        logger.info("=== FinanceDataReader 테스트 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"FinanceDataReader 테스트 실패: {e}")
        return False

def test_stock_api_fdr():
    """StockAPIFDR 클래스 테스트"""
    logger.info("=== StockAPIFDR 클래스 테스트 시작 ===")
    
    try:
        api = StockAPIFDR()
        
        # 1. 삼성전자 데이터 가져오기
        logger.info("1. 삼성전자 주가 데이터 테스트...")
        stock_data = api.fetch_stock_data('005930', period='1m')
        if stock_data is not None:
            logger.info(f"✓ 삼성전자 데이터: {len(stock_data)}개 레코드")
            logger.info(f"✓ 컬럼: {stock_data.columns.tolist()}")
            logger.info(f"✓ 최근 3일 데이터:\n{stock_data.tail(3)}")
        
        # 2. 회사 정보 가져오기
        logger.info("2. 회사 정보 테스트...")
        company_info = api.get_company_info('005930')
        logger.info(f"✓ 회사 정보: {company_info}")
        
        logger.info("=== StockAPIFDR 클래스 테스트 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"StockAPIFDR 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    test_finance_data_reader()
    print()
    test_stock_api_fdr() 