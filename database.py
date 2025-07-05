import sqlite3
import pandas as pd
from datetime import datetime

class StockDatabase:
    def __init__(self, db_name='stock_data.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 주식 회사 정보 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            market_cap REAL,
            sector TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 주식 가격 데이터 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date DATE NOT NULL,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL,
            volume INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, date)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_company(self, symbol, name, market_cap=None, sector=None):
        """회사 정보 삽입"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO companies (symbol, name, market_cap, sector)
            VALUES (?, ?, ?, ?)
            ''', (symbol, name, market_cap, sector))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting company: {e}")
            return False
        finally:
            conn.close()
    
    def insert_stock_prices(self, symbol, df):
        """주식 가격 데이터 삽입"""
        conn = sqlite3.connect(self.db_name)
        
        try:
            # DataFrame을 데이터베이스에 삽입
            df_to_insert = df.copy()
            df_to_insert['symbol'] = symbol
            df_to_insert['date'] = df_to_insert.index
            df_to_insert.reset_index(drop=True, inplace=True)
            
            # 컬럼명 변경
            df_to_insert.rename(columns={
                'Open': 'open_price',
                'High': 'high_price',
                'Low': 'low_price',
                'Close': 'close_price',
                'Volume': 'volume'
            }, inplace=True)
            
            # 필요한 컬럼만 선택
            df_to_insert = df_to_insert[['symbol', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
            
            # 데이터베이스에 삽입
            df_to_insert.to_sql('stock_prices', conn, if_exists='append', index=False)
            return True
        except Exception as e:
            print(f"Error inserting stock prices: {e}")
            return False
        finally:
            conn.close()
    
    def get_companies(self):
        """등록된 회사 목록 조회"""
        conn = sqlite3.connect(self.db_name)
        try:
            df = pd.read_sql_query("SELECT * FROM companies", conn)
            return df
        except Exception as e:
            print(f"Error getting companies: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def get_stock_prices(self, symbol, days=365):
        """특정 심볼의 주식 가격 데이터 조회"""
        conn = sqlite3.connect(self.db_name)
        try:
            query = '''
            SELECT * FROM stock_prices 
            WHERE symbol = ? 
            ORDER BY date DESC 
            LIMIT ?
            '''
            df = pd.read_sql_query(query, conn, params=(symbol, days))
            return df
        except Exception as e:
            print(f"Error getting stock prices: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def get_latest_prices(self):
        """모든 주식의 최신 가격 조회"""
        conn = sqlite3.connect(self.db_name)
        try:
            query = '''
            SELECT sp.symbol, c.name, sp.close_price, sp.date
            FROM stock_prices sp
            JOIN companies c ON sp.symbol = c.symbol
            WHERE sp.date = (
                SELECT MAX(date) FROM stock_prices sp2 WHERE sp2.symbol = sp.symbol
            )
            '''
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            print(f"Error getting latest prices: {e}")
            return pd.DataFrame()
        finally:
            conn.close() 