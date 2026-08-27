import json  # 匯入處理 JSON 檔案格式的工具箱
import numpy as np  # 匯入數字與數學計算工具箱，簡稱為 np
import pandas as pd  # 匯入表格資料處理工具箱，簡稱為 pd
import plotly.graph_objects as go  # 匯入繪製互動圖表工具箱，簡稱為 go
import streamlit as st  # 匯入建立網頁介面工具箱，簡稱為 st

# 設定網頁標題與版面
st.set_page_config(  # 呼叫 Streamlit 網頁設定函式
    page_title="Retirement Planning System",  # 設定瀏覽器標題
    layout="wide",  # 設定網頁版面為寬螢幕模式
    initial_sidebar_state="expanded",  # 設定側邊欄預設為展開
)  # 結束網頁設定

# 自訂網頁 CSS 樣式，強化卡片質感與閱讀體驗
st.markdown(  # 插入網頁美化樣式
    """
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.1rem; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.2rem; }
    .stNumberInput input { font-weight: 600; }
</style>
""",  # CSS 樣式碼定義
    unsafe_allow_html=True,  # 允許套用 HTML/CSS 語法
)  # 結束樣式設定


# 自訂雙向輸入元件：結合數字輸入框與滑桿
def dual_input(  # 定義 dual_input 函式
    label,  # 標題名稱
    key_prefix,  # 記憶體獨一無二金鑰前綴
    min_value,  # 最小值
    max_value,  # 最大值
    default_val,  # 預設值
    step=1,  # 加減步階
    format_fmt=None,  # 數字格式化字串
    help_text=None,  # 說明提示
):  # 函式開頭
  st.markdown(f"**{label}**")  # 顯示粗體標題文字
  val_key = f"{key_prefix}_val"  # 數值變數名稱
  num_key = f"{key_prefix}_num"  # 輸入框控制名稱
  slider_key = f"{key_prefix}_slider"  # 滑桿控制名稱

  if val_key not in st.session_state:  # 若記憶體中無此數值
    st.session_state[val_key] = default_val  # 寫入預設值

  if num_key not in st.session_state:  # 若無輸入框狀態
    st.session_state[num_key] = st.session_state[val_key]  # 同步為目前數值
  if slider_key not in st.session_state:  # 若無滑桿狀態
    st.session_state[slider_key] = st.session_state[val_key]  # 同步為目前數值

  def sync_from_num():  # 輸入框變動時觸發的同步函式
    st.session_state[val_key] = st.session_state[num_key]  # 更新數值
    st.session_state[slider_key] = st.session_state[num_key]  # 移動滑桿

  def sync_from_slider():  # 滑桿變動時觸發的同步函式
    st.session_state[val_key] = st.session_state[slider_key]  # 更新數值
    st.session_state[num_key] = st.session_state[slider_key]  # 更新輸入框

  col1, col2 = st.columns([1, 1])  # 切分為左右兩等分欄位
  with col1:  # 左側欄位
    st.number_input(  # 建立數字輸入框
        label="數字輸入",  # 標題
        min_value=min_value,  # 最小值
        max_value=max_value,  # 最大值
        step=step,  # 步階
        format=format_fmt,  # 格式
        key=num_key,  # 控制金鑰
        on_change=sync_from_num,  # 觸發同步
        label_visibility="collapsed",  # 隱藏標題
        help=help_text,  # 說明文字
    )  # 結束輸入框
  with col2:  # 右側欄位
    st.slider(  # 建立滑桿
        label="滑桿調整",  # 標題
        min_value=min_value,  # 最小值
        max_value=max_value,  # 最大值
        step=step,  # 步階
        key=slider_key,  # 控制金鑰
        on_change=sync_from_slider,  # 觸發同步
        label_visibility="collapsed",  # 隱藏標題
    )  # 結束滑桿
  return st.session_state[val_key]  # 回傳最終選定的數值


# 台灣勞退投保薪資級距清單
LABOR_PENSION_LEVELS = [  # 建立金額清單
    15000,
    15840,
    16500,
    17280,
    17880,
    19047,
    20008,
    21009,  # 級距清單 1
    22000,
    23100,
    24000,
    25250,
    26400,
    27600,
    28800,  # 級距清單 2
    30300,
    31800,
    33300,
    34800,
    36300,
    38200,
    40100,  # 級距清單 3
    42000,
    43900,
    45800,
    48200,
    50600,
    53000,
    55400,  # 級距清單 4
    57800,
    60800,
    63800,
    66800,
    69800,
    72800,
    76500,  # 級距清單 5
    80200,
    83900,
    87600,
    92100,
    96600,
    101100,  # 級距清單 6
    105600,
    110100,
    115500,
    120900,
    126300,
    131100,  # 級距清單 7
    137100,
    142500,
    147900,
    150000,  # 最高投保級距
]  # 清單設定結束


def get_labor_pension_level(salary):  # 查詢勞退投保級距函式
  for lvl in LABOR_PENSION_LEVELS:  # 依序比對金額
    if salary <= lvl:  # 若低於或等於該級距
      return lvl  # 回傳該級距
  return LABOR_PENSION_LEVELS[-1]  # 超過上限則回傳最高級距


