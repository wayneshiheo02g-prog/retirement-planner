import json  # 匯入處理 JSON 檔案格式的工具箱
import numpy as np  # 匯入處理數字與數學計算的工具箱，簡稱為 np
import pandas as pd  # 匯入處理表格資料（如 Excel 般的資料表）的工具箱，簡稱為 pd
import plotly.graph_objects as go  # 匯入繪製互動式圖表的工具箱，簡稱為 go
import streamlit as st  # 匯入用來製作網頁介面的工具箱，簡稱為 st

# 設定 Streamlit 網頁的基本外觀與標題
st.set_page_config(  # 呼叫設定網頁的函式
    page_title="Retirement Planning System present by Wayne SHIH",  # 設定瀏覽器分頁標題
    layout="wide",  # 設定網頁版面為寬螢幕模式
    initial_sidebar_state="expanded",  # 設定側邊欄一開始為展開狀態
)  # 結束網頁設定

# 設定網頁自訂美化樣式 (CSS)
st.markdown(  # 讓 Streamlit 可以渲染 HTML/CSS 樣式
    """
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .author-sub { font-size: 0.95rem; font-weight: 500; color: #6B7280; font-style: italic; margin-bottom: 0.6rem; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 1.5rem; }
    .stNumberInput input { font-weight: 600; }
</style>
""",  # 這裡是用來調整字體大小、顏色與間距的網頁設計碼
    unsafe_allow_html=True,  # 允許使用 HTML/CSS 語法
)  # 結束樣式設定


# 自訂函式：建立一個「數字輸入框」與「滑桿」同步連動的元件
def dual_input(  # 定義名為 dual_input 的函式
    label,  # 傳入輸入框的名稱標題
    key_prefix,  # 傳入用於分辨不同元件的獨一無二前綴字串
    min_value,  # 傳入可輸入的最小值
    max_value,  # 傳入可輸入的最大值
    default_val,  # 傳入預設顯示的數字
    step=1,  # 傳入每次加減的步階（預設為 1）
    format_fmt=None,  # 傳入數字顯示格式（例如小數點幾位）
    help_text=None,  # 傳入滑鼠移上去時顯示的說明文字
):  # 函式定義開頭
  st.markdown(f"**{label}**")  # 在網頁上印出粗體的標題文字
  val_key = f"{key_prefix}_val"  # 建立存放目前數值的變數名稱字串
  num_key = f"{key_prefix}_num"  # 建立數字輸入框專用的控制名稱字串
  slider_key = f"{key_prefix}_slider"  # 建立拉桿專用的控制名稱字串

  if val_key not in st.session_state:  # 如果網頁記憶體中還沒有這個數值
    st.session_state[val_key] = default_val  # 就把數值設定為預設值

  if num_key not in st.session_state:  # 如果網頁記憶體中還沒有數字輸入框的狀態
    st.session_state[num_key] = st.session_state[
        val_key
    ]  # 讓數字輸入框顯示目前數值
  if slider_key not in st.session_state:  # 如果網頁記憶體中還沒有拉桿的狀態
    st.session_state[slider_key] = st.session_state[
        val_key
    ]  # 讓拉桿位置調整到目前數值

  def sync_from_num():  # 定義當使用者修改「數字輸入框」時執行的動作
    st.session_state[val_key] = st.session_state[num_key]  # 更新目前數值
    st.session_state[slider_key] = st.session_state[
        num_key
    ]  # 自動把拉桿拉到對應位置

  def sync_from_slider():  # 定義當使用者拉動「拉桿」時執行的動作
    st.session_state[val_key] = st.session_state[slider_key]  # 更新目前數值
    st.session_state[num_key] = st.session_state[
        slider_key
    ]  # 自動把數字輸入框變成對應數字

  col1, col2 = st.columns([1, 1])  # 在網頁上切分成左右等寬的兩個欄位
  with col1:  # 在左邊欄位放入元件
    st.number_input(  # 建立數字輸入框
        label="數字輸入",  # 元件名稱
        min_value=min_value,  # 設定最小值
        max_value=max_value,  # 設定最大值
        step=step,  # 設定加減間距
        format=format_fmt,  # 設定顯示格式
        key=num_key,  # 綁定記憶體控制名稱
        on_change=sync_from_num,  # 設定數字改變時觸發同步函式
        label_visibility="collapsed",  # 隱藏重複顯示的元件名稱
        help=help_text,  # 顯示說明提示
    )  # 結束數字輸入框設定
  with col2:  # 在右邊欄位放入元件
    st.slider(  # 建立滑桿（拉桿）
        label="滑桿調整",  # 元件名稱
        min_value=min_value,  # 設定最小值
        max_value=max_value,  # 設定最大值
        step=step,  # 設定加減間距
        key=slider_key,  # 綁定記憶體控制名稱
        on_change=sync_from_slider,  # 設定拉桿移動時觸發同步函式
        label_visibility="collapsed",  # 隱藏重複顯示的元件名稱
    )  # 結束滑桿設定
  return st.session_state[val_key]  # 回傳最後使用者選擇的數值


# 建立台灣勞退投保薪資級距對照清單 (由小到大排列)
LABOR_PENSION_LEVELS = [  # 用中括號建立一個數值清單 (List)
    15000,
    15840,
    16500,
    17280,
    17880,
    19047,
    20008,
    21009,  # 薪資對照級距列表
    22000,
    23100,
    24000,
    25250,
    26400,
    27600,
    28800,  # 薪資對照級距列表
    30300,
    31800,
    33300,
    34800,
    36300,
    38200,
    40100,  # 薪資對照級距列表
    42000,
    43900,
    45800,
    48200,
    50600,
    53000,
    55400,  # 薪資對照級距列表
    57800,
    60800,
    63800,
    66800,
    69800,
    72800,
    76500,  # 薪資對照級距列表
    80200,
    83900,
    87600,
    92100,
    96600,
    101100,  # 薪資對照級距列表
    105600,
    110100,
    115500,
    120900,
    126300,
    131100,  # 薪資對照級距列表
    137100,
    142500,
    147900,
    150000,  # 最高投保級距金額
]  # 清單結束


