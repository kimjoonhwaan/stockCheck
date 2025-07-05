from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from stock_api import StockAPI

app = Flask(__name__)
CORS(app)

# 전역 변수로 StockAPI 인스턴스 생성
stock_api = StockAPI()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/stocks')
def get_stocks():
    """전체 주식 목록 및 요약 정보 API"""
    try:
        summary = stock_api.get_all_stocks_summary()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stocks/<symbol>')
def get_stock_detail(symbol):
    """특정 주식의 상세 정보 API"""
    try:
        analysis = stock_api.get_stock_analysis(symbol)
        if analysis:
            return jsonify({
                'success': True,
                'data': analysis
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Stock data not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/update-data', methods=['POST'])
def update_stock_data():
    """주식 데이터 업데이트 API"""
    try:
        # 백그라운드에서 데이터 업데이트 실행
        stock_api.update_all_kospi_data()
        return jsonify({
            'success': True,
            'message': 'Stock data updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/companies')
def get_companies():
    """등록된 회사 목록 API"""
    try:
        companies = stock_api.db.get_companies()
        return jsonify({
            'success': True,
            'data': companies.to_dict('records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chart-data/<symbol>')
def get_chart_data(symbol):
    """차트 데이터 API"""
    try:
        days = request.args.get('days', 365, type=int)
        df = stock_api.db.get_stock_prices(symbol, days=days)
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No data found'
            }), 404
        
        # 날짜 정렬 (오래된 것부터)
        df = df.sort_values('date')
        
        # 차트용 데이터 포맷
        chart_data = {
            'labels': df['date'].tolist(),
            'prices': df['close_price'].tolist(),
            'volumes': df['volume'].tolist()
        }
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 