# 預設個人參數字典 (已加入 pre_retire_annual_expense)
DEFAULT_PROFILES = {  # 建立母字典
    "夫": {  # 丈夫參數
        "current_age": 30,  # 目前年齡
        "retire_age": 55,  # 退休年齡
        "labor_pension_claim_age": 60,  # 勞退請領年齡
        "labor_ins_claim_age": 60,  # 勞保請領年齡
        "labor_pension_balance": 500000,  # 目前勞退餘額
        "insured_salary": 45800,  # 月投保薪資
        "salary_growth_rate": 2.0,  # 薪資成長率%
        "labor_pension_rate": 12.0,  # 勞退提撥率%
        "labor_pension_return": 7.64,  # 提領前：勞退基金報酬率%
        "labor_pension_reinvest_return": 5.0,  # 提領後：轉投資報酬率%
        "stock_balance": 4000000,  # 目前股票總額
        "stock_monthly": 35000,  # 每月股票投入
        "stock_return": 6.0,  # 股票年報酬率%
        "cash_balance": 2000000,  # 目前備用金總額
        "cash_monthly": 12000,  # 每月備用金存入
        "cash_return": 2.0,  # 備用金年利率%
        "labor_ins_years": 10,  # 目前勞保年資
        "labor_ins_salary": 45800,  # 勞保最高薪資
        "pre_retire_annual_expense": 100000,  # 🆕 退休前每年享樂/彈性支出 (旅遊、買包等)
        "post_retire_expense": 100000,  # 退休後每月生活費
        "drawdown_priority": ["備用金", "股票", "勞退金額"],  # 扣款順序
    },  # 丈夫參數結束
    "妻": {  # 妻子參數
        "current_age": 30,  # 目前年齡
        "retire_age": 55,  # 退休年齡
        "labor_pension_claim_age": 60,  # 勞退請領年齡
        "labor_ins_claim_age": 60,  # 勞保請領年齡
        "labor_pension_balance": 500000,  # 目前勞退餘額
        "insured_salary": 55400,  # 月投保薪資
        "salary_growth_rate": 2.0,  # 薪資成長率%
        "labor_pension_rate": 12.0,  # 勞退提撥率%
        "labor_pension_return": 7.64,  # 提領前：勞退基金報酬率%
        "labor_pension_reinvest_return": 5.0,  # 提領後：轉投資報酬率%
        "stock_balance": 2500000,  # 目前股票總額
        "stock_monthly": 20000,  # 每月股票投入
        "stock_return": 6.0,  # 股票年報酬率%
        "cash_balance": 1500000,  # 目前備用金總額
        "cash_monthly": 8000,  # 每月備用金存入
        "cash_return": 2.0,  # 備用金年利率%
        "labor_ins_years": 10,  # 目前勞保年資
        "labor_ins_salary": 45800,  # 勞保最高薪資
        "pre_retire_annual_expense": 100000,  # 🆕 退休前每年享樂/彈性支出
        "post_retire_expense": 40000,  # 退休後每月生活費
        "drawdown_priority": ["備用金", "股票", "勞退金額"],  # 扣款順序
    },  # 妻子參數結束
}  # 字典設定結束


def calc_labor_ins_annuity(
    avg_salary, total_years, claim_age
):  # 計算勞保老年年金函式
  base_monthly = avg_salary * total_years * 0.0155  # 計算每月基本年金金額
  diff_years = claim_age - 65  # 計算與標準 65 歲相差年數
  adj_factor = max(
      0.6, min(1.2, 1.0 + (diff_years * 0.04))
  )  # 展延加成或提前減額比例
  return base_monthly * adj_factor  # 回傳調整後月領年金金額


def run_initial_simulation(p):  # 建立基礎試算明細表格函式
  end_age = 85  # 設定試算預設終點為 85 歲
  records = []  # 建立空清單準備存放逐年資料
  cur_salary = p["insured_salary"]  # 設定初始月投保薪資

  for age in range(p["current_age"], end_age + 1):  # 從目前年齡計算至 85 歲
    is_working = age < p["retire_age"]  # 判斷該年齡是否為工作期間
    status = "工作中" if is_working else "已退休"  # 設定文字狀態

    if is_working and age > p["current_age"]:  # 工作期間且非第一年
      cur_salary = cur_salary * (
          1 + p["salary_growth_rate"] / 100.0
      )  # 按年成長率調升薪資

    cur_level = get_labor_pension_level(cur_salary)  # 對應取得勞退投保級距金額

    # 判斷工作期與退休期的開銷設定
    if is_working:  # 若為工作中
      pension_rate = p["labor_pension_rate"]  # 採用預設提撥率
      stock_m = p["stock_monthly"]  # 採用預設股票月投入
      cash_m = p["cash_monthly"]  # 採用預設備用金月投入
      expense = 0  # 工作期未產生退休生活費支出
      extra_exp = p.get(
          "pre_retire_annual_expense", 100000
      )  # 🆕 退休前的每年彈性/享樂支出
      extra_note = "退休前年度享樂/旅遊開銷"  # 預設備註
    else:  # 若為已退休
      pension_rate = 0.0  # 停止提撥勞退
      stock_m = 0  # 停止投入股票
      cash_m = 0  # 停止存入備用金
      expense = p["post_retire_expense"]  # 讀取退休月生活費
      extra_exp = 0  # 退休後預設無大額支出 (可在表格手動填寫)
      extra_note = ""

    labor_ins_annuity_monthly = 0  # 預設勞保年金為 0
    if age >= p["labor_ins_claim_age"]:  # 達到勞保請領年齡
      service_years = p["labor_ins_years"] + max(
          0, p["retire_age"] - p["current_age"]
      )  # 估算總累積年資
      labor_ins_annuity_monthly = calc_labor_ins_annuity(  # 計算勞保月領金額
          p["labor_ins_salary"], service_years, p["labor_ins_claim_age"]
      )  # 代入公式

    eff_pension_ret = (  # 計算勞退當期報酬率
        p["labor_pension_return"]  # 請領前使用勞退基金報酬率
        if age < p["labor_pension_claim_age"]
        else p["labor_pension_reinvest_return"]  # 請領後使用轉投資報酬率
    )  # 條件成立選擇

    records.append({  # 將年度資料寫入字典打包加入清單
        "年齡": age,  # 年齡
        "狀態": status,  # 狀態
        "投保級距": round(cur_level),  # 投保級距
        "當期提撥率(%)": pension_rate,  # 提撥率
        "勞退當期報酬率(%)": eff_pension_ret,  # 勞退報酬率
        "股票每月投入": stock_m,  # 股票月投入
        "當期股票報酬率(%)": p["stock_return"],  # 股票報酬率
        "備用金每月投入(含年金併入)": round(
            cash_m + labor_ins_annuity_monthly
        ),  # 現金投入+年金
        "備用金報酬率(%)": p["cash_return"],  # 現金報酬率
        "退休月生活費": expense,  # 退休月生活費
        "當頁額外大額支出 (元)": extra_exp,  # 🆕 自動帶入退休前彈性開銷
        "大額支出備註/用途": extra_note,  # 🆕 備註說明
        "累計勞退金額": 0,  # 累計金額預設 0
        "累計股票金額": 0,  # 累計金額預設 0
        "累計備用金": 0,  # 累計金額預設 0
        "累計總資產": 0,  # 累計金額預設 0
    })  # 打包結束
  return pd.DataFrame(records)  # 轉為 Pandas Dataframe 回傳


