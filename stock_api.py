import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from database import StockDatabase

class StockAPI:
    def __init__(self):
        self.db = StockDatabase()
        # 코스피 시총 상위 10개 회사 심볼 (한국 주식은 .KS 접미사 사용)
        self.kospi_top10 = {
            '005930.KS': '삼성전자',
            '000660.KS': 'SK하이닉스', 
            '207940.KS': '삼성바이오로직스',
            '005380.KS': '현대차',
            '051910.KS': 'LG화학',
            '006400.KS': '삼성SDI',
            '035420.KS': 'NAVER',
            '005490.KS': 'POSCO홀딩스',
            '028260.KS': '삼성물산',
            '012330.KS': '현대모비스'
        }
    
    def fetch_stock_data(self, symbol, period='1y'):
        """특정 심볼의 주식 데이터 가져오기"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                print(f"No data found for symbol: {symbol}")
                return None
            
            # 인덱스를 날짜 문자열로 변환
            data.index = data.index.strftime('%Y-%m-%d')
            
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_company_info(self, symbol):
        """회사 정보 가져오기"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            company_info = {
                'symbol': symbol,
                'name': info.get('longName', self.kospi_top10.get(symbol, symbol)),
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown')
            }
            
            return company_info
        except Exception as e:
            print(f"Error getting company info for {symbol}: {e}")
            return {
                'symbol': symbol,
                'name': self.kospi_top10.get(symbol, symbol),
                'market_cap': 0,
                'sector': 'Unknown'
            }
    
    def update_all_kospi_data(self):
        """코스피 상위 10개 회사의 데이터 업데이트"""
        print("코스피 상위 10개 회사 데이터 업데이트 시작...")
        
        for symbol, name in self.kospi_top10.items():
            print(f"Processing {name} ({symbol})...")
            
            # 회사 정보 가져오기 및 저장
            company_info = self.get_company_info(symbol)
            self.db.insert_company(
                symbol=company_info['symbol'],
                name=company_info['name'],
                market_cap=company_info['market_cap'],
                sector=company_info['sector']
            )
            
            # 주식 가격 데이터 가져오기 및 저장
            stock_data = self.fetch_stock_data(symbol, period='1y')
            if stock_data is not None:
                self.db.insert_stock_prices(symbol, stock_data)
                print(f"✓ {name} 데이터 저장 완료")
            else:
                print(f"✗ {name} 데이터 가져오기 실패")
        
        print("모든 데이터 업데이트 완료!")
    
    def get_stock_analysis(self, symbol):
        """주식 분석 데이터 생성"""
        df = self.db.get_stock_prices(symbol, days=365)
        
        if df.empty:
            return None
        
        # 날짜 정렬 (오래된 것부터)
        df = df.sort_values('date')
        
        # 기본 통계
        current_price = df.iloc[-1]['close_price']
        year_ago_price = df.iloc[0]['close_price']
        year_return = ((current_price - year_ago_price) / year_ago_price) * 100
        
        # 최고/최저가
        year_high = df['high_price'].max()
        year_low = df['low_price'].min()
        
        # 평균 거래량
        avg_volume = df['volume'].mean()
        
        analysis = {
            'symbol': symbol,
            'current_price': current_price,
            'year_return': year_return,
            'year_high': year_high,
            'year_low': year_low,
            'avg_volume': avg_volume,
            'data_points': len(df),
            'chart_data': df[['date', 'close_price', 'volume']].to_dict('records')
        }
        
        return analysis
    
    def get_all_stocks_summary(self):
        """전체 주식 요약 정보"""
        latest_prices = self.db.get_latest_prices()
        
        if latest_prices.empty:
            return []
        
        summary = []
        for _, row in latest_prices.iterrows():
            analysis = self.get_stock_analysis(row['symbol'])
            if analysis:
                summary.append({
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'current_price': row['close_price'],
                    'year_return': analysis['year_return'],
                    'year_high': analysis['year_high'],
                    'year_low': analysis['year_low']
                })
        
        return summary

if __name__ == "__main__":
    # 테스트용 코드
    stock_api = StockAPI()
    stock_api.update_all_kospi_data() 