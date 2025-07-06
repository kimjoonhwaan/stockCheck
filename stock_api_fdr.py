import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
from database import StockDatabase
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockAPIFDR:
    def __init__(self):
        self.db = StockDatabase()
        # 코스피 시총 상위 10개 회사
        self.kospi_top10 = {
            '005930': '삼성전자',
            '000660': 'SK하이닉스', 
            '207940': '삼성바이오로직스',
            '005380': '현대차',
            '051910': 'LG화학',
            '006400': '삼성SDI',
            '035420': 'NAVER',
            '005490': 'POSCO홀딩스',
            '028260': '삼성물산',
            '012330': '현대모비스'
        }
    
    def fetch_stock_data(self, symbol, period='1y'):
        """FinanceDataReader를 사용한 주식 데이터 가져오기"""
        try:
            logger.info(f"Fetching stock data for {symbol} using FinanceDataReader...")
            
            # 기간 계산
            end_date = datetime.now()
            if period == '1y':
                start_date = end_date - timedelta(days=365)
            elif period == '6m':
                start_date = end_date - timedelta(days=180)
            elif period == '3m':
                start_date = end_date - timedelta(days=90)
            elif period == '1m':
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=365)
            
            # FinanceDataReader로 데이터 가져오기 (KRX 소스 우선)
            try:
                # KRX 소스 시도
                df = fdr.DataReader(f'KRX:{symbol}', start_date, end_date)
                logger.info(f"✓ KRX 소스에서 데이터 가져옴: {symbol}")
            except:
                try:
                    # NAVER 소스 시도
                    df = fdr.DataReader(f'NAVER:{symbol}', start_date, end_date)
                    logger.info(f"✓ NAVER 소스에서 데이터 가져옴: {symbol}")
                except:
                    # 기본 소스 시도
                    df = fdr.DataReader(symbol, start_date, end_date)
                    logger.info(f"✓ 기본 소스에서 데이터 가져옴: {symbol}")
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            # 컬럼명이 이미 영어인 경우 그대로 사용
            if 'Close' not in df.columns and '종가' in df.columns:
                # 한글 컬럼명을 영어로 변경
                df.rename(columns={
                    '시가': 'Open',
                    '고가': 'High', 
                    '저가': 'Low',
                    '종가': 'Close',
                    '거래량': 'Volume'
                }, inplace=True)
            
            # 필요한 컬럼만 선택
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df[required_columns]
            
            # 인덱스를 날짜 문자열로 변환
            df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')
            
            logger.info(f"Successfully fetched {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_company_info(self, symbol):
        """회사 정보 가져오기"""
        try:
            logger.info(f"Getting company info for {symbol}...")
            
            # FinanceDataReader로 기본 정보 가져오기
            try:
                # 최근 1개월 데이터로 현재가 정보 얻기
                recent_df = fdr.DataReader(symbol, datetime.now() - timedelta(days=30), datetime.now())
                if not recent_df.empty:
                    current_price = recent_df['Close'].iloc[-1] if 'Close' in recent_df.columns else recent_df['종가'].iloc[-1]
                    market_cap = current_price * 5969782550  # 삼성전자 기준 상장주식수 (임시)
                else:
                    market_cap = 0
            except:
                market_cap = 0
            
            company_info = {
                'symbol': symbol,
                'name': self.kospi_top10.get(symbol, f'종목{symbol}'),
                'market_cap': market_cap,
                'sector': 'Technology'
            }
            
            logger.info(f"Successfully got company info for {symbol}")
            return company_info
            
        except Exception as e:
            logger.error(f"Error getting company info for {symbol}: {e}")
            return {
                'symbol': symbol,
                'name': self.kospi_top10.get(symbol, f'종목{symbol}'),
                'market_cap': 0,
                'sector': 'Unknown'
            }
    
    def update_all_kospi_data(self, conservative_mode=True):
        """코스피 상위 10개 회사의 데이터 업데이트 (FinanceDataReader 사용)"""
        logger.info("FinanceDataReader를 사용하여 코스피 상위 10개 회사 데이터 업데이트 시작...")
        
        success_count = 0
        total_count = len(self.kospi_top10)
        
        for i, (symbol, name) in enumerate(self.kospi_top10.items(), 1):
            try:
                logger.info(f"Processing {name} ({symbol})... [{i}/{total_count}]")
                
                # 회사 정보 가져오기 및 저장
                company_info = self.get_company_info(symbol)
                if company_info:
                    self.db.insert_company(
                        symbol=company_info['symbol'],
                        name=company_info['name'],
                        market_cap=company_info['market_cap'],
                        sector=company_info['sector']
                    )
                    logger.info(f"✓ {name} 회사 정보 저장 완료")
                
                # 주식 가격 데이터 가져오기 및 저장
                stock_data = self.fetch_stock_data(symbol, period='1y')
                if stock_data is not None and not stock_data.empty:
                    # 데이터베이스에 저장
                    for date, row in stock_data.iterrows():
                        self.db.insert_stock_price(
                            symbol=symbol,
                            date=date,
                            open_price=float(row['Open']),
                            high_price=float(row['High']),
                            low_price=float(row['Low']),
                            close_price=float(row['Close']),
                            volume=int(row['Volume']) if pd.notna(row['Volume']) else 0
                        )
                    
                    success_count += 1
                    logger.info(f"✓ {name} 주가 데이터 저장 완료 ({len(stock_data)}개 레코드)")
                else:
                    logger.warning(f"✗ {name} 주가 데이터 가져오기 실패")
                
                # 요청 간격 조정
                if conservative_mode:
                    time.sleep(3)  # 3초 대기
                else:
                    time.sleep(1)  # 1초 대기
                
            except Exception as e:
                logger.error(f"Error processing {name} ({symbol}): {e}")
                continue
        
        logger.info(f"데이터 업데이트 완료: {success_count}/{total_count} 성공")
        return success_count
    
    def get_all_stocks_summary(self):
        """모든 주식 요약 정보 가져오기"""
        companies = self.db.get_all_companies()
        summary = []
        
        for company in companies:
            symbol = company[0]
            name = company[1]
            
            # 최근 주가 정보 가져오기
            recent_prices = self.db.get_recent_stock_prices(symbol, days=30)
            
            if recent_prices:
                latest_price = recent_prices[0]
                current_price = latest_price[4]  # close_price
                
                # 1년 전 가격과 비교
                year_ago_prices = self.db.get_stock_prices_by_date_range(
                    symbol, 
                    (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                    (datetime.now() - timedelta(days=350)).strftime('%Y-%m-%d')
                )
                
                year_return = 0
                if year_ago_prices:
                    year_ago_price = year_ago_prices[0][4]
                    year_return = ((current_price - year_ago_price) / year_ago_price) * 100
                
                summary.append({
                    'symbol': symbol,
                    'name': name,
                    'current_price': current_price,
                    'year_return': round(year_return, 2)
                })
        
        return summary
    
    def get_stock_chart_data(self, symbol, days=365):
        """특정 종목의 차트 데이터 가져오기"""
        stock_prices = self.db.get_recent_stock_prices(symbol, days)
        
        if not stock_prices:
            return None
        
        # 날짜 순으로 정렬 (오래된 것부터)
        stock_prices.reverse()
        
        chart_data = {
            'dates': [],
            'prices': [],
            'volumes': []
        }
        
        for price in stock_prices:
            chart_data['dates'].append(price[1])  # date
            chart_data['prices'].append(price[4])  # close_price
            chart_data['volumes'].append(price[5])  # volume
        
        return chart_data 