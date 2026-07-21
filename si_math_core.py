import numpy as np
import pandas as pd
import skrf as rf
from scipy.interpolate import interp1d

def read_test_il(file_path, target_pair="P1TX1_P2RX1"):
    """讀取 VNA 測試檔案的 Insertion Loss"""
    df = pd.read_excel(file_path, sheet_name='IL', skiprows=1)
    df.columns = [str(c).strip() for c in df.columns]
    freq_ghz = df.iloc[:, 0].values / 1000.0
    
    # 防呆：如果找不到預設的差分對，就抓檔案裡的第一對資料
    if target_pair not in df.columns:
        target_pair = df.columns[1] 
        
    db_values = df[target_pair].values
    return freq_ghz, db_values

def read_sim_il(file_path, port_i=1, port_j=0):
    """讀取 CST 模擬的 Touchstone 檔案"""
    net = rf.Network(file_path)
    freq_ghz = net.f / 1e9 
    db_values = net.s_db[:, port_i, port_j]
    return freq_ghz, db_values

def align_and_calculate_error(freq_sim, db_sim, freq_test, db_test):
    """進行內插對齊與計算誤差"""
    if len(freq_sim) < len(freq_test):
        x_base = freq_sim
        y_sim_aligned = db_sim
        f_interp = interp1d(freq_test, db_test, kind='linear', bounds_error=False, fill_value=np.nan)
        y_test_aligned = f_interp(x_base)
    else:
        x_base = freq_test
        y_test_aligned = db_test
        f_interp = interp1d(freq_sim, db_sim, kind='linear', bounds_error=False, fill_value=np.nan)
        y_sim_aligned = f_interp(x_base)

    delta_db = np.abs(y_test_aligned - y_sim_aligned)
    return x_base, y_sim_aligned, y_test_aligned, delta_db

def clean_array(arr):
    """將 Numpy 陣列轉為 Python List，並將 NaN 轉為 None 以符合 JSON 格式"""
    return [None if np.isnan(x) else float(x) for x in arr]

def run_correlation(sim_path, test_path, mode="IL"):
    """前端呼叫的主函數：負責統籌資料流與打包"""
    if mode == "IL":
        # 1. 讀取資料
        freq_test, db_test = read_test_il(test_path)
        freq_sim, db_sim = read_sim_il(sim_path)
        
        # 2. 對齊與計算
        x_base, y_sim, y_test, delta_db = align_and_calculate_error(freq_sim, db_sim, freq_test, db_test)
        
        # 3. 打包成 JSON 字典
        return {
            "x_freq": clean_array(x_base),
            "y_sim": clean_array(y_sim),
            "y_test": clean_array(y_test),
            "delta": clean_array(delta_db),
            "title": "Insertion Loss (Sdd21) 模擬與實測比對",
            "x_title": "Frequency (GHz)",
            "y_title": "Magnitude (dB)"
        }
    else:
        # TDR 功能預留擴充
        raise NotImplementedError(f"模式 {mode} 正在開發中，請先測試 IL 模式！")