def recalculate_dataframe(df, p):  # 動態計算利息與扣除支出之引擎函式
  cur_pension = p["labor_pension_balance"]  # 初始勞退金額
  cur_stock = p["stock_balance"]  # 初始股票金額
  cur_cash = p["cash_balance"]  # 初始備用金金額

  updated_rows = []  # 存放重算後的資料列
  priority = p.get(
      "drawdown_priority", ["備用金", "股票", "勞退金額"]
  )  # 讀取資產扣款優先順序
  claim_age = p.get("labor_pension_claim_age", 60)  # 讀取勞退請領年齡

  for _, row in df.iterrows():  # 逐列計算資產滾動
    age = int(row["年齡"])  # 取得年齡
    level = float(row["投保級距"])  # 取得級距
    pension_rate = float(row["當期提撥率(%)"])  # 取得提撥率
    pension_ret = float(row["勞退當期報酬率(%)"])  # 取得勞退報酬率
    stock_m = float(row["股票每月投入"])  # 股票投入
    stock_ret = float(row["當期股票報酬率(%)"])  # 股票報酬率
    cash_m = float(row["備用金每月投入(含年金併入)"])  # 現金投入
    cash_ret = float(row["備用金報酬率(%)"])  # 現金報酬率
    monthly_expense = float(row["退休月生活費"])  # 月生活費
    extra_expense = float(row.get("當頁額外大額支出 (元)", 0))  # 大額支出/彈性開銷

    # 1. 勞退金額累積計算
    pension_contrib = level * (pension_rate / 100.0) * 12  # 年提撥金額
    cur_pension = (cur_pension + pension_contrib) * (
        1 + pension_ret / 100.0
    )  # 利滾利計算

    # 2. 支出扣算 (包含退休後月生活費 + 退休前/後的大額與彈性支出)
    tot_annual_draw = (monthly_expense * 12) + extra_expense  # 年度總花費
    if tot_annual_draw > 0:  # 需要扣花費時
      rem_expense = tot_annual_draw  # 待扣剩餘額度
      for source in priority:  # 按優先順序扣款
        if rem_expense <= 0:  # 已扣完則跳出
          break  # 中斷迴圈
        if source == "備用金":  # 優先扣備用金
          draw = min(cur_cash, rem_expense)  # 取可扣金額
          cur_cash -= draw  # 扣減備用金
          rem_expense -= draw  # 減少待扣額
        elif source == "股票":  # 優先扣股票
          draw = min(cur_stock, rem_expense)  # 取可扣金額
          cur_stock -= draw  # 扣減股票
          rem_expense -= draw  # 減少待扣額
        elif source == "勞退金額":  # 優先扣勞退
          if age >= claim_age:  # 達請領年齡方可動用
            draw = min(cur_pension, rem_expense)  # 取可扣金額
            cur_pension -= draw  # 扣減勞退
            rem_expense -= draw  # 減少待扣額

    # 3. 股票與備用金累積利息計算
    cur_stock = (cur_stock + stock_m * 12) * (
        1 + stock_ret / 100.0
    )  # 股票複利成長
    cur_cash = (cur_cash + cash_m * 12) * (
        1 + cash_ret / 100.0
    )  # 備用金複利成長
    tot_asset = cur_pension + cur_stock + cur_cash  # 計算當年度總資產

    row_dict = row.to_dict()  # 轉為字典
    row_dict["累計勞退金額"] = round(cur_pension)  # 寫入勞退金額
    row_dict["累計股票金額"] = round(cur_stock)  # 寫入股票金額
    row_dict["累計備用金"] = round(cur_cash)  # 寫入備用金金額
    row_dict["累計總資產"] = round(tot_asset)  # 寫入總資產金額
    updated_rows.append(row_dict)  # 加入結果清單

  return pd.DataFrame(updated_rows)  # 回傳更新後表格


# 頁面主標題區
st.markdown(
    '<div class="main-header">Retirement Planning System</div>',
    unsafe_allow_html=True,
)  # 顯示白話標題
st.markdown(
    '<div'
    ' class="sub-header">present by Wayne SHIH</div>',
    unsafe_allow_html=True,
)  # 顯示簡潔說明文字

