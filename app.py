from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename  # 📍 關鍵新增：用來確保檔名在雲端存檔時不會出錯
from si_math_core import run_correlation 

app = Flask(__name__)

# 📍 關鍵修正：強制使用「絕對路徑」來定位 uploads 資料夾
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        sim_file = request.files.get('sim_file')
        test_file = request.files.get('test_file')
        mode = request.form.get('mode')

        if not sim_file or not test_file:
            return jsonify({'status': 'error', 'message': '請確認模擬與實測檔案皆已上傳！'})

        # 📍 關鍵修正：套用 secure_filename 過濾檔名，並使用絕對路徑存檔
        sim_filename = secure_filename(sim_file.filename)
        test_filename = secure_filename(test_file.filename)
        
        sim_path = os.path.join(app.config['UPLOAD_FOLDER'], sim_filename)
        test_path = os.path.join(app.config['UPLOAD_FOLDER'], test_filename)
        
        sim_file.save(sim_path)
        test_file.save(test_path)

        # 呼叫數學核心引擎進行運算！
        result_data = run_correlation(sim_path, test_path, mode)

        return jsonify({
            'status': 'success',
            'message': '計算完成，圖表渲染中！',
            'chart_data': result_data  # 將算好的座標點傳給前端
        })

    except Exception as e:
        # 這樣如果還有錯，真正的錯誤原因才會顯示在網頁畫面上
        return jsonify({'status': 'error', 'message': f'伺服器運算錯誤: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