def get_labor_pension_level(salary):  # 定義找出正確勞退級距的函式
  for lvl in LABOR_PENSION_LEVELS:  # 依序檢查每個級距金額
    if salary <= lvl:  # 如果薪資小於或等於目前檢查的級距
      return lvl  # 就回傳這個級距金額
  return LABOR_PENSION_LEVELS[-1]  # 若超過最大值，就回傳最高級距


# 設定系統預設的人員設定資料 (預設預設值字典)
DEFAULT_PROFILES = {  # 建立大字典 (Dictionary)
    "夫": {  # 丈夫的預設參數字典
        "current_age": 30,  # 目前年齡
        "retire_age": 55,  # 預計退休年齡
        "labor_pension_claim_age": 60,  # 勞退請領年齡
        "labor_ins_claim_age": 60,  # 勞保請領年齡
        "labor_pension_balance": 500000,  # 目前勞退帳戶金額
        "insured_salary": 105600,  # 月投保薪資
        "salary_growth_rate": 2.0,  # 薪資每年成長%
        "labor_pension_rate": 12.0,  # 勞退提撥率%
        "labor_pension_return": 7.64,  # 退休前勞退投報率%
        "labor_pension_reinvest_return": 5.0,  # 退休後轉投資投報率%
        "stock_balance": 4000000,  # 目前股票總額
        "stock_monthly": 35000,  # 每月股票投入
        "stock_return": 6.0,  # 股票年報酬率%
        "cash_balance": 2000000,  # 目前備用金總額
        "cash_monthly": 12000,  # 每月備用金投入
        "cash_return": 2.0,  # 備用金年利率%
        "labor_ins_years": 10,  # 目前勞保年資
        "labor_ins_salary": 45800,  # 勞保最高投保薪資
        "post_retire_expense": 100000,  # 退休後月生活費
        "drawdown_priority": ["備用金", "股票", "勞退金額"],  # 生活費扣款優先順序
    },  # 丈夫預設值結束
    "妻": {  # 妻子的預設參數字典
        "current_age": 30,  # 目前年齡
        "retire_age": 55,  # 預計退休年齡
        "labor_pension_claim_age": 60,  # 勞退請領年齡
        "labor_ins_claim_age": 60,  # 勞保請領年齡
        "labor_pension_balance": 500000,  # 目前勞退帳戶金額
        "insured_salary": 55400,  # 月投保薪資
        "salary_growth_rate": 2.0,  # 薪資每年成長%
        "labor_pension_rate": 12.0,  # 勞退提撥率%
        "labor_pension_return": 7.64,  # 退休前勞退投報率%
        "labor_pension_reinvest_return": 5.0,  # 退休後轉投資投報率%
        "stock_balance": 2500000,  # 目前股票總額
        "stock_monthly": 20000,  # 每月股票投入
        "stock_return": 6.0,  # 股票年報酬率%
        "cash_balance": 1500000,  # 目前備用金總額
        "cash_monthly": 8000,  # 每月備用金投入
        "cash_return": 2.0,  # 備用金年利率%
        "labor_ins_years": 10,  # 目前勞保年資
        "labor_ins_salary": 45800,  # 勞保最高投保薪資
        "post_retire_expense": 40000,  # 退休後月生活費
        "drawdown_priority": ["備用金", "股票", "勞退金額"],  # 生活費扣款優先順序
    },  # 妻子預設值結束
}  # 大字典設定結束


def calc_labor_ins_annuity(
    avg_salary, total_years, claim_age
):  # 定義計算勞保月領年金的公式函式
  base_monthly = (
      avg_salary * total_years * 0.0155
  )  # 計算基礎月領金額 (平均薪資 * 年資 * 1.55%)
  diff_years = claim_age - 65  # 計算與法定65歲相差幾年 (展延或提前)
  adj_factor = max(
      0.6, min(1.2, 1.0 + (diff_years * 0.04))
  )  # 計算提前或延後的加減成比例 (每年4%，最多±20%)
  return base_monthly * adj_factor  # 回傳最後調整後的每月勞保年金