# 側邊欄設定
st.sidebar.header("⚙️ 模式與檔案管理")  # 側邊欄區塊標題
calc_mode = st.sidebar.radio(
    "選擇計算模式", ["個人獨立規劃", "夫妻共同規劃"]
)  # 計算模式選擇

st.sidebar.subheader("💾 儲存/讀取評估方案")  # 側邊欄子標題
scenario_name = st.sidebar.text_input("方案名稱", "預設規劃案")  # 輸入框：方案名稱

if "user_profiles" not in st.session_state:  # 初始化使用者設定
  st.session_state["user_profiles"] = DEFAULT_PROFILES.copy()  # 載入預設設定

if "uploader_key" not in st.session_state:  # 初始化上傳控制編號
  st.session_state["uploader_key"] = 0  # 預設編號為 0


def load_json_callback():  # JSON 讀取自動執行函式
  uploader_file = st.session_state.get(
      f"json_uploader_{st.session_state['uploader_key']}"
  )  # 取得上傳檔案
  if uploader_file is not None:  # 若有檔案
    try:  # 嘗試解析
      loaded_data = json.load(uploader_file)  # 解析 JSON
      if "profiles" in loaded_data:  # 若含 profiles
        st.session_state["user_profiles"] = loaded_data[
            "profiles"
        ]  # 覆蓋設定
      else:  # 若舊版本
        st.session_state["user_profiles"] = loaded_data  # 覆蓋設定

      keys_to_clear = [  # 整理需清除的控制金鑰
          k
          for k in list(st.session_state.keys())
          if k.endswith("_val")
          or k.endswith("_num")
          or k.endswith("_slider")
          or k.endswith("_drawdown_prio")
          or k.startswith("df_")
          or k.startswith("hash_")
          or k.startswith("editor_")
      ]  # 比對規則選出
      for k in keys_to_clear:  # 巡迴清除
        del st.session_state[k]  # 刪除舊金鑰

      if "details" in loaded_data:  # 若含有明細資料
        for p_key, df_dict in loaded_data["details"].items():  # 巡迴人物
          st.session_state[f"df_{p_key}"] = pd.DataFrame(
              df_dict
          )  # 還原 Dataframe
          if p_key in st.session_state["user_profiles"]:  # 同步更新雜湊標籤
            st.session_state[f"hash_{p_key}"] = json.dumps(
                st.session_state["user_profiles"][p_key], sort_keys=True
            )  # 更新雜湊

      st.session_state["uploader_key"] += 1  # 上傳編號加 1
      st.session_state["load_success_msg"] = (
          "✅ 成功載入方案！"  # 設定成功提示
      )
    except Exception as e:  # 發生例外錯誤
      st.session_state["load_error_msg"] = (
          f"❌ 載入失敗：{e}"  # 設定失敗提示
      )


def prepare_export_json():  # 打包 JSON 下載資料函式
  export_details = {}  # 明細字典
  for k in list(st.session_state.keys()):  # 尋找 df_ 開頭內容
    if k.startswith("df_"):  # 判斷開頭
      p_key = k.replace("df_", "")  # 取得人物關鍵字
      export_details[p_key] = st.session_state[k].to_dict(
          orient="records"
      )  # 轉字典清單
  full_package = {  # 總打包物件
      "profiles": st.session_state["user_profiles"],  # 個人設定
      "details": export_details,  # 明細內容
  }  # 打包結束
  return json.dumps(
      full_package, ensure_ascii=False, indent=2
  )  # 轉為格式化 JSON 字串


st.sidebar.download_button(  # 側邊欄下載按鈕
    label="📥 下載 JSON 設定檔",  # 按鈕標題
    data=prepare_export_json(),  # 資料來源
    file_name=f"{scenario_name}_退休規劃.json",  # 預設檔名
    mime="application/json",  # 檔案類型
)  # 按鈕設定結束

st.sidebar.file_uploader(  # 側邊欄上傳元件
    "📤 讀取已存方案 (JSON)",  # 說明標題
    type=["json"],  # 限制格式
    key=f"json_uploader_{st.session_state['uploader_key']}",  # 金鑰
    on_change=load_json_callback,  # 上傳觸發函式
)  # 上傳元件設定結束

if "load_success_msg" in st.session_state:  # 成功訊息顯示判斷
  st.sidebar.success(
      st.session_state.pop("load_success_msg")
  )  # 顯示綠色成功框
if "load_error_msg" in st.session_state:  # 失敗訊息顯示判斷
  st.sidebar.error(st.session_state.pop("load_error_msg"))  # 顯示紅色錯誤框

profiles_to_calc = (
    ["個人"] if calc_mode == "個人獨立規劃" else ["夫", "妻"]
)  # 判斷需計算幾個人物

# 🌟 UI 改善亮點 1：預估年報酬率與歷史參考數據指引 (Guidance & Custom Return Rates)
st.markdown("### 步驟 1：填寫預估年報酬率 (附歷史數據參考)")  # 大步驟標題

