import sqlite3
import pandas as pd
from datetime import datetime

def connect_db():
    """데이터베이스 연결"""
    return sqlite3.connect('stock_data.db')

def show_all_companies():
    """모든 회사 목록 조회"""
    conn = connect_db()
    query = "SELECT * FROM companies"
    df = pd.read_sql_query(query, conn)
    conn.close()
    print("=== 등록된 회사 목록 ===")
    print(df.to_string(index=False))
    return df

def show_latest_prices():
    """최신 주식 가격 조회"""
    conn = connect_db()
    query = """
    SELECT c.name, c.symbol, sp.date, sp.close_price, sp.volume
    FROM companies c
    JOIN stock_prices sp ON c.symbol = sp.symbol
    WHERE sp.date = (
        SELECT MAX(date) FROM stock_prices sp2 WHERE sp2.symbol = c.symbol
    )
    ORDER BY sp.close_price DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    print("\n=== 최신 주식 가격 ===")
    print(df.to_string(index=False))
    return df

def show_stock_history(symbol='005930.KS', days=30):
    """특정 주식의 최근 가격 이력 조회"""
    conn = connect_db()
    query = """
    SELECT date, open_price, high_price, low_price, close_price, volume
    FROM stock_prices
    WHERE symbol = ?
    ORDER BY date DESC
    LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=[symbol, days])
    conn.close()
    print(f"\n=== {symbol} 최근 {days}일 데이터 ===")
    print(df.to_string(index=False))
    return df

def show_price_statistics():
    """주식 가격 통계 조회"""
    conn = connect_db()
    query = """
    SELECT 
        c.name,
        c.symbol,
        COUNT(sp.date) as data_count,
        MIN(sp.close_price) as min_price,
        MAX(sp.close_price) as max_price,
        AVG(sp.close_price) as avg_price,
        MIN(sp.date) as start_date,
        MAX(sp.date) as end_date
    FROM companies c
    JOIN stock_prices sp ON c.symbol = sp.symbol
    GROUP BY c.symbol, c.name
    ORDER BY avg_price DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    print("\n=== 주식 가격 통계 ===")
    print(df.to_string(index=False))
    return df

def custom_query(sql_query):
    """사용자 정의 SQL 쿼리 실행"""
    conn = connect_db()
    try:
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        print(f"\n=== 쿼리 결과 ===")
        print(df.to_string(index=False))
        return df
    except Exception as e:
        conn.close()
        print(f"쿼리 실행 오류: {e}")
        return None

if __name__ == "__main__":
    print("📊 주식 데이터베이스 조회 도구")
    print("=" * 50)
    
    # 1. 모든 회사 목록
    show_all_companies()
    
    # 2. 최신 주식 가격
    show_latest_prices()
    
    # 3. 삼성전자 최근 30일 데이터
    show_stock_history('005930.KS', 30)
    
    # 4. 주식 가격 통계
    show_price_statistics()
    
    print("\n" + "=" * 50)
    print("🔍 사용 가능한 함수:")
    print("- show_all_companies(): 모든 회사 목록")
    print("- show_latest_prices(): 최신 주식 가격")
    print("- show_stock_history(symbol, days): 특정 주식 이력")
    print("- show_price_statistics(): 주식 가격 통계")
    print("- custom_query(sql): 사용자 정의 쿼리")
    print("\n예시:")
    print("python db_query.py")
    print("또는 Python에서 import해서 사용하세요!") 