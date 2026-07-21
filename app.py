from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# 設定上傳檔案的暫存目錄
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    # 渲染首頁
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # 1. 接收前端傳來的檔案與選擇的模式
        sim_file = request.files.get('sim_file')
        test_file = request.files.get('test_file')
        mode = request.form.get('mode')

        # 防呆：確認檔案都有傳上來
        if not sim_file or not test_file:
            return jsonify({'status': 'error', 'message': '請確認模擬與實測檔案皆已上傳！'})

        # 2. 將檔案暫存到 uploads 資料夾
        sim_path = os.path.join(app.config['UPLOAD_FOLDER'], sim_file.filename)
        test_path = os.path.join(app.config['UPLOAD_FOLDER'], test_file.filename)
        sim_file.save(sim_path)
        test_file.save(test_path)

        # ---------------------------------------------------------
        # 💡 未來這裡會呼叫 si_math_core.py 的函數來做資料對齊與計算
        # result_data = run_correlation(sim_path, test_path, mode)
        # ---------------------------------------------------------

        # 3. 先回傳成功訊息，測試前後端連線是否正常
        return jsonify({
            'status': 'success',
            'message': f'伺服器已成功接收檔案！準備進行 【{mode}】 模式分析。',
            'data': {
                'sim_filename': sim_file.filename,
                'test_filename': test_file.filename
            }
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'伺服器發生錯誤: {str(e)}'})

if __name__ == '__main__':
    # debug=True 讓你在存檔時，伺服器會自動重新啟動，非常適合開發
    app.run(debug=True, port=5000)