# 歷史數據引導展開區塊
with st.expander(
    "📊 點此查看【歷史參考年化報酬率數據】(0050、台幣定存、勞退基金)",
    expanded=False,
):  # 歷史指引展開區塊
  ref_col1, ref_col2, ref_col3 = st.columns(3)  # 切為三欄指引卡片

  with ref_col1:  # 股票指引卡片
    st.markdown("#### 0050 年化報酬率(至2025年底)")  # 卡片小標題
    st.markdown("""
        * **創立至今** (2003~2025)：**12.62% ~ 13.11%**
        * **近 20 年**：**11.56% ~ 12.04%**
        * **近 10 年**：**21.79%**
        * **近 5 年**：**20.99%**
        * **近 1 年**：**37.13%**
        """)  # 顯示歷史報酬率資料

  with ref_col2:  # 備用金指引卡片
    st.markdown("#### 台幣定存利率(近年統計)")  # 卡片小標題
    st.markdown("""
        * **近 20 年平均**：**2.10%**
        * **近 10 年平均**：**1.15%**
        * **近 5 年平均**：**0.80%**
        * **近 1 年平均**：**1.72%**
        """)  # 顯示定存歷史利率資料

  with ref_col3:  # 勞退基金指引卡片
    st.markdown("#### 勞退基金歷史報酬率")  # 卡片小標題
    st.markdown("""
        * **成立迄今**：**7.64%**
        * **近十年**：**8.70%**
        * **近五年**：**10.28%**
        * **近三年**：**14.91%**
        * **近一年**：**15.60%**
        """)  # 顯示勞退歷史數據

st.markdown("#### 請填寫您預估的各項年報酬率 (%)：")  # 子標題

# 依據角色設定 4 大年報酬率
rate_tabs = st.tabs(
    [f"👤 {p_name} 的報酬率設定" for p_name in profiles_to_calc]
)  # 為每位角色建立頁籤

for idx, p_name in enumerate(profiles_to_calc):  # 逐一處理角色設定
  with rate_tabs[idx]:  # 切換至角色頁籤
    if p_name not in st.session_state["user_profiles"]:  # 若字典無資料
      st.session_state["user_profiles"][p_name] = DEFAULT_PROFILES[
          "夫"
      ].copy()  # 初始化初值
    p_target = st.session_state["user_profiles"][p_name]  # 取得個人字典引用

    r_col1, r_col2 = st.columns(2)  # 將 4 個輸入欄位切為兩欄
    with r_col1:  # 左欄
      p_target["stock_return"] = dual_input(  # 輸入股票預估年報酬率
          "股票預估年報酬率 (%)",
          f"{p_name}_ret_stock",
          0.0,
          30.0,
          p_target.get("stock_return", 6.0),
          step=0.1,
          format_fmt="%.1f",
          help_text="參考 0050 創立至今約 12.6%，長期保守預估建議填寫 6%~8%",
      )  # 綁定參數
      p_target["labor_pension_return"] = dual_input(  # 輸入提領前勞退報酬率
          "提領前：勞退基金預估年報酬率 (%)",
          f"{p_name}_ret_lp_pre",
          0.0,
          20.0,
          p_target.get("labor_pension_return", 7.64),
          step=0.1,
          format_fmt="%.1f",
          help_text="參考勞退基金成立迄今約 7.64%",
      )  # 綁定參數

    with r_col2:  # 右欄
      p_target["cash_return"] = dual_input(  # 輸入備用金預估年報酬率
          "備用金/定存預估年報酬率 (%)",
          f"{p_name}_ret_cash",
          0.0,
          10.0,
          p_target.get("cash_return", 2.0),
          step=0.1,
          format_fmt="%.1f",
          help_text="參考台幣定存近 20 年約 2.1%",
      )  # 綁定參數
      p_target["labor_pension_reinvest_return"] = dual_input(  # 輸入提領後轉投資報酬率
          "提領後：一次請領帳戶投資年報酬率 (%)",
          f"{p_name}_ret_lp_post",
          0.0,
          20.0,
          p_target.get("labor_pension_reinvest_return", 5.0),
          step=0.1,
          format_fmt="%.1f",
          help_text="60歲請領勞退金後，自行轉入低風險資產（如債券/高股息）的預期報酬",
      )  # 綁定參數

# 🌟 UI 改善亮點 2：簡化的參數輸入介面 (含新功能：退休前享樂/旅遊支出)
st.markdown("---")  # 水平分割線
st.markdown("### 步驟 2：輸入您的個人基本狀況")  # 大步驟標題
tab_list = st.tabs(
    [f"👤 {p_name} 的資料設定" for p_name in profiles_to_calc]
)  # 建立人物分頁 (Tabs)

sim_results = {}  # 存放最終結果字典