# 初始模擬計算 Engine (建立基本空白表格)
def run_initial_simulation(p):  # 定義計算每年基本欄位資料的函式，p 代表個人的設定參數
  end_age = 85  # 設定模擬計算終點年齡為 85 歲
  records = []  # 建立一個空清單，用來收集每一年的紀錄
  cur_salary = p["insured_salary"]  # 設定第一年的初始投保薪資

  for age in range(p["current_age"], end_age + 1):  # 從目前年齡循環算到 85 歲
    is_working = age < p["retire_age"]  # 判斷這一年是否還在工作 (年齡小於退休年齡)
    status = (
        "工作中" if is_working else "已退休"
    )  # 根據判斷結果設定文字為「工作中」或「已退休」

    if (
        is_working and age > p["current_age"]
    ):  # 如果還在工作而且不是第一年
      cur_salary = cur_salary * (
          1 + p["salary_growth_rate"] / 100.0
      )  # 薪資按設定的成長率調漲

    cur_level = get_labor_pension_level(cur_salary)  # 查詢調漲後的薪資對應哪一個勞退級距

    if is_working:  # 如果在工作中
      pension_rate = p["labor_pension_rate"]  # 提撥率使用設定值
      stock_m = p["stock_monthly"]  # 股票月投入使用設定值
      cash_m = p["cash_monthly"]  # 備用金月投入使用設定值
      expense = 0  # 還沒退休，生活費支出設為 0
    else:  # 如果已經退休
      pension_rate = 0.0  # 停止提撥勞退
      stock_m = 0  # 停止定期定額買股票
      cash_m = 0  # 停止存備用金
      expense = p["post_retire_expense"]  # 開始計算退休月生活費

    labor_ins_annuity_monthly = 0  # 預設勞保年金為 0
    if age >= p["labor_ins_claim_age"]:  # 如果達到設定的勞保請領年齡
      service_years = p["labor_ins_years"] + max(
          0, p["retire_age"] - p["current_age"]
      )  # 計算總累積勞保年資
      labor_ins_annuity_monthly = calc_labor_ins_annuity(  # 算每月可領的勞保年金
          p["labor_ins_salary"], service_years, p["labor_ins_claim_age"]
      )  # 代入公式計算

    eff_pension_ret = (  # 計算勞退基金當年的年報酬率
        p["labor_pension_return"]  # 如果還沒領，使用基金官方預估報酬率
        if age < p["labor_pension_claim_age"]
        else p["labor_pension_reinvest_return"]  # 領出來轉投資後，改用自訂報酬率
    )  # 條件判斷結束

    records.append({  # 把這一年的所有基本數據打包成一個字典放進清單中
        "年齡": age,  # 年齡
        "狀態": status,  # 工作或退休
        "投保級距": round(cur_level),  # 四捨五入投保級距
        "當期提撥率(%)": pension_rate,  # 勞退提撥比例
        "勞退當期報酬率(%)": eff_pension_ret,  # 勞退投資報酬率
        "股票每月投入": stock_m,  # 股票每月買進金額
        "當期股票報酬率(%)": p["stock_return"],  # 股票年報酬率
        "備用金每月投入(含年金併入)": round(
            cash_m + labor_ins_annuity_monthly
        ),  # 備用金投入加勞保年金
        "備用金報酬率(%)": p["cash_return"],  # 備用金利息%
        "退休月生活費": expense,  # 退休生活費
        "當頁額外大額支出 (元)": 0,  # 預設大額支出為 0
        "大額支出備註/用途": "",  # 預設大額支出備註為空白
        "累計勞退金額": 0,  # 預設總額為 0 (稍後計算)
        "累計股票金額": 0,  # 預設總額為 0 (稍後計算)
        "累計備用金": 0,  # 預設總額為 0 (稍後計算)
        "累計總資產": 0,  # 預設總額為 0 (稍後計算)
    })  # 單年紀錄打包結束
  return pd.DataFrame(records)  # 將整個清單轉成 Pandas 的 Excel 表格型態回傳


# 動態資產滾動計算 Engine (連動計算利息與扣除支出)
def recalculate_dataframe(df, p):  # 傳入目前的數據表格 df 與個人參數 p
  cur_pension = p["labor_pension_balance"]  # 讀取最初的勞退帳戶餘額
  cur_stock = p["stock_balance"]  # 讀取最初的股票資產餘額
  cur_cash = p["cash_balance"]  # 讀取最初的備用金餘額

  updated_rows = []  # 建立清單準備存重新計算後的每一行
  priority = p.get(
      "drawdown_priority", ["備用金", "股票", "勞退金額"]
  )  # 取得生活費扣款順序
  claim_age = p.get("labor_pension_claim_age", 60)  # 取得勞退可以請領的年齡

  for _, row in df.iterrows():  # 逐行讀取表格內容進行複利與扣款計算
    age = int(row["年齡"])  # 取得該行的年齡
    level = float(row["投保級距"])  # 取得投保級距
    pension_rate = float(row["當期提撥率(%)"])  # 取得勞退提撥率
    pension_ret = float(row["勞退當期報酬率(%)"])  # 取得勞退報酬率
    stock_m = float(row["股票每月投入"])  # 取得每月股票投入
    stock_ret = float(row["當期股票報酬率(%)"])  # 取得股票報酬率
    cash_m = float(row["備用金每月投入(含年金併入)"])  # 取得每月現金投入
    cash_ret = float(row["備用金報酬率(%)"])  # 取得現金報酬率
    monthly_expense = float(row["退休月生活費"])  # 取得該年退休月生活費
    extra_expense = float(
        row.get("當頁額外大額支出 (元)", 0)
    )  # 取得該年使用者手動輸入的大額支出

    # 1. 計算勞退金額累積與利息
    pension_contrib = level * (pension_rate / 100.0) * 12  # 算出一年提撥的勞退總額
    cur_pension = (cur_pension + pension_contrib) * (
        1 + pension_ret / 100.0
    )  # 本金加上投入金額，再乘上報酬率

    # 2. 扣除退休生活費與大額支出
    tot_annual_draw = (
        monthly_expense * 12
    ) + extra_expense  # 算出該年總共需要花掉多少錢
    if tot_annual_draw > 0:  # 如果這一年需要花錢
      rem_expense = tot_annual_draw  # 紀錄還沒扣夠的金額

      for source in priority:  # 依照設定的資產順序開始扣款
        if rem_expense <= 0:  # 如果費用已經扣完了
          break  # 就跳出扣款迴圈

        if source == "備用金":  # 如果優先扣備用金
          draw = min(cur_cash, rem_expense)  # 看看備用金夠不夠扣
          cur_cash -= draw  # 扣除備用金
          rem_expense -= draw  # 減少剩餘要扣的費用
        elif source == "股票":  # 如果優先扣股票
          draw = min(cur_stock, rem_expense)  # 看看股票金額夠不夠扣
          cur_stock -= draw  # 賣掉股票扣款
          rem_expense -= draw  # 減少剩餘要扣的費用
        elif source == "勞退金額":  # 如果優先扣勞退
          if age >= claim_age:  # 只有達到請領年齡才可以動用勞退
            draw = min(cur_pension, rem_expense)  # 看看勞退金額夠不夠扣
            cur_pension -= draw  # 扣除勞退帳戶金額
            rem_expense -= draw  # 減少剩餘要扣的費用

    # 3. 計算股票與備用金的投入與複利成長
    cur_stock = (cur_stock + stock_m * 12) * (
        1 + stock_ret / 100.0
    )  # 股票本金 + 一年投入金額，再乘上股票報酬率
    cur_cash = (cur_cash + cash_m * 12) * (
        1 + cash_ret / 100.0
    )  # 現金本金 + 一年存入金額，再乘上利息
    tot_asset = cur_pension + cur_stock + cur_cash  # 加總三大資產算該年總資產

    row_dict = row.to_dict()  # 將原本這行的資料轉成字典
    row_dict["累計勞退金額"] = round(cur_pension)  # 寫入最新算出的勞退金額 (四捨五入)
    row_dict["累計股票金額"] = round(cur_stock)  # 寫入最新算出的股票金額 (四捨五入)
    row_dict["累計備用金"] = round(cur_cash)  # 寫入最新算出的備用金金額 (四捨五入)
    row_dict["累計總資產"] = round(tot_asset)  # 寫入最新算出的總資產 (四捨五入)
    updated_rows.append(row_dict)  # 將更新後的這行加入清單

  return pd.DataFrame(updated_rows)  # 回傳完全重新計算好的新表格


