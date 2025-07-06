from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import logging
import time
import os
from stock_api_fdr import StockAPIFDR

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 전역 변수로 StockAPIFDR 인스턴스 생성 (FinanceDataReader 사용)
stock_api = StockAPIFDR()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/stocks')
def get_stocks():
    """전체 주식 목록 및 요약 정보 API"""
    try:
        logger.info("Fetching all stocks summary")
        start_time = time.time()
        
        summary = stock_api.get_all_stocks_summary()
        
        end_time = time.time()
        logger.info(f"Successfully fetched {len(summary)} stocks in {end_time - start_time:.2f} seconds")
        
        return jsonify({
            'success': True,
            'data': summary,
            'count': len(summary)
        })
    except Exception as e:
        logger.error(f"Error in get_stocks: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch stocks: {str(e)}',
            'data': []
        }), 500

@app.route('/api/stocks/<symbol>')
def get_stock_detail(symbol):
    """특정 주식의 상세 정보 API"""
    try:
        logger.info(f"Fetching stock detail for {symbol}")
        start_time = time.time()
        
        # 회사 정보 가져오기
        company_info = stock_api.get_company_info(symbol)
        
        # 차트 데이터 가져오기
        chart_data = stock_api.get_stock_chart_data(symbol, days=365)
        
        if company_info and chart_data:
            analysis = {
                'symbol': symbol,
                'name': company_info['name'],
                'market_cap': company_info['market_cap'],
                'sector': company_info['sector'],
                'chart_data': chart_data
            }
        else:
            analysis = None
        
        end_time = time.time()
        logger.info(f"Fetched stock detail for {symbol} in {end_time - start_time:.2f} seconds")
        
        if analysis:
            return jsonify({
                'success': True,
                'data': analysis
            })
        else:
            logger.warning(f"No data found for symbol: {symbol}")
            return jsonify({
                'success': False,
                'error': f'Stock data not found for {symbol}',
                'data': None
            }), 404
    except Exception as e:
        logger.error(f"Error in get_stock_detail for {symbol}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch stock detail: {str(e)}',
            'data': None
        }), 500

@app.route('/api/update-data', methods=['POST'])
def update_stock_data():
    """주식 데이터 업데이트 API"""
    try:
        logger.info("Starting stock data update")
        start_time = time.time()
        
        # 백그라운드에서 데이터 업데이트 실행
        success_count = stock_api.update_all_kospi_data()
        
        end_time = time.time()
        logger.info(f"Stock data update completed in {end_time - start_time:.2f} seconds")
        
        return jsonify({
            'success': True,
            'message': f'Stock data updated successfully. {success_count} companies updated.',
            'updated_count': success_count,
            'total_time': f"{end_time - start_time:.2f}s"
        })
    except Exception as e:
        logger.error(f"Error in update_stock_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to update stock data: {str(e)}',
            'updated_count': 0
        }), 500

@app.route('/api/companies')
def get_companies():
    """등록된 회사 목록 API"""
    try:
        logger.info("Fetching companies list")
        start_time = time.time()
        
        companies = stock_api.db.get_companies()
        companies_list = companies.to_dict('records') if not companies.empty else []
        
        end_time = time.time()
        logger.info(f"Fetched {len(companies_list)} companies in {end_time - start_time:.2f} seconds")
        
        return jsonify({
            'success': True,
            'data': companies_list,
            'count': len(companies_list)
        })
    except Exception as e:
        logger.error(f"Error in get_companies: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch companies: {str(e)}',
            'data': []
        }), 500

@app.route('/api/chart-data/<symbol>')
def get_chart_data(symbol):
    """차트 데이터 API"""
    try:
        days = request.args.get('days', 365, type=int)
        logger.info(f"Fetching chart data for {symbol} (last {days} days)")
        start_time = time.time()
        
        # 일수 제한 (최대 2년)
        days = min(days, 730)
        
        df = stock_api.db.get_stock_prices(symbol, days=days)
        
        if df.empty:
            logger.warning(f"No chart data found for {symbol}")
            return jsonify({
                'success': False,
                'error': f'No data found for {symbol}',
                'data': None
            }), 404
        
        # 날짜 정렬 (오래된 것부터)
        df = df.sort_values('date')
        
        # 차트용 데이터 포맷
        chart_data = {
            'labels': df['date'].astype(str).tolist(),
            'prices': df['close_price'].astype(float).tolist(),
            'volumes': df['volume'].astype(int).tolist()
        }
        
        end_time = time.time()
        logger.info(f"Fetched {len(chart_data['labels'])} data points for {symbol} in {end_time - start_time:.2f} seconds")
        
        return jsonify({
            'success': True,
            'data': chart_data,
            'symbol': symbol,
            'days': days,
            'data_points': len(chart_data['labels'])
        })
    except Exception as e:
        logger.error(f"Error in get_chart_data for {symbol}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch chart data: {str(e)}',
            'data': None
        }), 500

@app.route('/api/health')
def health_check():
    """헬스 체크 API"""
    try:
        # 간단한 데이터베이스 연결 테스트
        companies = stock_api.db.get_companies()
        db_status = "OK" if not companies.empty else "No data"
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': db_status,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port) 