for idx, p_name in enumerate(profiles_to_calc):  # 逐一處理分頁
  with tab_list[idx]:  # 進入分頁
    p = st.session_state["user_profiles"][p_name]  # 取得個人參數字典

    # 基礎核心參數 (直接呈現，保持畫面乾淨)
    col_c1, col_c2 = st.columns(2)  # 將核心輸入切為左右兩欄
    with col_c1:  # 左側基本資料
      st.markdown("#### 1. 年齡與月薪資")  # 區塊小標題
      p["current_age"] = dual_input(  # 輸入目前年齡
          "您目前的年齡 (歲)", f"{p_name}_cur_age", 20, 70, p.get("current_age", 30)
      )  # 設定綁定
      p["retire_age"] = dual_input(  # 輸入預計退休年齡
          "預計幾歲停止工作/退休？",
          f"{p_name}_ret_age",
          40,
          75,
          p.get("retire_age", 55),
      )  # 設定綁定
      p["insured_salary"] = dual_input(  # 輸入月薪投保級距
          "目前每月投保薪資 (元)",
          f"{p_name}_ins_sal",
          15000,
          150000,
          p.get("insured_salary", 45800),
          step=1000,
      )  # 設定綁定

    with col_c2:  # 右側每月儲蓄與收支期待
      st.markdown("#### 2. 每月投資與生活支出預算")  # 區塊小標題
      p["stock_monthly"] = dual_input(  # 每月定期定額買股票
          "每月定期定額買股票/基金 (元)",
          f"{p_name}_stk_m",
          0,
          1000000,
          p.get("stock_monthly", 35000),
          step=1000,
      )  # 設定綁定
      p["cash_monthly"] = dual_input(  # 每月存備用金
          "每月存入備用金/定存 (元)",
          f"{p_name}_csh_m",
          0,
          1000000,
          p.get("cash_monthly", 12000),
          step=1000,
      )  # 設定綁定

      # 🆕 新增：退休前每年享樂/旅遊/購物開銷
      p["pre_retire_annual_expense"] = dual_input(
          "退休前預計【每年】享樂/旅遊/彈性支出 (元)",
          f"{p_name}_pre_exp",
          0,
          2000000,
          p.get("pre_retire_annual_expense", 100000),
          step=10000,
          help_text=(
              "包含每年出國旅遊、買包包精品、送禮等非日常固定開銷。此金額會在退休前的每年自動自備用金/資產中扣除。"
          ),
      )

      p["post_retire_expense"] = dual_input(  # 退休後月生活費
          "退休後希望【每月】有多少生活費？ (元)",
          f"{p_name}_exp",
          10000,
          1000000,
          p.get("post_retire_expense", 100000),
          step=2000,
      )  # 設定綁定

    # 🌟 UI 改善亮點 3：漸進式揭露 (Progressive Disclosure) - 隱藏專業/複雜設定
    with st.expander(
        "⚙️ 點此展開【進階詳細設定】(現有存款金額、勞保年資與扣款順序)",
        expanded=False,
    ):  # 折疊選單
      st.info(
          "提示：勞退個人專戶與投保年資可上勞保局網站查詢及試算。"
      )  # 提示說明框
      ex_col1, ex_col2 = st.columns(2)  # 將折疊選單切為左右兩欄
      with ex_col1:  # 左側進階參數
        st.markdown("##### 💰 目前已累積的資產餘額")  # 小標題
        p["labor_pension_balance"] = dual_input(  # 勞退帳戶餘額
            "勞退個人專戶目前累積金額 (元)",
            f"{p_name}_lp_bal",
            0,
            20000000,
            p.get("labor_pension_balance", 500000),
            step=10000,
        )  # 綁定參數
        p["stock_balance"] = dual_input(  # 股票已累積金額
            "目前股票/基金總價值 (元)",
            f"{p_name}_stk_bal",
            0,
            100000000,
            p.get("stock_balance", 4000000),
            step=50000,
        )  # 綁定參數
        p["cash_balance"] = dual_input(  # 備用金已累積金額
            "目前備用金/定存總額 (元)",
            f"{p_name}_csh_bal",
            0,
            100000000,
            p.get("cash_balance", 2000000),
            step=50000,
        )  # 綁定參數

      with ex_col2:  # 右側進階參數
        st.markdown("##### 🛡️ 勞保與提撥率細節")  # 小標題
        p["labor_ins_years"] = dual_input(  # 勞保累積年資
            "目前勞保已投保年資 (年)",
            f"{p_name}_li_yrs",
            0,
            40,
            p.get("labor_ins_years", 10),
        )  # 綁定參數
        p["labor_ins_salary"] = dual_input(  # 勞保最高投保薪資
            "勞保最高 60 個月平均投保薪資",
            f"{p_name}_li_sal",
            10000,
            45800,
            p.get("labor_ins_salary", 45800),
            step=1000,
        )  # 綁定參數
        p["salary_growth_rate"] = dual_input(  # 預估薪資成長率
            "預估薪資每年成長率 (%)",
            f"{p_name}_sal_growth",
            0.0,
            10.0,
            p.get("salary_growth_rate", 2.0),
            step=0.1,
            format_fmt="%.1f",
        )  # 綁定參數
        p["labor_pension_rate"] = dual_input(  # 勞退提撥比例
            "勞退提撥率 (雇主6% + 個人自提%)",
            f"{p_name}_lp_rate",
            6,
            12,
            p.get("labor_pension_rate", 12),
            step=1,
        )  # 綁定參數
        p["labor_pension_claim_age"] = dual_input(  # 勞退請領年齡
            "勞退開始提領年齡 (法定≥60歲)",
            f"{p_name}_lp_claim",
            60,
            100,
            p.get("labor_pension_claim_age", 60),
        )  # 綁定參數
        p["labor_ins_claim_age"] = dual_input(  # 勞保請領年齡
            "勞保年金開始提領年齡 (60~65歲)",
            f"{p_name}_li_claim",
            60,
            65,
            p.get("labor_ins_claim_age", 60),
        )  # 綁定參數

        p["drawdown_priority"] = st.multiselect(  # 退休金扣款順序多選框
            "資產扣款優先順序 (第一個項目最優先扣抵)：",  # 說明文字
            options=["備用金", "股票", "勞退金額"],  # 三大項目
            default=p.get(
                "drawdown_priority", ["備用金", "股票", "勞退金額"]
            ),  # 預設順序
            key=f"{p_name}_drawdown_prio",  # 控制金鑰
        )  # 多選框結束

    # 內部 Dataframe 重新計算管理邏輯
    working_df_key = f"df_{p_name}"  # 表格變數金鑰
    hash_key = f"hash_{p_name}"  # 快照雜湊金鑰
    current_hash = json.dumps(p, sort_keys=True)  # 將目前設定轉為文字標籤

    if (
        st.session_state.get(hash_key) != current_hash
        or working_df_key not in st.session_state
    ):  # 若設定已改變或表格未建立
      st.session_state[hash_key] = current_hash  # 寫入最新標籤
      base_df = run_initial_simulation(p)  # 計算基礎模擬表格
      st.session_state[working_df_key] = recalculate_dataframe(
          base_df, p
      )  # 計算資產滾動並寫入

    sim_results[p_name] = st.session_state[working_df_key]  # 放入結果字典