# 網頁畫面開始渲染 (UI Starts)
st.markdown(
    '<div class="main-header">Retirement Planning System</div>',
    unsafe_allow_html=True,
)  # 在網頁顯示大標題
st.markdown(
    '<div class="author-sub">present by Wayne SHIH</div>', unsafe_allow_html=True
)  # 在網頁顯示作者名稱
st.markdown(
    '<div class="sub-header">試算勞退新制、股票投資、備用現金與勞保年金，掌握退休資產變化</div>',
    unsafe_allow_html=True,
)  # 在網頁顯示副標題說明

# 側邊欄控制選單 (Sidebar)
st.sidebar.header("⚙️ 模式與檔案管理")  # 側邊欄區塊標題
calc_mode = st.sidebar.radio(
    "選擇計算模式", ["個人獨立規劃", "夫妻共同規劃"]
)  # 側邊欄單選按鈕：選擇模式

st.sidebar.subheader("💾 儲存/讀取評估方案")  # 側邊欄子標題
scenario_name = st.sidebar.text_input("方案名稱", "預設規劃案")  # 文字輸入框：方案名稱

if "user_profiles" not in st.session_state:  # 如果網頁記憶體還沒有使用者設定
  st.session_state["user_profiles"] = DEFAULT_PROFILES.copy()  # 載入預設的參數資料

if "uploader_key" not in st.session_state:  # 如果記憶體中沒有檔案上傳器的版本號
  st.session_state["uploader_key"] = 0  # 預設上傳器版本為 0


# --- 關鍵：JSON 檔案讀取 Callback 函式 (包含還原「逐年明細表格」) ---
def load_json_callback():  # 定義使用者挑選 JSON 檔案後自動執行的函式
  uploader_file = st.session_state.get(
      f"json_uploader_{st.session_state['uploader_key']}"
  )  # 取得上傳的檔案
  if uploader_file is not None:  # 如果確實有挑選檔案
    try:  # 嘗試執行以下讀取步驟
      loaded_data = json.load(uploader_file)  # 將 JSON 檔案內容轉成 Python 資料

      # 1. 還原基本輸入參數
      if "profiles" in loaded_data:  # 如果 JSON 包含 profiles 欄位
        st.session_state["user_profiles"] = loaded_data[
            "profiles"
        ]  # 更新使用者設定
      else:  # 如果是舊版的 JSON 檔案
        st.session_state["user_profiles"] = loaded_data  # 直接蓋寫設定

      # 2. 清除 UI 元件在記憶體中的暫存鍵值 (防止舊控制項覆蓋新讀入的資料)
      keys_to_clear = [  # 建立需要清理的鍵值名稱比對規則
          k
          for k in list(st.session_state.keys())
          if k.endswith("_val")
          or k.endswith("_num")
          or k.endswith("_slider")
          or k.endswith("_drawdown_prio")
          or k.startswith("df_")
          or k.startswith("hash_")
          or k.startswith("editor_")
      ]  # 搜尋出所有相關的舊暫存鍵值
      for k in keys_to_clear:  # 逐一巡迴
        del st.session_state[k]  # 從記憶體中刪除舊鍵值

      # 3. 還原「逐年明細」表格內容 (確保使用者自訂的大額支出/備註完整更新回來)
      if "details" in loaded_data:  # 如果 JSON 中包含表格明細資料
        for p_key, df_dict in loaded_data[
            "details"
        ].items():  # 讀取每個人 (如: 夫, 妻) 的明細
          loaded_df = pd.DataFrame(df_dict)  # 將字典格式轉回 Pandas 表格
          st.session_state[f"df_{p_key}"] = loaded_df  # 直接寫入網頁記憶體中
          if p_key in st.session_state["user_profiles"]:  # 同步更新雜湊金鑰
            st.session_state[f"hash_{p_key}"] = json.dumps(
                st.session_state["user_profiles"][p_key], sort_keys=True
            )  # 避免被系統誤判成設定改變而重新計算覆蓋

      st.session_state["uploader_key"] += 1  # 增加檔案上傳器的版本號 (用來清空上傳框)
      st.session_state["load_success_msg"] = (
          "✅ 成功載入方案與逐年明細！"  # 設定成功提示訊息
      )
    except Exception as e:  # 若檔案讀取發生錯誤
      st.session_state["load_error_msg"] = f"❌ 載入失敗：{e}"  # 設定失敗提示訊息


# 打包儲存資料的函式 (將參數與編輯後的表格明細一起打包)
def prepare_export_json():  # 定義打包 JSON 的函式
  export_details = {}  # 建立用於存表格明細的空字典
  for k in list(st.session_state.keys()):  # 搜尋記憶體中所有的資料
    if k.startswith("df_"):  # 只要是表格明細 (以 df_ 開頭)
      p_key = k.replace("df_", "")  # 取得對象名稱 (例如: 夫、妻)
      export_details[p_key] = st.session_state[k].to_dict(
          orient="records"
      )  # 將表格轉成標準字典格式

  full_package = {  # 建立最終匯出的總打包字典
      "profiles": st.session_state["user_profiles"],  # 放入介面設定參數
      "details": export_details,  # 放入編輯後的逐年表格明細
  }  # 打包結束
  return json.dumps(
      full_package, ensure_ascii=False, indent=2
  )  # 轉成格式漂亮的 JSON 文字字串


