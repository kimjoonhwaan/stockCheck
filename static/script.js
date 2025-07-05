// 전역 변수
let stockChart = null;
let stocksData = [];

// DOM 요소들
const updateBtn = document.getElementById('updateBtn');
const refreshBtn = document.getElementById('refreshBtn');
const statusMessage = document.getElementById('statusMessage');
const stocksGrid = document.getElementById('stocksGrid');
const stockSelect = document.getElementById('stockSelect');
const periodSelect = document.getElementById('periodSelect');
const priceChart = document.getElementById('priceChart');

// 통계 요소들
const totalStocks = document.getElementById('totalStocks');
const positiveStocks = document.getElementById('positiveStocks');
const negativeStocks = document.getElementById('negativeStocks');
const neutralStocks = document.getElementById('neutralStocks');

// 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', function() {
    loadStocksData();
    
    updateBtn.addEventListener('click', updateStockData);
    refreshBtn.addEventListener('click', loadStocksData);
    stockSelect.addEventListener('change', loadChart);
    periodSelect.addEventListener('change', loadChart);
});

// 상태 메시지 표시
function showMessage(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';
    
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 5000);
}

// 로딩 상태 표시
function setLoading(element, isLoading) {
    if (isLoading) {
        element.innerHTML = '<div class="loading"></div>';
        element.disabled = true;
    } else {
        element.disabled = false;
    }
}

// 주식 데이터 로드
async function loadStocksData() {
    try {
        setLoading(refreshBtn, true);
        showMessage('주식 데이터를 불러오는 중...', 'info');
        
        const response = await fetch('/api/stocks');
        const result = await response.json();
        
        if (result.success) {
            stocksData = result.data;
            displayStocks(stocksData);
            updateStatistics(stocksData);
            updateStockSelect(stocksData);
            showMessage('주식 데이터를 성공적으로 불러왔습니다!', 'success');
        } else {
            showMessage(`데이터 로드 실패: ${result.error}`, 'error');
        }
    } catch (error) {
        showMessage(`네트워크 오류: ${error.message}`, 'error');
    } finally {
        setLoading(refreshBtn, false);
    }
}

// 주식 데이터 업데이트
async function updateStockData() {
    try {
        setLoading(updateBtn, true);
        showMessage('주식 데이터를 업데이트하는 중... (약 1-2분 소요)', 'info');
        
        const response = await fetch('/api/update-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('주식 데이터 업데이트가 완료되었습니다!', 'success');
            // 업데이트 후 데이터 다시 로드
            setTimeout(() => {
                loadStocksData();
            }, 1000);
        } else {
            showMessage(`업데이트 실패: ${result.error}`, 'error');
        }
    } catch (error) {
        showMessage(`네트워크 오류: ${error.message}`, 'error');
    } finally {
        setLoading(updateBtn, false);
    }
}

// 주식 목록 표시
function displayStocks(stocks) {
    if (!stocks || stocks.length === 0) {
        stocksGrid.innerHTML = '<p>주식 데이터가 없습니다. 데이터 업데이트를 해주세요.</p>';
        return;
    }
    
    stocksGrid.innerHTML = stocks.map(stock => {
        const changeClass = stock.year_return > 0 ? 'positive' : 
                           stock.year_return < 0 ? 'negative' : 'neutral';
        const changeSymbol = stock.year_return > 0 ? '+' : '';
        
        return `
            <div class="stock-card ${changeClass} fade-in" data-symbol="${stock.symbol}">
                <div class="stock-name">${stock.name}</div>
                <div class="stock-symbol">${stock.symbol}</div>
                <div class="stock-price">${formatPrice(stock.current_price)}</div>
                <div class="stock-change ${changeClass}">
                    ${changeSymbol}${stock.year_return.toFixed(2)}% (1년)
                </div>
                <div class="stock-range">
                    High: ${formatPrice(stock.year_high)} | Low: ${formatPrice(stock.year_low)}
                </div>
            </div>
        `;
    }).join('');
    
    // 주식 카드 클릭 이벤트
    document.querySelectorAll('.stock-card').forEach(card => {
        card.addEventListener('click', () => {
            const symbol = card.dataset.symbol;
            stockSelect.value = symbol;
            loadChart();
        });
    });
}

// 통계 업데이트
function updateStatistics(stocks) {
    if (!stocks || stocks.length === 0) {
        totalStocks.textContent = '0';
        positiveStocks.textContent = '0';
        negativeStocks.textContent = '0';
        neutralStocks.textContent = '0';
        return;
    }
    
    const total = stocks.length;
    const positive = stocks.filter(s => s.year_return > 0).length;
    const negative = stocks.filter(s => s.year_return < 0).length;
    const neutral = stocks.filter(s => s.year_return === 0).length;
    
    totalStocks.textContent = total;
    positiveStocks.textContent = positive;
    negativeStocks.textContent = negative;
    neutralStocks.textContent = neutral;
}

// 주식 선택 드롭다운 업데이트
function updateStockSelect(stocks) {
    const options = stocks.map(stock => 
        `<option value="${stock.symbol}">${stock.name} (${stock.symbol})</option>`
    ).join('');
    
    stockSelect.innerHTML = '<option value="">주식을 선택하세요</option>' + options;
}

// 차트 로드
async function loadChart() {
    const symbol = stockSelect.value;
    const days = periodSelect.value;
    
    if (!symbol) {
        if (stockChart) {
            stockChart.destroy();
            stockChart = null;
        }
        return;
    }
    
    try {
        showMessage('차트 데이터를 불러오는 중...', 'info');
        
        const response = await fetch(`/api/chart-data/${symbol}?days=${days}`);
        const result = await response.json();
        
        if (result.success) {
            displayChart(result.data);
            showMessage('차트를 성공적으로 불러왔습니다!', 'success');
        } else {
            showMessage(`차트 로드 실패: ${result.error}`, 'error');
        }
    } catch (error) {
        showMessage(`네트워크 오류: ${error.message}`, 'error');
    }
}

// 차트 표시
function displayChart(data) {
    const ctx = priceChart.getContext('2d');
    
    // 기존 차트 제거
    if (stockChart) {
        stockChart.destroy();
    }
    
    // 새 차트 생성
    stockChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: '종가',
                data: data.prices,
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '주가 변동 차트'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: '날짜'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: '가격 (원)'
                    }
                }
            },
            elements: {
                point: {
                    radius: 1,
                    hoverRadius: 5
                }
            }
        }
    });
}

// 가격 포맷팅
function formatPrice(price) {
    if (price === null || price === undefined) return 'N/A';
    
    return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(price);
}

// 숫자 포맷팅
function formatNumber(num) {
    if (num === null || num === undefined) return 'N/A';
    
    return new Intl.NumberFormat('ko-KR').format(num);
}

// 페이지 언로드 시 차트 정리
window.addEventListener('beforeunload', () => {
    if (stockChart) {
        stockChart.destroy();
    }
}); 