# 🌟 UI 改善亮點 4：結果前置與儀表板卡片視覺化 (Result-First Dashboard)
st.markdown("---")  # 水平分割線
st.markdown("## 步驟 3：查看您的退休資產成果分析")  # 大步驟標題

if len(profiles_to_calc) == 1:  # 單人模式
  master_df = sim_results[profiles_to_calc[0]].copy()  # 複製個人表格
else:  # 夫妻雙人模式
  df1 = sim_results[profiles_to_calc[0]]  # 取得人物 1 表格
  df2 = sim_results[profiles_to_calc[1]]  # 取得人物 2 表格
  master_df = df1[["年齡", "狀態"]].copy()  # 複製基礎欄位
  master_df["累計勞退金額"] = (
      df1["累計勞退金額"] + df2["累計勞退金額"]
  )  # 雙人金額相加
  master_df["累計股票金額"] = (
      df1["累計股票金額"] + df2["累計股票金額"]
  )  # 雙人金額相加
  master_df["累計備用金"] = (
      df1["累計備用金"] + df2["累計備用金"]
  )  # 雙人金額相加
  master_df["累計總資產"] = (
      df1["累計總資產"] + df2["累計總資產"]
  )  # 雙人金額相加

retire_age_ref = st.session_state["user_profiles"][profiles_to_calc[0]][
    "retire_age"
]  # 取得參考退休年齡
claim_60_idx = master_df[master_df["年齡"] == 60]  # 找出 60 歲列
claim_ret_idx = master_df[master_df["年齡"] == retire_age_ref]  # 找出退休年齡列

val_at_retire = (
    claim_ret_idx["累計總資產"].values[0] if len(claim_ret_idx) > 0 else 0
)  # 退休時總資產
val_at_60 = (
    claim_60_idx["累計總資產"].values[0] if len(claim_60_idx) > 0 else 0
)  # 60 歲時總資產

# 四大核心結果指標卡片 (Metrics Cards)
row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)  # 切分為 4 欄
with row1_col1:  # 卡片 1
  st.metric(
      f"🛑 退休時總資產 ({retire_age_ref}歲)", f"${val_at_retire:,.0f}"
  )  # 顯示退休資產
with row1_col2:  # 卡片 2
  st.metric("📈 60歲時滾動總資產", f"${val_at_60:,.0f}")  # 顯示 60 歲資產
with row1_col3:  # 卡片 3
  total_annuity_monthly = 0  # 月領年金初始化
  for p_name in profiles_to_calc:  # 巡迴計算年金
    p = st.session_state["user_profiles"][p_name]  # 讀取個人設定
    tot_yrs = p["labor_ins_years"] + max(
        0, p["retire_age"] - p["current_age"]
    )  # 計算總年資
    total_annuity_monthly += calc_labor_ins_annuity(  # 加總年金
        p["labor_ins_salary"], tot_yrs, p["labor_ins_claim_age"]
    )  # 呼叫計算公式
  st.metric(
      "💵 預估勞保月領年金", f"${total_annuity_monthly:,.0f} /月"
  )  # 顯示月領年金
with row1_col4:  # 卡片 4
  end_val = master_df.iloc[-1]["累計總資產"]  # 85 歲剩餘總資產
  st.metric("🏁 85歲終點剩餘總資產", f"${end_val:,.0f}")  # 顯示終點資產

# 繪製 Plotly 資產趨勢圖表
st.markdown("#### 📈 資產累積與退休花費趨勢圖")  # 圖表區塊標題
fig = go.Figure()  # 建立 Plotly 圖表物件

fig.add_trace(  # 加入勞退折線
    go.Scatter(  # 散佈圖/折線圖
        x=master_df["年齡"],  # X 軸：年齡
        y=master_df["累計勞退金額"],  # Y 軸：勞退
        mode="lines",  # 純折線模式
        name="勞退金額 (含請領後投資)",  # 圖例名稱
        line=dict(color="#2563EB"),  # 藍色線條
    )  # 折線設定結束
)  # 加入結束

fig.add_trace(  # 加入股票折線
    go.Scatter(  # 散佈圖/折線圖
        x=master_df["年齡"],  # X 軸：年齡
        y=master_df["累計股票金額"],  # Y 軸：股票
        mode="lines",  # 純折線模式
        name="投資股票/基金",  # 圖例名稱
        line=dict(color="#059669"),  # 綠色線條
    )  # 折線設定結束
)  # 加入結束

fig.add_trace(  # 加入總資產折線
    go.Scatter(  # 散佈圖/折線圖
        x=master_df["年齡"],  # X 軸：年齡
        y=master_df["累計總資產"],  # Y 軸：總資產
        mode="lines+markers",  # 折線加點模式
        name="總資產趨勢線",  # 圖例名稱
        line=dict(color="#1E1B4B", width=3),  # 深藍加粗線條
    )  # 折線設定結束
)  # 加入結束

fig.add_trace(  # 加入備用金折線 (使用右側 Y 軸)
    go.Scatter(  # 散佈圖/折線圖
        x=master_df["年齡"],  # X 軸：年齡
        y=master_df["累計備用金"],  # Y 軸：備用金
        mode="lines",  # 純折線模式
        name="備用現金 (右軸)",  # 圖例名稱
        line=dict(color="#D97706", width=2, dash="dot"),  # 橘色虛線
        yaxis="y2",  # 綁定至右側 Y2 軸
    )  # 折線設定結束
)  # 加入結束