st.sidebar.download_button(  # 在側邊欄放下載按鈕
    label="📥 下載 JSON 設定檔 (含編輯明細)",  # 按鈕顯示文字
    data=prepare_export_json(),  # 代入打包好的 JSON 文字內容
    file_name=f"{scenario_name}_退休規劃.json",  # 下載後的預設檔名
    mime="application/json",  # 設定檔案類型為 JSON
)  # 結束下載按鈕設定

st.sidebar.file_uploader(  # 在側邊欄放上傳按鈕
    "📤 讀取已存方案 (JSON)",  # 按鈕顯示文字
    type=["json"],  # 限制只能挑選 json 格式的檔案
    key=f"json_uploader_{st.session_state['uploader_key']}",  # 動態綁定控制鍵值
    on_change=load_json_callback,  # 設定當使用者選取檔案時，自動執行 load_json_callback
)  # 結束上傳按鈕設定

if "load_success_msg" in st.session_state:  # 如果有成功載入訊息
  st.sidebar.success(
      st.session_state.pop("load_success_msg")
  )  # 顯示綠色成功框並清除訊息
if "load_error_msg" in st.session_state:  # 如果有失敗載入訊息
  st.sidebar.error(
      st.session_state.pop("load_error_msg")
  )  # 顯示紅色失敗框並清除訊息

profiles_to_calc = (
    ["個人"] if calc_mode == "個人獨立規劃" else ["夫", "妻"]
)  # 根據選取的模式決定要計算誰
tab_list = st.tabs(
    [f"👤 {p_name} 參數設定" for p_name in profiles_to_calc]
)  # 根據人數建立分頁 (Tabs)

sim_results = {}  # 建立字典準備存放計算後的最終結果

