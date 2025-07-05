import os
from app import app

# Render는 gunicorn이 이 파일을 직접 import하므로 
# if __name__ == "__main__" 블록이 필요하지 않습니다.

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 