fig.add_vline(  # 加入退休垂直輔助線
    x=retire_age_ref,  # 位置：退休年齡
    line_dash="dash",  # 虛線樣式
    line_color="red",  # 紅色
    annotation_text=f"停止工作 ({retire_age_ref}歲)",  # 輔助標籤文字
)  # 輔助線結束

fig.add_vline(  # 加入勞退請領輔助線
    x=60,  # 位置：60 歲
    line_dash="dash",  # 虛線樣式
    line_color="green",  # 綠色
    annotation_text="勞退請領 (60歲)",  # 輔助標籤文字
)  # 輔助線結束

fig.update_layout(  # 設定版面配置
    xaxis=dict(title="年齡 (歲)"),  # X 軸名稱
    yaxis=dict(title="主要資產金額 (TWD)", side="left"),  # 左 Y 軸名稱
    yaxis2=dict(  # 右 Y 軸設定
        title="備用現金金額 (TWD)",  # 右 Y 軸名稱
        side="right",  # 放右側
        overlaying="y",  # 與左 Y 軸重疊
        showgrid=False,  # 不顯示右軸網格
    ),  # 右 Y 軸設定結束
    hovermode="x unified",  # 懸浮顯示同一 X 軸資料
    margin=dict(l=20, r=20, t=30, b=20),  # 邊距設定
)  # 版面配置結束
st.plotly_chart(fig, use_container_width=True)  # 渲染 Plotly 圖表

# 🌟 UI 改善亮點 5：明細表格收納至 Expandable 區塊中 (預防視覺雜亂)
st.markdown("---")  # 水平分割線
with st.expander(
    "📑 點此展開/隱藏【逐年詳細數據表格與匯出】", expanded=False
):  # 收納表格的折疊區塊
  selected_detail_profile = st.selectbox(  # 選取要看哪個人的表格
      "選擇欲檢視/編輯的明細對象", profiles_to_calc  # 選項
  )  # 下拉選單結束

  working_key = f"df_{selected_detail_profile}"  # 表格金鑰
  profile_obj = st.session_state["user_profiles"][
      selected_detail_profile
  ]  # 個人設定字典


  def on_table_edited():  # 表格編輯連動 Callback 函式
    editor_key = f"editor_{selected_detail_profile}"  # 編輯器金鑰
    if (
        editor_key in st.session_state
        and "edited_rows" in st.session_state[editor_key]
    ):  # 檢查有無編輯紀錄
      changes_dict = st.session_state[editor_key]["edited_rows"]  # 取得編輯內容
      if changes_dict:  # 若有內容
        curr_df = st.session_state[working_key].copy()  # 複製表格
        for r_idx_str, row_changes in changes_dict.items():  # 巡迴修改列
          r_idx = int(r_idx_str)  # 轉列號為整數
          for col_name, new_val in row_changes.items():  # 巡迴欄位
            curr_df.at[r_idx, col_name] = new_val  # 覆蓋新值

        st.session_state[working_key] = recalculate_dataframe(
            curr_df, profile_obj
        )  # 重新計算資產滾動


  edited_df = st.data_editor(  # 呼叫資料編輯器
      st.session_state[working_key],  # 傳入表格
      num_rows="fixed",  # 限制列數固定
      use_container_width=True,  # 自動寬度
      disabled=[
          "累計勞退金額",
          "累計股票金額",
          "累計備用金",
          "累計總資產",
      ],  # 鎖定計算欄位不可改
      column_config={  # 欄位格式化配置
          "投保級距": st.column_config.NumberColumn(
              "投保級距", format="$%d"
          ),  # 貨幣格式
          "股票每月投入": st.column_config.NumberColumn(
              "股票每月投入", format="$%d"
          ),  # 貨幣格式
          "備用金每月投入(含年金併入)": st.column_config.NumberColumn(  # 格式化
              "備用金每月投入", format="$%d"
          ),  # 貨幣格式
          "退休月生活費": st.column_config.NumberColumn(
              "退休月生活費", format="$%d"
          ),  # 貨幣格式
          "當頁額外大額支出 (元)": st.column_config.NumberColumn(  # 欄位設定
              "當頁額外大額支出 (元)",  # 名稱
              format="$%d",  # 貨幣格式
              help="退休前已包含預設享樂開銷；可在此處手動修改或加入特定年份大額花費",  # 說明
          ),  # 設定結束
          "大額支出備註/用途": st.column_config.TextColumn(  # 文字欄位
              "大額支出備註/用途", help="自由紀錄該筆支出的用途"
          ),  # 設定結束
          "累計勞退金額": st.column_config.NumberColumn(
              "累計勞退金額", format="$%d"
          ),  # 貨幣格式
          "累計股票金額": st.column_config.NumberColumn(
              "累計股票金額", format="$%d"
          ),  # 貨幣格式
          "累計備用金": st.column_config.NumberColumn(
              "累計備用金", format="$%d"
          ),  # 貨幣格式
          "累計總資產": st.column_config.NumberColumn(
              "累計總資產", format="$%d"
          ),  # 貨幣格式
      },  # 格式化結束
      key=f"editor_{selected_detail_profile}",  # 控制金鑰
      on_change=on_table_edited,  # 觸發 Callback 函式
  )  # 編輯器結束

  csv_data = edited_df.to_csv(index=False).encode(
      "utf-8-sig"
  )  # 轉為 UTF-8-SIG CSV Format
  st.download_button(  # 下載 CSV 按鈕
      label="📥 下載此對象之逐年明細 CSV 表格",  # 按鈕文字
      data=csv_data,  # 下載資料
      file_name=f"{selected_detail_profile}_退休規劃明細.csv",  # 檔名
      mime="text/csv",  # 檔案類型
  )  # 下載按鈕設定結束