for idx, p_name in enumerate(profiles_to_calc):  # 逐一處理每一個人的設定分頁
  if p_name not in st.session_state["user_profiles"]:  # 若人物設定不在記憶體中
    st.session_state["user_profiles"][p_name] = DEFAULT_PROFILES[
        "夫"
    ].copy()  # 給予預設初始值

  with tab_list[idx]:  # 進入對應的分頁介面
    p = st.session_state["user_profiles"][p_name]  # 取得這個人的設定字典
    st.markdown(f"### 📋 {p_name} 基本參數配置")  # 顯示個人設定標題

    col_a, col_b = st.columns(2)  # 將分頁內容分成左右兩大欄
    with col_a:  # 左側欄位
      st.subheader("1. 年齡與退休時間規劃")  # 小標題
      p["current_age"] = dual_input(  # 呼叫自訂輸入組件設定目前年齡
          "目前年齡", f"{p_name}_cur_age", 20, 70, p.get("current_age", 30)
      )  # 綁定參數
      p["retire_age"] = dual_input(  # 呼叫自訂輸入組件設定退休年齡
          "預計停止工作年齡", f"{p_name}_ret_age", 40, 75, p.get("retire_age", 55)
      )  # 綁定參數
      p["labor_pension_claim_age"] = dual_input(  # 設定勞退請領年齡
          "勞退新制開始提領年齡 (法定≥60歲)",
          f"{p_name}_lp_claim",
          60,
          100,
          p.get("labor_pension_claim_age", 60),
      )  # 綁定參數
      p["labor_ins_claim_age"] = dual_input(  # 設定勞保年金請領年齡
          "勞保老年年金開始提領年齡 (60~65歲)",
          f"{p_name}_li_claim",
          60,
          65,
          p.get("labor_ins_claim_age", 60),
      )  # 綁定參數

      st.subheader("2. 薪資與勞工退休金新制")  # 小標題
      p["insured_salary"] = dual_input(  # 設定投保薪資級距
          "目前月投保薪資級距 (元)",
          f"{p_name}_ins_sal",
          15000,
          150000,
          p.get("insured_salary", 105600),
          step=1000,
      )  # 綁定參數
      p["salary_growth_rate"] = dual_input(  # 設定薪資調漲率
          "預估薪資年成長率 (%)",
          f"{p_name}_sal_growth",
          0.0,
          10.0,
          p.get("salary_growth_rate", 2.0),
          step=0.1,
          format_fmt="%.1f",
      )  # 綁定參數
      p["labor_pension_balance"] = dual_input(  # 設定目前勞退金額
          "勞退新制目前累計金額 (元)",
          f"{p_name}_lp_bal",
          0,
          20000000,
          p.get("labor_pension_balance", 500000),
          step=10000,
      )  # 綁定參數
      p["labor_pension_rate"] = dual_input(  # 設定提撥比例
          "勞退提撥率 (雇主+自提 %)",
          f"{p_name}_lp_rate",
          6,
          12,
          p.get("labor_pension_rate", 12),
          step=1,
      )  # 綁定參數
      p["labor_pension_return"] = dual_input(  # 設定勞退請領前報酬率
          "提領前：勞退基金預估年報酬率 (%)",
          f"{p_name}_lp_ret",
          0.0,
          15.0,
          p.get("labor_pension_return", 7.64),
          step=0.1,
          format_fmt="%.2f",
      )  # 綁定參數
      p["labor_pension_reinvest_return"] = dual_input(  # 設定勞退請領後轉投資報酬率
          "提領後：一次請領帳戶投資年報酬率 (%)",
          f"{p_name}_lp_reinv_ret",
          0.0,
          20.0,
          p.get("labor_pension_reinvest_return", 5.0),
          step=0.1,
          format_fmt="%.1f",
      )  # 綁定參數

    with col_b:  # 右側欄位
      st.subheader("3. 投資股票")  # 小標題
      p["stock_balance"] = dual_input(  # 設定目前股票累積金額
          "股票目前累計金額 (元)",
          f"{p_name}_stk_bal",
          0,
          100000000,
          p.get("stock_balance", 4000000),
          step=50000,
      )  # 綁定參數
      p["stock_monthly"] = dual_input(  # 設定每月定期定額買股票金額
          "股票每月投入金額 (元)",
          f"{p_name}_stk_m",
          0,
          1000000,
          p.get("stock_monthly", 35000),
          step=1000,
      )  # 綁定參數
      p["stock_return"] = dual_input(  # 設定股票年報酬率
          "股票預估年報酬率 (%)",
          f"{p_name}_stk_ret",
          0.0,
          20.0,
          p.get("stock_return", 6.0),
          step=0.1,
          format_fmt="%.1f",
      )  # 綁定參數

      st.subheader("4. 備用現金與定存")  # 小標題
      p["cash_balance"] = dual_input(  # 設定目前備用現金金額
          "備用金目前累計金額 (元)",
          f"{p_name}_csh_bal",
          0,
          100000000,
          p.get("cash_balance", 2000000),
          step=50000,
      )  # 綁定參數
      p["cash_monthly"] = dual_input(  # 設定每月存入備用金金額
          "備用金每月投入金額 (元)",
          f"{p_name}_csh_m",
          0,
          1000000,
          p.get("cash_monthly", 12000),
          step=1000,
      )  # 綁定參數
      p["cash_return"] = dual_input(  # 設定備用金利率
          "備用金預估年報酬率 (%)",
          f"{p_name}_csh_ret",
          0.0,
          10.0,
          p.get("cash_return", 2.0),
          step=0.1,
          format_fmt="%.1f",
      )  # 綁定參數

      st.subheader("5. 勞保老年給付與退休生活費")  # 小標題
      p["labor_ins_years"] = dual_input(  # 設定目前勞保年資
          "目前勞保投保年資 (年)",
          f"{p_name}_li_yrs",
          0,
          40,
          p.get("labor_ins_years", 10),
      )  # 綁定參數
      p["labor_ins_salary"] = dual_input(  # 設定勞保最高投保薪資
          "勞保平均最高月投保薪資 (上限45800元)",
          f"{p_name}_li_sal",
          10000,
          45800,
          p.get("labor_ins_salary", 45800),
          step=1000,
      )  # 綁定參數
      p["post_retire_expense"] = dual_input(  # 設定退休後每月生活費
          "退休後預估每月生活費 (元)",
          f"{p_name}_exp",
          10000,
          1000000,
          p.get("post_retire_expense", 100000),
          step=2000,
      )  # 綁定參數

      st.markdown(
          "**退休生活費及大額支出扣算順序 (依序排列)：**"
      )  # 顯示多選下拉選單標題
      p["drawdown_priority"] = st.multiselect(  # 建立多選下拉選單
          "請依序選擇扣款資產項目（第一個選取的將最優先扣抵）",  # 選單提示文字
          options=["備用金", "股票", "勞退金額"],  # 可供選擇的三項資產
          default=p.get(
              "drawdown_priority", ["備用金", "股票", "勞退金額"]
          ),  # 預設選取順序
          key=f"{p_name}_drawdown_prio",  # 獨一無二控制金鑰
      )  # 結束多選下拉選單設定

    # 表格與記憶體狀態管理
    working_df_key = f"df_{p_name}"  # 建立表格資料在記憶體中的名稱
    hash_key = f"hash_{p_name}"  # 建立參數快照雜湊的名稱
    current_hash = json.dumps(p, sort_keys=True)  # 將目前所有參數轉成字串當作比對標籤

    # 檢查：如果網頁中還沒有表格資料，或者上方 Sliders 參數被動過了，才重新計算整張表格
    if (
        st.session_state.get(hash_key) != current_hash
        or working_df_key not in st.session_state
    ):  # 條件判斷
      st.session_state[hash_key] = current_hash  # 更新最新的參數比對標籤
      base_df = run_initial_simulation(p)  # 產生初始基本資料表格
      st.session_state[working_df_key] = recalculate_dataframe(
          base_df, p
      )  # 執行利息與支出計算後寫入記憶體

    # 將計算好的表格存入總結果字典中，供下方圖表與指標使用
    sim_results[p_name] = st.session_state[working_df_key]  # 寫入字典

# 儀表板總覽呈現 (Dashboard Overview)
st.markdown("---")  # 在網頁畫出一條水平分割線
st.markdown("## 📊 退休資產試算總覽與里程碑比較")  # 顯示區塊大標題

if len(profiles_to_calc) == 1:  # 如果是單人模式
  master_df = sim_results[profiles_to_calc[0]].copy()  # 直接複製該個人的數據表格
else:  # 如果是夫妻雙人模式
  df1 = sim_results[profiles_to_calc[0]]  # 取得丈夫的數據表格
  df2 = sim_results[profiles_to_calc[1]]  # 取得妻子的數據表格
  master_df = df1[["年齡", "狀態"]].copy()  # 複製年齡與狀態欄位作為合併基礎
  master_df["累計勞退金額"] = (
      df1["累計勞退金額"] + df2["累計勞退金額"]
  )  # 將兩人的勞退金額相加
  master_df["累計股票金額"] = (
      df1["累計股票金額"] + df2["累計股票金額"]
  )  # 將兩人的股票金額相加
  master_df["累計備用金"] = (
      df1["累計備用金"] + df2["累計備用金"]
  )  # 將兩人的備用金金額相加
  master_df["累計總資產"] = (
      df1["累計總資產"] + df2["累計總資產"]
  )  # 將兩人的總資產金額相加

row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(
    4
)  # 將儀表板第一排切分成 4 個卡片欄位
retire_age_ref = st.session_state["user_profiles"][profiles_to_calc[0]][
    "retire_age"
]  # 取得參考退休年齡
claim_60_idx = master_df[master_df["年齡"] == 60]  # 找出 60 歲那年的數據行
claim_ret_idx = master_df[
    master_df["年齡"] == retire_age_ref
]  # 找出退休那年的數據行

