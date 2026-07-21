from flask import Flask, render_template, request, jsonify
import os
# 📍 引入剛剛寫好的數學引擎主函數
from si_math_core import run_correlation 

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
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

        # 儲存檔案
        sim_path = os.path.join(app.config['UPLOAD_FOLDER'], sim_file.filename)
        test_path = os.path.join(app.config['UPLOAD_FOLDER'], test_file.filename)
        sim_file.save(sim_path)
        test_file.save(test_path)

        # 📍 呼叫數學核心引擎進行運算！
        result_data = run_correlation(sim_path, test_path, mode)

        return jsonify({
            'status': 'success',
            'message': '計算完成，圖表渲染中！',
            'chart_data': result_data  # 將算好的座標點傳給前端
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'伺服器運算錯誤: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