val_at_retire = (
    claim_ret_idx["累計總資產"].values[0] if len(claim_ret_idx) > 0 else 0
)  # 取得退休時總資產金額
val_at_60 = (
    claim_60_idx["累計總資產"].values[0] if len(claim_60_idx) > 0 else 0
)  # 取得 60 歲時總資產金額

with row1_col1:  # 第 1 個數字卡片
  st.metric(
      f"停止工作時總資產 ({retire_age_ref}歲)", f"${val_at_retire:,.0f}"
  )  # 顯示退休時總資產
with row1_col2:  # 第 2 個數字卡片
  st.metric("到期繼續複利總資產 (60歲)", f"${val_at_60:,.0f}")  # 顯示 60 歲總資產
with row1_col3:  # 第 3 個數字卡片
  total_annuity_monthly = 0  # 預設月領年金總額為 0
  for p_name in profiles_to_calc:  # 巡迴計算每個人的勞保年金
    p = st.session_state["user_profiles"][p_name]  # 取得該個人參數
    tot_yrs = p["labor_ins_years"] + max(
        0, p["retire_age"] - p["current_age"]
    )  # 計算勞保總年資
    total_annuity_monthly += calc_labor_ins_annuity(  # 累加月領金額
        p["labor_ins_salary"], tot_yrs, p["labor_ins_claim_age"]
    )  # 呼叫年金計算函式
  st.metric(
      "預估勞保月領年金總額", f"${total_annuity_monthly:,.0f} /月"
  )  # 顯示預估月領年金
with row1_col4:  # 第 4 個數字卡片
  end_val = master_df.iloc[-1]["累計總資產"]  # 取得 85 歲表格最後一列的總資產
  st.metric("85歲終點預估剩餘總資產", f"${end_val:,.0f}")  # 顯示 85 歲剩餘總資產

# 繪製動態圖表 (Chart)
st.subheader("📈 退休累積資產增長趨勢圖 (動態即時連動)")  # 顯示圖表區塊標題
fig = go.Figure()  # 建立一個新的空白 Plotly 圖表物件

# 在圖表中加入第一條折線：勞退金額
fig.add_trace(  # 加入折線圖軌跡
    go.Scatter(  # 建立散佈/折線圖
        x=master_df["年齡"],  # 設定 X 軸資料為年齡
        y=master_df["累計勞退金額"],  # 設定 Y 軸資料為勞退金額
        mode="lines",  # 圖表樣式為純折線
        name="勞退金額 (含請領後投資)",  # 圖例標籤名稱
        line=dict(color="#2563EB"),  # 設定折線顏色為藍色
    )  # 結束這條折線設定
)  # 結束圖軌加入

# 在圖表中加入第二條折線：股票金額
fig.add_trace(  # 加入折線圖軌跡
    go.Scatter(  # 建立散佈/折線圖
        x=master_df["年齡"],  # 設定 X 軸資料為年齡
        y=master_df["累計股票金額"],  # 設定 Y 軸資料為股票金額
        mode="lines",  # 圖表樣式為純折線
        name="投資股票",  # 圖例標籤名稱
        line=dict(color="#059669"),  # 設定折線顏色為綠色
    )  # 結束這條折線設定
)  # 結束圖軌加入

# 在圖表中加入第三條折線：總資產線
fig.add_trace(  # 加入折線圖軌跡
    go.Scatter(  # 建立散佈/折線圖
        x=master_df["年齡"],  # 設定 X 軸資料為年齡
        y=master_df["累計總資產"],  # 設定 Y 軸資料為總資產
        mode="lines+markers",  # 圖表樣式為折線加上資料點標記
        name="總資產線",  # 圖例標籤名稱
        line=dict(color="#1E1B4B", width=3),  # 設定折線顏色為深藍色，線條加粗
    )  # 結束這條折線設定
)  # 結束圖軌加入

# 在圖表中加入第四條折線：備用金 (使用右側獨立 Y 軸)
fig.add_trace(  # 加入折線圖軌跡
    go.Scatter(  # 建立散佈/折線圖
        x=master_df["年齡"],  # 設定 X 軸資料為年齡
        y=master_df["累計備用金"],  # 設定 Y 軸資料為備用金
        mode="lines",  # 圖表樣式為純折線
        name="備用現金 (右軸)",  # 圖例標籤名稱
        line=dict(color="#D97706", width=2, dash="dot"),  # 設定顏色為橘黃色虛線
        yaxis="y2",  # 指定綁定到右側第二個 Y 軸
    )  # 結束這條折線設定
)  # 結束圖軌加入

# 在圖表中加入紅色的退休垂直虛線
fig.add_vline(  # 加入垂直輔助線
    x=retire_age_ref,  # 垂直線對齊退休年齡位置
    line_dash="dash",  # 線條樣式為虛線
    line_color="red",  # 線條顏色為紅色
    annotation_text=f"停止工作 ({retire_age_ref}歲)",  # 在虛線旁顯示文字標籤
)  # 結束垂直虛線設定

# 在圖表中加入綠色的 60 歲勞退請領垂直虛線
fig.add_vline(  # 加入垂直輔助線
    x=60,  # 垂直線對齊 60 歲位置
    line_dash="dash",  # 線條樣式為虛線
    line_color="green",  # 線條顏色為綠色
    annotation_text="勞退請領轉自營 (60歲)",  # 在虛線旁顯示文字標籤
)  # 結束垂直虛線設定

# 設定圖表的整體版面配置與雙 Y 軸
fig.update_layout(  # 更新版面配置
    xaxis=dict(title="年齡"),  # 設定 X 軸標題文字
    yaxis=dict(title="主要資產金額 (TWD)", side="left"),  # 設定左側 Y 軸標題
    yaxis2=dict(  # 設定右側第二個 Y 軸
        title="備用現金金額 (TWD)",  # 右側 Y 軸標題
        side="right",  # 將 Y 軸放於圖表右側
        overlaying="y",  # 與左側 Y 軸重疊呈現
        showgrid=False,  # 隱藏右側 Y 軸的背景網格線，避免畫面雜亂
    ),  # 結束右側 Y 軸設定
    hovermode="x unified",  # 滑鼠移上去時，同時顯示同一 X 軸的所有數值標籤
    margin=dict(l=20, r=20, t=30, b=20),  # 設定圖表周圍留白邊距
)  # 結束版面配置設定
st.plotly_chart(fig, use_container_width=True)  # 在 Streamlit 網頁上把圖表畫出來

# 可互動的詳細數據表格 (Interactive Data Table)
st.markdown("---")  # 畫出一條水平分割線
st.subheader("📑 逐年明細 (雙擊可修改參數)")  # 顯示表格區塊標題
selected_detail_profile = st.selectbox(  # 建立下拉選單挑選要檢視哪個人的表格
    "選擇欲檢視/編輯的明細對象", profiles_to_calc  # 選項清單 (如: 個人 或 夫/妻)
)  # 結束下拉選單設定

working_key = f"df_{selected_detail_profile}"  # 取得要編輯的表格記憶體名稱
profile_obj = st.session_state["user_profiles"][
    selected_detail_profile
]  # 取得該個人的設定字典


# 當使用者在表格中手動雙擊修改儲存格時自動執行的 Callback 函式
def on_table_edited():  # 定義表格編輯 Callback 函式
  editor_key = f"editor_{selected_detail_profile}"  # 取得編輯器控制組件名稱
  if (
      editor_key in st.session_state
      and "edited_rows" in st.session_state[editor_key]
  ):  # 檢查是否有編輯紀錄
    changes_dict = st.session_state[editor_key]["edited_rows"]  # 取得使用者編輯的內容字典
    if changes_dict:  # 如果確實有修改內容
      curr_df = st.session_state[working_key].copy()  # 複製一份目前的表格數據
      for r_idx_str, row_changes in changes_dict.items():  # 巡迴每一個修改的列號
        r_idx = int(r_idx_str)  # 將列號字串轉成整數 index
        for col_name, new_val in row_changes.items():  # 巡迴該列中每一個修改的欄位
          curr_df.at[r_idx, col_name] = new_val  # 將新修改的值寫入表格中

      # 填入使用者手動修改的值後，傳入計算引擎重新運算整張表格的利息與總資產
      st.session_state[working_key] = recalculate_dataframe(
          curr_df, profile_obj
      )  # 更新記憶體


# 渲染可編輯的表格組件
edited_df = st.data_editor(  # 呼叫 Streamlit 互動表格編輯器
    st.session_state[working_key],  # 傳入目前要顯示的數據表格
    num_rows="fixed",  # 固定表格列數，不允許使用者手動增加或刪減「年齡列」
    use_container_width=True,  # 自動對齊並填滿網頁寬度
    disabled=[
        "累計勞退金額",
        "累計股票金額",
        "累計備用金",
        "累計總資產",
    ],  # 鎖定系統計算出的總額欄位，不允許手動修改
    column_config={  # 設定各個欄位標題與數字格式
        "投保級距": st.column_config.NumberColumn(
            "投保級距", format="$%d"
        ),  # 格式化為貨幣格式
        "股票每月投入": st.column_config.NumberColumn(
            "股票每月投入", format="$%d"
        ),  # 格式化為貨幣格式
        "備用金每月投入(含年金併入)": st.column_config.NumberColumn(  # 欄位格式化
            "備用金每月投入", format="$%d"
        ),  # 格式化為貨幣格式
        "退休月生活費": st.column_config.NumberColumn(
            "退休月生活費", format="$%d"
        ),  # 格式化為貨幣格式
        "當頁額外大額支出 (元)": st.column_config.NumberColumn(  # 欄位格式化
            "當頁額外大額支出 (元)",  # 欄位顯示名稱
            format="$%d",  # 格式化為貨幣格式
            help="請在此處輸入該年齡一次性的大額支出金額 (如: 買車、買房頭期款)",  # 移上去的說明
        ),  # 欄位設定結束
        "大額支出備註/用途": st.column_config.TextColumn(  # 設定文字欄位
            "大額支出備註/用途", help="可自由紀錄該筆支出的用途，防止未來遺忘"
        ),  # 欄位設定結束
        "累計勞退金額": st.column_config.NumberColumn(
            "累計勞退金額", format="$%d"
        ),  # 格式化為貨幣格式
        "累計股票金額": st.column_config.NumberColumn(
            "累計股票金額", format="$%d"
        ),  # 格式化為貨幣格式
        "累計備用金": st.column_config.NumberColumn(
            "累計備用金", format="$%d"
        ),  # 格式化為貨幣格式
        "累計總資產": st.column_config.NumberColumn(
            "累計總資產", format="$%d"
        ),  # 格式化為貨幣格式
    },  # 欄位配置設定結束
    key=f"editor_{selected_detail_profile}",  # 綁定編輯器獨一無二的控制金鑰
    on_change=on_table_edited,  # 設定當使用者修改表格儲存格時，自動觸發 on_table_edited 函式
)  # 互動表格設定結束

st.subheader("📥 匯出明細資料")  # 顯示匯出區塊小標題
csv_data = edited_df.to_csv(index=False).encode(
    "utf-8-sig"
)  # 將目前表格轉成 Excel 可開啟的 UTF-8 CSV 檔案格式
st.download_button(  # 在網頁放置 CSV 下載按鈕
    label="下載此對象之逐年明細 CSV",  # 按鈕顯示文字
    data=csv_data,  # 代入轉換好的 CSV 資料
    file_name=f"{selected_detail_profile}_退休規劃明細.csv",  # 下載的檔案名稱
    mime="text/csv",  # 檔案類型為 CSV
)  # 下載按鈕設定結束
