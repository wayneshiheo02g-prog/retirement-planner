import json  # 匯入處理 JSON 檔案格式的工具箱
import numpy as np  # 匯入數字與數學計算工具箱
import pandas as pd  # 匯入表格資料處理工具箱
import plotly.graph_objects as go  # 匯入互動式圖表繪製工具箱
import streamlit as st  # 匯入 Streamlit 網頁介面框架

# ==========================================
# 0. 全域常數與設定 (Constants)
# ==========================================
LABOR_INS_MAX_SALARY = 45800  # 勞保最高投保薪資上限
DEFAULT_STOCK_RATIO = 80  # 預設股票配置比例 (%)
ANNUITY_RATE_PER_YEAR = 0.0155  # 勞保所得替代率

LABOR_PENSION_LEVELS = [
    15000,
    15840,
    16500,
    17280,
    17880,
    19047,
    20008,
    21009,
    22000,
    23100,
    24000,
    25250,
    26400,
    27600,
    28800,
    30300,
    31800,
    33300,
    34800,
    36300,
    38200,
    40100,
    42000,
    43900,
    45800,
    48200,
    50600,
    53000,
    55400,
    57800,
    60800,
    63800,
    66800,
    69800,
    72800,
    76500,
    80200,
    83900,
    87600,
    92100,
    96600,
    101100,
    105600,
    110100,
    115500,
    120900,
    126300,
    131100,
    137100,
    142500,
    147900,
    150000,
]

DEFAULT_PROFILES = {
    "個人": {
        "current_age": 35,
        "work_years": 10,
        "retire_age": 55,
        "life_expectancy": 85,
        "labor_pension_claim_age": 60,
        "labor_ins_claim_age": 60,
        "labor_pension_balance": 0,
        "insured_salary": 50000,
        "annual_bonus": 100000,
        "salary_growth_rate": 1.0,
        "labor_pension_self_rate": 6.0,
        "labor_pension_rate": 12.0,
        "labor_pension_return": 7.64,
        "labor_pension_reinvest_return": 4.0,
        "stock_balance": 1000000,
        "stock_monthly": 20000,
        "stock_return": 6.0,
        "cash_balance": 500000,
        "cash_monthly": 10000,
        "cash_return": 1.8,
        "labor_ins_years": 10,
        "labor_ins_salary": 45800,
        "pre_retire_monthly_expense": 30000,
        "pre_retire_annual_expense": 120000,
        "post_retire_expense": 60000,
        "legacy_target": 20000000,
        "drawdown_priority": ["備用金", "股票", "勞退金額"],
        "stock_ratio_pct": 80,
    },
    "夫": {
        "current_age": 35,
        "work_years": 10,
        "retire_age": 55,
        "life_expectancy": 85,
        "labor_pension_claim_age": 60,
        "labor_ins_claim_age": 60,
        "labor_pension_balance": 0,
        "insured_salary": 50000,
        "annual_bonus": 100000,
        "salary_growth_rate": 1.0,
        "labor_pension_self_rate": 6.0,
        "labor_pension_rate": 12.0,
        "labor_pension_return": 7.64,
        "labor_pension_reinvest_return": 4.0,
        "stock_balance": 1000000,
        "stock_monthly": 20000,
        "stock_return": 6.0,
        "cash_balance": 500000,
        "cash_monthly": 10000,
        "cash_return": 1.8,
        "labor_ins_years": 10,
        "labor_ins_salary": 45800,
        "pre_retire_monthly_expense": 30000,
        "pre_retire_annual_expense": 150000,
        "post_retire_expense": 60000,
        "legacy_target": 20000000,
        "drawdown_priority": ["備用金", "股票", "勞退金額"],
        "stock_ratio_pct": 80,
    },
    "妻": {
        "current_age": 30,
        "work_years": 5,
        "retire_age": 55,
        "life_expectancy": 85,
        "labor_pension_claim_age": 60,
        "labor_ins_claim_age": 60,
        "labor_pension_balance": 0,
        "insured_salary": 50000,
        "annual_bonus": 100000,
        "salary_growth_rate": 1.0,
        "labor_pension_self_rate": 0.0,
        "labor_pension_rate": 6.0,
        "labor_pension_return": 7.64,
        "labor_pension_reinvest_return": 4.0,
        "stock_balance": 400000,
        "stock_monthly": 15000,
        "stock_return": 6.0,
        "cash_balance": 300000,
        "cash_monthly": 5000,
        "cash_return": 1.8,
        "labor_ins_years": 5,
        "labor_ins_salary": 45800,
        "pre_retire_monthly_expense": 25000,
        "pre_retire_annual_expense": 100000,
        "post_retire_expense": 45000,
        "legacy_target": 10000000,
        "drawdown_priority": ["備用金", "股票", "勞退金額"],
        "stock_ratio_pct": 80,
    },
}

# 設定網頁標題與版面樣式
st.set_page_config(
    page_title="Retirement Planning Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.1rem; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.2rem; }
    .stNumberInput input { font-weight: 600; }
    .wizard-card { background-color: #F3F4F6; padding: 1.2rem; border-radius: 8px; margin-bottom: 1rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 1. 輔助與安全轉譯 Helper 函式
# ==========================================
def safe_float(val, default=0.0):
  """安全轉換為浮點數，防範 None / NaN / 空字串 造成的崩潰"""
  try:
    if pd.isna(val) or val is None:
      return float(default)
    return float(val)
  except (ValueError, TypeError):
    return float(default)


def safe_int(val, default=0):
  """安全轉換為整數"""
  return int(round(safe_float(val, default)))


def dual_input(
    label,
    key_prefix,
    min_value,
    max_value,
    default_val,
    step=1,
    format_fmt=None,
    help_text=None,
):
  st.markdown(f"**{label}**")
  val_key = f"{key_prefix}_val"
  num_key = f"{key_prefix}_num"
  slider_key = f"{key_prefix}_slider"

  if val_key not in st.session_state:
    st.session_state[val_key] = default_val
  if num_key not in st.session_state:
    st.session_state[num_key] = st.session_state[val_key]
  if slider_key not in st.session_state:
    st.session_state[slider_key] = st.session_state[val_key]

  def sync_from_num():
    st.session_state[val_key] = st.session_state[num_key]
    st.session_state[slider_key] = st.session_state[num_key]

  def sync_from_slider():
    st.session_state[val_key] = st.session_state[slider_key]
    st.session_state[num_key] = st.session_state[slider_key]

  col1, col2 = st.columns([1, 1])
  with col1:
    st.number_input(
        label="數字輸入",
        min_value=min_value,
        max_value=max_value,
        step=step,
        format=format_fmt,
        key=num_key,
        on_change=sync_from_num,
        label_visibility="collapsed",
        help=help_text,
    )
  with col2:
    st.slider(
        label="滑桿調整",
        min_value=min_value,
        max_value=max_value,
        step=step,
        key=slider_key,
        on_change=sync_from_slider,
        label_visibility="collapsed",
    )
  return st.session_state[val_key]


def get_labor_pension_level(salary):
  sal = safe_float(salary)
  for lvl in LABOR_PENSION_LEVELS:
    if sal <= lvl:
      return lvl
  return LABOR_PENSION_LEVELS[-1]


def calc_labor_ins_annuity(avg_salary, total_years, claim_age):
  sal = safe_float(avg_salary)
  yrs = safe_float(total_years)
  c_age = safe_float(claim_age)

  base_monthly = sal * yrs * ANNUITY_RATE_PER_YEAR
  diff_years = c_age - 65
  adj_factor = max(0.6, min(1.2, 1.0 + (diff_years * 0.04)))
  return base_monthly * adj_factor


def estimate_labor_pension_balance(
    monthly_salary, self_rate, work_years, annual_return
):
  sal = safe_float(monthly_salary)
  s_rate = safe_float(self_rate)
  w_yrs = safe_float(work_years)
  a_ret = safe_float(annual_return)

  total_rate = (6.0 + s_rate) / 100.0
  monthly_contrib = get_labor_pension_level(sal) * total_rate
  r_month = (a_ret / 100.0) / 12
  total_months = int(w_yrs * 12)

  if r_month == 0:
    return monthly_contrib * total_months
  estimated_balance = monthly_contrib * (
      ((1 + r_month) ** total_months - 1) / r_month
  )
  return round(estimated_balance)


# ==========================================
# 2. 模擬引擎核心 logic
# ==========================================
def run_initial_simulation(p):
  current_age = safe_int(p.get("current_age", 30))
  retire_age = safe_int(p.get("retire_age", 60))
  end_age = safe_int(p.get("life_expectancy", 85))

  records = []
  cur_salary = safe_float(p.get("insured_salary", 50000))
  cur_bonus = safe_float(p.get("annual_bonus", 0))  # 💡 取得預估每年獎金/年終總額
  salary_growth = safe_float(p.get("salary_growth_rate", 1.0)) / 100.0

  for age in range(current_age, end_age + 1):
    is_working = age < retire_age
    status = "工作中" if is_working else "已退休"

    if is_working and age > current_age:
      cur_salary *= 1 + salary_growth
      cur_bonus *= 1 + salary_growth  # 💡 獎金跟隨薪資成長率同步調升

    cur_level = get_labor_pension_level(cur_salary)

    if is_working:
      pension_rate = safe_float(p.get("labor_pension_rate", 12.0))
      stock_m = safe_float(p.get("stock_monthly", 0))
      cash_m = safe_float(p.get("cash_monthly", 0))
      annual_bonus_val = cur_bonus  # 💡 工作期間每年注入獎金
      expense = 0.0
      extra_exp = safe_float(p.get("pre_retire_annual_expense", 120000))
      extra_note = "退休前年度享樂/旅遊開銷"
    else:
      pension_rate = 0.0
      stock_m = 0.0
      cash_m = 0.0
      annual_bonus_val = 0.0  # 退休後無獎金收入
      expense = safe_float(p.get("post_retire_expense", 60000))
      extra_exp = 0.0
      extra_note = ""

    labor_ins_annuity_monthly = 0.0
    if age >= safe_int(p.get("labor_ins_claim_age", 60)):
      service_years = safe_float(p.get("labor_ins_years", 5)) + max(
          0, retire_age - current_age
      )
      labor_ins_annuity_monthly = calc_labor_ins_annuity(
          p.get("labor_ins_salary", LABOR_INS_MAX_SALARY),
          service_years,
          p.get("labor_ins_claim_age", 60),
      )

    eff_pension_ret = (
        safe_float(p.get("labor_pension_return", 7.64))
        if age < safe_int(p.get("labor_pension_claim_age", 60))
        else safe_float(p.get("labor_pension_reinvest_return", 4.0))
    )

    records.append({
        "年齡": age,
        "狀態": status,
        "投保級距": round(cur_level),
        "當期提撥率(%)": pension_rate,
        "勞退當期報酬率(%)": eff_pension_ret,
        "股票每月投入": stock_m,
        "當期股票報酬率(%)": safe_float(p.get("stock_return", 6.0)),
        "備用金每月投入(含年金併入)": round(
            cash_m + labor_ins_annuity_monthly
        ),
        "年度獎金/年終注入 (元)": round(
            annual_bonus_val
        ),  # 💡 新增此欄位記錄年度獎金
        "備用金報酬率(%)": safe_float(p.get("cash_return", 1.8)),
        "退休月生活費": expense,
        "當年額外大額支出 (元)": extra_exp,
        "大額支出備註/用途": extra_note,
        "累計勞退金額": 0,
        "累計股票金額": 0,
        "累計備用金": 0,
        "累計總資產": 0,
    })
  return pd.DataFrame(records)


def recalculate_dataframe(df, p):
  cur_pension = safe_float(p.get("labor_pension_balance", 0))
  cur_stock = safe_float(p.get("stock_balance", 0))
  cur_cash = safe_float(p.get("cash_balance", 0))

  updated_rows = []
  priority = p.get("drawdown_priority", ["備用金", "股票", "勞退金額"])
  claim_age = safe_int(p.get("labor_pension_claim_age", 60))

  for _, row in df.iterrows():
    age = safe_int(row["年齡"])
    level = safe_float(row["投保級距"])
    pension_rate = safe_float(row["當期提撥率(%)"])
    pension_ret = safe_float(row["勞退當期報酬率(%)"])
    stock_m = safe_float(row["股票每月投入"])
    stock_ret = safe_float(row["當期股票報酬率(%)"])
    cash_m = safe_float(row["備用金每月投入(含年金併入)"])
    annual_bonus_val = safe_float(row.get("年度獎金/年終注入 (元)", 0))  # 💡 讀取年終獎金
    cash_ret = safe_float(row["備用金報酬率(%)"])
    monthly_expense = safe_float(row["退休月生活費"])
    extra_expense = safe_float(row.get("當年額外大額支出 (元)", 0))

    # 1. 投入與利息滾存
    pension_contrib = level * (pension_rate / 100.0) * 12
    cur_pension = (cur_pension + pension_contrib) * (1 + pension_ret / 100.0)
    cur_stock = (cur_stock + stock_m * 12) * (1 + stock_ret / 100.0)
    cur_cash = (cur_cash + cash_m * 12 + annual_bonus_val) * (1 + cash_ret / 100.0)  # 💡 注入年終獎金

    # 2. 支出扣抵（依優先順序）
    tot_annual_draw = (monthly_expense * 12) + extra_expense
    if tot_annual_draw > 0:
      rem_expense = tot_annual_draw
      for source in priority:
        if rem_expense <= 0:
          break
        if source == "備用金" and cur_cash > 0:
          draw = min(cur_cash, rem_expense)
          cur_cash -= draw
          rem_expense -= draw
        elif source == "股票" and cur_stock > 0:
          draw = min(cur_stock, rem_expense)
          cur_stock -= draw
          rem_expense -= draw
        elif source == "勞退金額" and age >= claim_age and cur_pension > 0:
          draw = min(cur_pension, rem_expense)
          cur_pension -= draw
          rem_expense -= draw

      # 若所有指定項目扣完後仍不夠，則由預備金承擔缺口 (產生負債/赤字)
      if rem_expense > 0:
        cur_cash -= rem_expense

    tot_asset = cur_pension + cur_stock + cur_cash

    row_dict = row.to_dict()
    row_dict["累計勞退金額"] = round(cur_pension)
    row_dict["累計股票金額"] = round(cur_stock)
    row_dict["累計備用金"] = round(cur_cash)
    row_dict["累計總資產"] = round(tot_asset)
    updated_rows.append(row_dict)

  return pd.DataFrame(updated_rows)


def Fast_simulate_end_asset(p, monthly_req_total, stock_ratio):
  """高熱度二分搜尋的純數據計算引擎（優化效能）"""
  c_age = safe_int(p.get("current_age", 30))
  r_age = safe_int(p.get("retire_age", 60))
  e_age = safe_int(p.get("life_expectancy", 85))

  pension_bal = safe_float(p.get("labor_pension_balance", 0))
  stock_bal = safe_float(p.get("stock_balance", 0))
  cash_bal = safe_float(p.get("cash_balance", 0))

  stock_m_working = monthly_req_total * stock_ratio
  cash_m_working = monthly_req_total * (1.0 - stock_ratio)

  sal = safe_float(p.get("insured_salary", 50000))
  bonus = safe_float(p.get("annual_bonus", 0))
  sal_growth = safe_float(p.get("salary_growth_rate", 1.0)) / 100.0

  li_claim_age = safe_int(p.get("labor_ins_claim_age", 60))
  lp_claim_age = safe_int(p.get("labor_pension_claim_age", 60))

  for age in range(c_age, e_age + 1):
    is_working = age < r_age

    if is_working and age > c_age:
      sal *= 1 + sal_growth
      bonus *= (1 + sal_growth)

    if is_working:
      level = get_labor_pension_level(sal)
      p_rate = safe_float(p.get("labor_pension_rate", 12.0)) / 100.0
      pension_contrib = level * p_rate * 12
      stock_in = stock_m_working * 12
      cash_in = cash_m_working * 12
      ann_exp = safe_float(p.get("pre_retire_annual_expense", 120000))
    else:
      pension_contrib = 0.0
      stock_in = 0.0
      cash_in = 0.0
      ann_exp = safe_float(p.get("post_retire_expense", 60000)) * 12

    # 勞保年金匯入預備金
    if age >= li_claim_age:
      s_yrs = safe_float(p.get("labor_ins_years", 5)) + max(0, r_age - c_age)
      annuity_m = calc_labor_ins_annuity(
          p.get("labor_ins_salary", LABOR_INS_MAX_SALARY),
          s_yrs,
          li_claim_age,
      )
      cash_in += annuity_m * 12

    pension_ret = (
        safe_float(p.get("labor_pension_return", 7.64)) / 100.0
        if age < lp_claim_age
        else safe_float(p.get("labor_pension_reinvest_return", 4.0)) / 100.0
    )
    stock_ret = safe_float(p.get("stock_return", 6.0)) / 100.0
    cash_ret = safe_float(p.get("cash_return", 1.8)) / 100.0

    pension_bal = (pension_bal + pension_contrib) * (1 + pension_ret)
    stock_bal = (stock_bal + stock_in) * (1 + stock_ret)
    cash_bal = (cash_bal + cash_in) * (1 + cash_ret)

    if ann_exp > 0:
      rem = ann_exp
      # 順序：預備金 -> 股票 -> 勞退
      if cash_bal > 0:
        d = min(cash_bal, rem)
        cash_bal -= d
        rem -= d
      if rem > 0 and stock_bal > 0:
        d = min(stock_bal, rem)
        stock_bal -= d
        rem -= d
      if rem > 0 and age >= lp_claim_age and pension_bal > 0:
        d = min(pension_bal, rem)
        pension_bal -= d
        rem -= d
      if rem > 0:
        cash_bal -= rem

  return pension_bal + stock_bal + cash_bal


def calculate_retirement_goal(p, stock_ratio=0.8):
    c_age = safe_int(p.get("current_age", 30))
    r_age = safe_int(p.get("retire_age", 60))
    years_to_retire = max(1, r_age - c_age)

    salary = safe_float(p.get("insured_salary", 50000))
    annual_bonus = safe_float(p.get("annual_bonus", 0))

    # 💡 1. 取得勞退投保級距並計算「每月自提金額」
    level = get_labor_pension_level(salary)
    self_rate = safe_float(p.get("labor_pension_self_rate", 6.0)) / 100.0
    monthly_self_pension = level * self_rate  # 級距 * 自提%數

    pre_monthly_exp = safe_float(p.get("pre_retire_monthly_expense", 30000))
    pre_ann_exp = safe_float(p.get("pre_retire_annual_expense", 120000))

    # 💡 2. 淨結餘扣除「每月自提金額」
    monthly_income_total = salary + (annual_bonus / 12.0)
    monthly_savings_capacity = monthly_income_total - monthly_self_pension - (pre_monthly_exp + (pre_ann_exp / 12.0))

    insured_salary_li = min(salary, LABOR_INS_MAX_SALARY)
    total_labor_ins_years = safe_float(p.get("work_years", 5)) + years_to_retire
    estimated_labor_ins_monthly = calc_labor_ins_annuity(
        insured_salary_li, total_labor_ins_years, 60
    )

    target_legacy = safe_float(p.get("legacy_target", 2000000))

    # 二分搜尋法搜尋每月最適儲蓄額
    low = 0.0
    high = max(300000.0, salary * 5, target_legacy / 12.0)
    best_req = high

    for _ in range(35):
        mid = (low + high) / 2.0
        end_asset = Fast_simulate_end_asset(p, mid, stock_ratio)

        if end_asset < target_legacy:
            low = mid
        else:
            high = mid
            best_req = mid

    if best_req >= high - 1.0:
        best_req = high

    monthly_stock_required = best_req * stock_ratio
    monthly_cash_required = best_req * (1.0 - stock_ratio)

    if best_req == 0:
        status = "EXCELLENT"
    elif best_req <= monthly_savings_capacity * 0.85:
        status = "GREEN"
    elif best_req <= monthly_savings_capacity:
        status = "YELLOW"
    else:
        status = "RED"

    return {
        "years_to_retire": years_to_retire,
        "monthly_savings_capacity": monthly_savings_capacity,
        "estimated_labor_ins_monthly": estimated_labor_ins_monthly,
        "monthly_required_total": best_req,
        "monthly_stock_required": monthly_stock_required,
        "monthly_cash_required": monthly_cash_required,
        "status": status,
    }


# ==========================================
# UI 主介面與選單建構
# ==========================================
st.markdown(
    '<div class="main-header">Retirement Planning Simulator</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">present by Wayne SHIH</div>',
    unsafe_allow_html=True,
)

st.sidebar.header("⚙️ 模式與設定")
app_mode = st.sidebar.radio(
    "選擇使用模式",
    ["引導模式 (自動規劃)", "審視模式 (精確計算)"],
)
calc_mode = st.sidebar.radio(
    "選擇規劃人數", ["個人獨立規劃", "夫妻共同規劃"]
)

st.sidebar.subheader("💾 儲存/讀取評估方案")
scenario_name = st.sidebar.text_input("方案名稱", "預設規劃案")

if "user_profiles" not in st.session_state:
  st.session_state["user_profiles"] = DEFAULT_PROFILES.copy()

if "uploader_key" not in st.session_state:
  st.session_state["uploader_key"] = 0


def load_json_callback():
  uploader_file = st.session_state.get(
      f"json_uploader_{st.session_state['uploader_key']}"
  )
  if uploader_file is not None:
    try:
      loaded_data = json.load(uploader_file)
      profiles = loaded_data.get("profiles", loaded_data)
      st.session_state["user_profiles"] = profiles

      # 清除試算表與 Hash 快取
      keys_to_clear = [
          k
          for k in list(st.session_state.keys())
          if k.startswith("df_")
          or k.startswith("hash_")
          or k.startswith("editor_")
      ]
      for k in keys_to_clear:
        del st.session_state[k]

      # 同步至 Widget Session Keys
      for p_name, p in profiles.items():
        st.session_state[f"ez_bonus_{p_name}"] = safe_int(p.get("annual_bonus", 100000))
        if "stock_ratio_pct" in p:
          ratio_val = safe_int(p["stock_ratio_pct"])
        else:
          stk_m = safe_float(p.get("stock_monthly", 0))
          csh_m = safe_float(p.get("cash_monthly", 0))
          tot_m = stk_m + csh_m
          ratio_val = (
              safe_int(round((stk_m / tot_m) * 100))
              if tot_m > 0
              else DEFAULT_STOCK_RATIO
          )

        st.session_state[f"ez_stk_ratio_{p_name}"] = ratio_val
        p["stock_ratio_pct"] = ratio_val

        # 簡易模式 Sync
        st.session_state[f"ez_c_age_{p_name}"] = safe_int(
            p.get("current_age", 30)
        )
        st.session_state[f"ez_sal_{p_name}"] = safe_int(
            p.get("insured_salary", 50000)
        )
        st.session_state[f"ez_r_age_{p_name}"] = safe_int(
            p.get("retire_age", 60)
        )
        st.session_state[f"ez_w_yrs_{p_name}"] = safe_int(
            p.get("work_years", 5)
        )
        st.session_state[f"ez_l_exp_{p_name}"] = safe_int(
            p.get("life_expectancy", 85)
        )
        st.session_state[f"ez_pre_m_{p_name}"] = safe_int(
            p.get("pre_retire_monthly_expense", 30000)
        )
        st.session_state[f"ez_pre_a_{p_name}"] = safe_int(
            p.get("pre_retire_annual_expense", 120000)
        )
        st.session_state[f"ez_stk_b_{p_name}"] = safe_int(
            p.get("stock_balance", 1000000)
        )
        st.session_state[f"ez_csh_b_{p_name}"] = safe_int(
            p.get("cash_balance", 500000)
        )
        st.session_state[f"ez_post_m_{p_name}"] = safe_int(
            p.get("post_retire_expense", 60000)
        )
        st.session_state[f"ez_leg_{p_name}"] = safe_int(
            p.get("legacy_target", 2000000)
        )
        st.session_state[f"ez_sal_g_{p_name}"] = safe_float(
            p.get("salary_growth_rate", 1.0)
        )
        st.session_state[f"ez_stk_r_{p_name}"] = safe_float(
            p.get("stock_return", 6.0)
        )
        st.session_state[f"ez_lp_ret_pre_{p_name}"] = safe_float(
            p.get("labor_pension_return", 7.64)
        )
        st.session_state[f"ez_csh_r_{p_name}"] = safe_float(
            p.get("cash_return", 2.0)
        )
        st.session_state[f"ez_lp_ret_post_{p_name}"] = safe_float(
            p.get("labor_pension_reinvest_return", 4.0)
        )
        st.session_state[f"ez_self_rate_{p_name}"] = safe_float(
            p.get("labor_pension_self_rate", 6.0)
        )
        st.session_state[f"ez_custom_lp_{p_name}"] = safe_int(
            p.get("labor_pension_balance", 0)
        )

        # 專業模式 Dual input Sync
        dual_map = {
            "ret_stock": ("stock_return", safe_float),
            "ret_lp_pre": ("labor_pension_return", safe_float),
            "ret_cash": ("cash_return", safe_float),
            "ret_lp_post": ("labor_pension_reinvest_return", safe_float),
            "cur_age": ("current_age", safe_int),
            "ret_age": ("retire_age", safe_int),
            "ins_sal": ("insured_salary", safe_int),
            "ann_bonus": ("annual_bonus", safe_int),
            "stk_m": ("stock_monthly", safe_int),
            "csh_m": ("cash_monthly", safe_int),
            "pre_exp": ("pre_retire_annual_expense", safe_int),
            "exp": ("post_retire_expense", safe_int),
            "lp_bal": ("labor_pension_balance", safe_int),
            "stk_bal": ("stock_balance", safe_int),
            "csh_bal": ("cash_balance", safe_int),
            "li_yrs": ("labor_ins_years", safe_int),
            "li_sal": ("labor_ins_salary", safe_int),
            "sal_growth": ("salary_growth_rate", safe_float),
            "lp_rate": ("labor_pension_rate", safe_int),
            "lp_claim": ("labor_pension_claim_age", safe_int),
            "li_claim": ("labor_ins_claim_age", safe_int),
        }
        for prefix, (field, type_fn) in dual_map.items():
          v = type_fn(p.get(field, 0))
          st.session_state[f"{p_name}_{prefix}_val"] = v
          st.session_state[f"{p_name}_{prefix}_num"] = v
          st.session_state[f"{p_name}_{prefix}_slider"] = v

      if "details" in loaded_data:
        for p_key, df_dict in loaded_data["details"].items():
          st.session_state[f"df_{p_key}"] = pd.DataFrame(df_dict)
          if p_key in st.session_state["user_profiles"]:
            st.session_state[f"hash_{p_key}"] = json.dumps(
                st.session_state["user_profiles"][p_key], sort_keys=True
            )

      st.session_state["uploader_key"] += 1
      st.session_state["load_success_msg"] = "✅ 成功載入方案！"
    except Exception as e:
      st.session_state["load_error_msg"] = f"❌ 載入失敗：{e}"


def prepare_export_json():
  export_details = {}
  for k in list(st.session_state.keys()):
    if k.startswith("df_"):
      p_key = k.replace("df_", "")
      export_details[p_key] = st.session_state[k].to_dict(orient="records")
  full_package = {
      "profiles": st.session_state["user_profiles"],
      "details": export_details,
  }
  return json.dumps(full_package, ensure_ascii=False, indent=2)


st.sidebar.download_button(
    label="📥 下載 JSON 設定檔",
    data=prepare_export_json(),
    file_name=f"{scenario_name}_退休規劃.json",
    mime="application/json",
)

st.sidebar.file_uploader(
    "📤 讀取已儲存方案 (JSON)",
    type=["json"],
    key=f"json_uploader_{st.session_state['uploader_key']}",
    on_change=load_json_callback,
)

if "load_success_msg" in st.session_state:
  st.sidebar.success(st.session_state.pop("load_success_msg"))
if "load_error_msg" in st.session_state:
  st.sidebar.error(st.session_state.pop("load_error_msg"))

profiles_to_calc = (
    ["個人"] if calc_mode == "個人獨立規劃" else ["夫", "妻"]
)

# ==========================================
# 模式 A：簡易模式
# ==========================================
if app_mode == "引導模式 (自動規劃)":
  st.markdown("### 簡易退休目標診斷與規劃")

  profile_choice = st.radio(
      "選擇要評估的身份：",
      options=profiles_to_calc,
      horizontal=True,
      key="goal_profile_selector",
  )
  p = st.session_state["user_profiles"][profile_choice]

  st.subheader("現狀與個人基本資料")
  col1, col2, col3 = st.columns(3)
  with col1:
    p["current_age"] = st.number_input(
        "目前年紀 (歲)",
        min_value=18,
        max_value=80,
        value=safe_int(p.get("current_age", 30)),
        step=1,
        key=f"ez_c_age_{profile_choice}",
    )
    p["insured_salary"] = st.number_input(
        "目前月薪 (元)",
        min_value=0,
        value=safe_int(p.get("insured_salary", 50000)),
        step=1000,
        format="%d",
        key=f"ez_sal_{profile_choice}",
    )
    p["annual_bonus"] = st.number_input(
        "預估每年獎金/年終總額 (元)",
        min_value=0,
        value=safe_int(p.get("annual_bonus", 100000)),
        step=10000,
        format="%d",
        key=f"ez_bonus_{profile_choice}",
    )
  with col2:
    p["retire_age"] = st.number_input(
        "計劃退休年紀 (歲)",
        min_value=p["current_age"] + 1,
        max_value=90,
        value=safe_int(p.get("retire_age", 60)),
        step=1,
        key=f"ez_r_age_{profile_choice}",
    )
    p["work_years"] = st.number_input(
        "已工作年資 (年)",
        min_value=0,
        max_value=50,
        value=safe_int(p.get("work_years", 5)),
        step=1,
        key=f"ez_w_yrs_{profile_choice}",
    )
  with col3:
    p["life_expectancy"] = st.number_input(
        "試算最終壽命 (歲)",
        min_value=p["retire_age"] + 1,
        max_value=110,
        value=safe_int(p.get("life_expectancy", 85)),
        step=1,
        key=f"ez_l_exp_{profile_choice}",
    )

  st.markdown("---")
  st.subheader("現有資產與日常生活開銷")
  col4, col5 = st.columns(2)
  with col4:
    p["pre_retire_monthly_expense"] = st.number_input(
        "(退休前) 每月平均總花費 (元)",
        min_value=0,
        value=safe_int(p.get("pre_retire_monthly_expense", 30000)),
        step=1000,
        format="%d",
        key=f"ez_pre_m_{profile_choice}",
    )
  with col5:
    p["pre_retire_annual_expense"] = st.number_input(
        "(退休前) 每年享樂/旅遊/彈性支出 (元)",
        min_value=0,
        value=safe_int(p.get("pre_retire_annual_expense", 120000)),
        step=1000,
        format="%d",
        key=f"ez_pre_a_{profile_choice}",
    )

  col_a1, col_a2 = st.columns(2)
  with col_a1:
    p["stock_balance"] = st.number_input(
        "現有投資部位 (股票/基金) 總值 (元)",
        min_value=0,
        value=safe_int(p.get("stock_balance", 1000000)),
        step=50000,
        format="%d",
        key=f"ez_stk_b_{profile_choice}",
    )
  with col_a2:
    p["cash_balance"] = st.number_input(
        "現有預備金 (活/定存) 總值 (元)",
        min_value=0,
        value=safe_int(p.get("cash_balance", 500000)),
        step=50000,
        format="%d",
        key=f"ez_csh_b_{profile_choice}",
    )

  st.markdown("---")
  st.subheader("退休願景與進階報酬率設定")
  col_t1, col_t2 = st.columns(2)
  with col_t1:
    p["post_retire_expense"] = st.number_input(
        "(退休後) 每月希望生活費 (元)",
        min_value=0,
        value=safe_int(p.get("post_retire_expense", 60000)),
        step=5000,
        format="%d",
        key=f"ez_post_m_{profile_choice}",
    )
  with col_t2:
    p["legacy_target"] = st.number_input(
        "希望最後留下多少資產/遺產 (元)",
        min_value=0,
        value=safe_int(p.get("legacy_target", 2000000)),
        step=500000,
        format="%d",
        key=f"ez_leg_{profile_choice}",
    )

  with st.expander("⚙️ 點此展開【進階資產配置與年報酬率設定】", expanded=False):
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
      stock_ratio_pct = st.slider(
          "每月投資部位分配比例 (%)",
          min_value=0,
          max_value=100,
          value=safe_int(p.get("stock_ratio_pct", DEFAULT_STOCK_RATIO)),
          step=5,
          key=f"ez_stk_ratio_{profile_choice}",
      )
      p["stock_ratio_pct"] = stock_ratio_pct
      cash_ratio_pct = 100 - stock_ratio_pct
      st.caption(f"💡 每月現金部位分配比例自動設為：**{cash_ratio_pct}%**")

      p["salary_growth_rate"] = st.number_input(
          "預估薪資每年成長率 (%)",
          min_value=0.0,
          max_value=20.0,
          value=safe_float(p.get("salary_growth_rate", 1.0)),
          step=0.1,
          format="%.1f",
          key=f"ez_sal_g_{profile_choice}",
      )

    with col_p2:
      p["stock_return"] = st.number_input(
          "投資部位預估年報酬率 (%)",
          min_value=0.0,
          max_value=20.0,
          value=safe_float(p.get("stock_return", 6.0)),
          step=0.5,
          key=f"ez_stk_r_{profile_choice}",
      )
      p["labor_pension_return"] = st.number_input(
          "提領前：勞退基金預估年報酬率 (%)",
          min_value=0.0,
          max_value=20.0,
          value=safe_float(p.get("labor_pension_return", 7.64)),
          step=0.1,
          format="%.2f",
          key=f"ez_lp_ret_pre_{profile_choice}",
      )

    with col_p3:
      p["cash_return"] = st.number_input(
          "預備金/現金預估年報酬率 (%)",
          min_value=0.0,
          max_value=10.0,
          value=safe_float(p.get("cash_return", 2.0)),
          step=0.5,
          key=f"ez_csh_r_{profile_choice}",
      )
      p["labor_pension_reinvest_return"] = st.number_input(
          "提領後：一次請領帳戶投資年報酬率 (%)",
          min_value=0.0,
          max_value=20.0,
          value=safe_float(p.get("labor_pension_reinvest_return", 4.0)),
          step=0.1,
          format="%.1f",
          key=f"ez_lp_ret_post_{profile_choice}",
      )

  st.info("""
  💡 系統預設：
  - **資產使用順序**：扣款優先順序為 **預備金 ➔ 股票 ➔ 勞退金額**。
  - **退休金提領設定**：**60歲** 一次性提領勞退帳戶 與 月領勞保老年給付。
  """)

  st.markdown("---")
  st.subheader("勞退個人專戶累積金額設定")
  col_sub1, col_sub2 = st.columns(2)
  with col_sub1:
    rate_options = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    curr_self_rate = safe_float(p.get("labor_pension_self_rate", 6.0))
    self_rate_idx = (
        rate_options.index(curr_self_rate)
        if curr_self_rate in rate_options
        else 6
    )

    self_rate_in = st.selectbox(
        "自提勞退比例",
        options=rate_options,
        index=self_rate_idx,
        format_func=lambda x: "無自提 (0%)"
        if x == 0
        else f"有自提 ({int(x)}%)",
        key=f"ez_self_rate_{profile_choice}",
    )
    p["labor_pension_self_rate"] = self_rate_in
    p["labor_pension_rate"] = 6.0 + self_rate_in

  est_lp_bal = estimate_labor_pension_balance(
      p["insured_salary"],
      p["labor_pension_self_rate"],
      p["work_years"],
      p.get("labor_pension_return", 7.64),
  )

  with st.expander(
      "🔍 已查到勞退專戶真實金額？點此手動填寫 (若為 0 則由系統自動估算)",
      expanded=False,
  ):
    custom_lp = st.number_input(
        "請輸入目前勞退個人專戶累計金額 (元)",
        min_value=0,
        value=safe_int(p.get("labor_pension_balance", 0)),
        step=10000,
        format="%d",
        key=f"ez_custom_lp_{profile_choice}",
    )

    if custom_lp > 0:
      p["labor_pension_balance"] = custom_lp
    else:
      p["labor_pension_balance"] = est_lp_bal

  with col_sub2:
    p["labor_ins_years"] = p["work_years"]
    p["labor_ins_salary"] = min(LABOR_INS_MAX_SALARY, p["insured_salary"])
    source_tag = "手動填寫" if custom_lp > 0 else "系統自動估算"
    st.caption(
        f"💡 勞退帳戶累積金額 ({source_tag})："
        f" **${safe_float(p['labor_pension_balance']):,.0f}** 元"
    )

  stock_ratio_val = (
      st.session_state.get(
          f"ez_stk_ratio_{profile_choice}", DEFAULT_STOCK_RATIO
      )
      / 100.0
  )
  res = calculate_retirement_goal(p, stock_ratio=stock_ratio_val)

  p["stock_monthly"] = round(res["monthly_stock_required"])
  p["cash_monthly"] = round(res["monthly_cash_required"])

  st.markdown("---")
  st.subheader("📊 即時診斷報告與建議理財規劃")

  cap = res["monthly_savings_capacity"]
  req_total = res["monthly_required_total"]
  diff = cap - req_total

  m1, m2, m3, m4, m5 = st.columns(5)
  m1.metric("目前每月可理財淨結餘", f"${cap:,.0f}")
  m2.metric(
      "退休後預估勞保年金/月", f"${res['estimated_labor_ins_monthly']:,.0f}"
  )
  m3.metric("建議每月投入【投資部位】", f"${res['monthly_stock_required']:,.0f}")
  m4.metric("建議每月投入【現金部位】", f"${res['monthly_cash_required']:,.0f}")

  if diff >= 0:
    m5.metric("💡 可增加每月花費金額", f"${diff:,.0f}", delta=f"+${diff:,.0f}")
  else:
    m5.metric(
        "🚨 需減少每月花費金額",
        f"${abs(diff):,.0f}",
        delta=f"-${abs(diff):,.0f}",
        delta_color="normal",
    )

  st.write("")
  status = res["status"]

  if status == "EXCELLENT":
    st.success(
        "🎉 **完美！現有資產與政府年金已足以支援您的退休目標！**\n\n"
        "您目前不需要額外增加每月投資，現有資產經複利滾存即可輕鬆達成退休與遺產目標。"
    )
  elif status == "GREEN":
    st.success(
        f"🟢 **財務目標非常可行！**\n\n倒推算出您每月只需投入"
        f" **${req_total:,.0f}**（股票 **${res['monthly_stock_required']:,.0f}**"
        f" + 預備金"
        f" **${res['monthly_cash_required']:,.0f}**）。\n\n這僅占您目前每月可理財淨結餘"
        f" (${cap:,.0f}) 的 **{(req_total/cap)*100:.1f}%**，財務彈性相當充足！"
    )
  elif status == "YELLOW":
    st.warning(
        f"⚠️ **財務剛好平衡，需嚴格維持紀律！**\n\n達標每月需投入 **${req_total:,.0f}**，佔了您目前月結餘"
        f" (${cap:,.0f}) 的 **{(req_total/cap)*100:.1f}%**。"
    )
  else:
    gap_m = abs(diff)
    st.error(
        f"🚨 **警示：目前預算無法達成目標！（每月需減少花費金額：${gap_m:,.0f}）**\n\n"
        f"倒推算出您每月需要投入 **${req_total:,.0f}**，但您目前每月扣除生活與旅遊費用後的淨結餘僅有"
        f" **${cap:,.0f}**。"
    )

  sim_results = {}
  for p_name in profiles_to_calc:
    profile_data = st.session_state["user_profiles"][p_name]
    working_df_key = f"df_{p_name}"
    hash_key = f"hash_{p_name}"
    current_hash = json.dumps(profile_data, sort_keys=True)

    if (
        st.session_state.get(hash_key) != current_hash
        or working_df_key not in st.session_state
    ):
      st.session_state[hash_key] = current_hash
      base_df = run_initial_simulation(profile_data)
      st.session_state[working_df_key] = recalculate_dataframe(
          base_df, profile_data
      )

    sim_results[p_name] = st.session_state[working_df_key]

# ==========================================
# 模式 B：專業模式
# ==========================================
else:
  st.markdown("### 步驟 1：填寫預估年報酬率")

  with st.expander(
      "📊 點此查看【歷史參考年化報酬率數據】(0050、台幣定存、勞退基金)",
      expanded=False,
  ):
    ref_col1, ref_col2, ref_col3 = st.columns(3)
    with ref_col1:
      st.markdown("#### 0050 年化報酬率(至2025年底)")
      st.markdown(
          "* **創立至今** (2003~2025)：**12.58%**\n* **近 10 年**："
          " **21.79%**\n* **近 5 年**：**20.99%**"
      )
    with ref_col2:
      st.markdown("#### 台幣定存利率(近年統計)")
      st.markdown(
          "* **近 20 年平均**：**2.10%**\n* **近 10 年平均**："
          " **1.15%**\n* **近 1 年平均**：**1.72%**"
      )
    with ref_col3:
      st.markdown("#### 勞退基金歷史報酬率")
      st.markdown(
          "* **成立迄今**：**7.64%**\n* **近十年**：**8.70%**\n* **近三年**："
          " **14.91%**"
      )

  rate_tabs = st.tabs(
      [f"👤 {p_name} 的報酬率設定" for p_name in profiles_to_calc]
  )
  for idx, p_name in enumerate(profiles_to_calc):
    with rate_tabs[idx]:
      p_target = st.session_state["user_profiles"][p_name]
      r_col1, r_col2 = st.columns(2)
      with r_col1:
        p_target["stock_return"] = dual_input(
            "投資預估年報酬率 (%)",
            f"{p_name}_ret_stock",
            0.0,
            30.0,
            safe_float(p_target.get("stock_return", 6.0)),
            step=0.1,
            format_fmt="%.1f",
        )
        p_target["labor_pension_return"] = dual_input(
            "提領前：勞退基金預估年報酬率 (%)",
            f"{p_name}_ret_lp_pre",
            0.0,
            20.0,
            safe_float(p_target.get("labor_pension_return", 7.64)),
            step=0.1,
            format_fmt="%.1f",
        )
      with r_col2:
        p_target["cash_return"] = dual_input(
            "備用金預估年報酬率 (%)",
            f"{p_name}_ret_cash",
            0.0,
            10.0,
            safe_float(p_target.get("cash_return", 1.8)),
            step=0.1,
            format_fmt="%.1f",
        )
        p_target["labor_pension_reinvest_return"] = dual_input(
            "提領後：退休金帳戶投資年報酬率 (%)",
            f"{p_name}_ret_lp_post",
            0.0,
            20.0,
            safe_float(p_target.get("labor_pension_reinvest_return", 4.0)),
            step=0.1,
            format_fmt="%.1f",
        )

  st.markdown("---")
  st.markdown("### 步驟 2：輸入您的個人基本狀況")
  tab_list = st.tabs(
      [f"👤 {p_name} 的資料設定" for p_name in profiles_to_calc]
  )
  sim_results = {}

  for idx, p_name in enumerate(profiles_to_calc):
    with tab_list[idx]:
      p = st.session_state["user_profiles"][p_name]
      col_c1, col_c2 = st.columns(2)
      with col_c1:
        st.markdown("#### 1. 年齡與月薪資")
        p["current_age"] = dual_input(
            "您目前的年齡 (歲)",
            f"{p_name}_cur_age",
            20,
            70,
            safe_int(p.get("current_age", 30)),
        )
        p["retire_age"] = dual_input(
            "預計幾歲停止工作/退休？",
            f"{p_name}_ret_age",
            40,
            75,
            safe_int(p.get("retire_age", 60)),
        )
        p["insured_salary"] = dual_input(
            "目前每月薪資 (元)",
            f"{p_name}_ins_sal",
            15000,
            150000,
            safe_int(p.get("insured_salary", 50000)),
            step=1000,
        )
        p["annual_bonus"] = dual_input(
            "預估每年獎金/年終總額 (元)",
            f"{p_name}_ann_bonus",
            0,
            5000000,
            safe_int(p.get("annual_bonus", 100000)),
            step=10000,
        )
      with col_c2:
        st.markdown("#### 2. 每月投資與生活支出預算")
        p["stock_monthly"] = dual_input(
            "每月定額投資金額 (元)",
            f"{p_name}_stk_m",
            0,
            1000000,
            safe_int(p.get("stock_monthly", 20000)),
            step=1000,
        )
        p["cash_monthly"] = dual_input(
            "每月存入備用金/定存 (元)",
            f"{p_name}_csh_m",
            0,
            1000000,
            safe_int(p.get("cash_monthly", 10000)),
            step=1000,
        )
        p["pre_retire_annual_expense"] = dual_input(
            "退休前預計【每年】享樂/旅遊/彈性支出 (元)",
            f"{p_name}_pre_exp",
            0,
            2000000,
            safe_int(p.get("pre_retire_annual_expense", 120000)),
            step=10000,
        )
        p["post_retire_expense"] = dual_input(
            "退休後希望【每月】有多少生活費？ (元)",
            f"{p_name}_exp",
            10000,
            1000000,
            safe_int(p.get("post_retire_expense", 60000)),
            step=2000,
        )

      with st.expander(
          "⚙️ 點此展開【進階詳細設定】(現有存款金額、勞保年資與扣款順序)",
          expanded=False,
      ):
        ex_col1, ex_col2 = st.columns(2)
        with ex_col1:
          st.markdown("##### 💰 目前已累積的資產餘額")
          p["labor_pension_balance"] = dual_input(
              "勞退個人專戶目前累積金額 (元)",
              f"{p_name}_lp_bal",
              0,
              20000000,
              safe_int(p.get("labor_pension_balance", 0)),
              step=10000,
          )
          p["stock_balance"] = dual_input(
              "目前投資部位總額 (元)",
              f"{p_name}_stk_bal",
              0,
              100000000,
              safe_int(p.get("stock_balance", 1000000)),
              step=50000,
          )
          p["cash_balance"] = dual_input(
              "目前備用金/定存總額 (元)",
              f"{p_name}_csh_bal",
              0,
              100000000,
              safe_int(p.get("cash_balance", 500000)),
              step=50000,
          )
        with ex_col2:
          st.markdown("##### 🛡️ 勞保與提撥率細節")
          p["labor_ins_years"] = dual_input(
              "目前勞保已投保年資 (年)",
              f"{p_name}_li_yrs",
              0,
              40,
              safe_int(p.get("labor_ins_years", 5)),
          )
          p["labor_ins_salary"] = dual_input(
              "勞保最高 60 個月平均投保薪資",
              f"{p_name}_li_sal",
              10000,
              LABOR_INS_MAX_SALARY,
              safe_int(p.get("labor_ins_salary", LABOR_INS_MAX_SALARY)),
              step=1000,
          )
          p["salary_growth_rate"] = dual_input(
              "預估薪資每年成長率 (%)",
              f"{p_name}_sal_growth",
              0.0,
              10.0,
              safe_float(p.get("salary_growth_rate", 1.0)),
              step=0.1,
              format_fmt="%.1f",
          )
          p["labor_pension_rate"] = dual_input(
              "勞退提撥率 (雇主6% + 個人自提%)",
              f"{p_name}_lp_rate",
              6,
              12,
              safe_int(p.get("labor_pension_rate", 12)),
              step=1,
          )
          p["labor_pension_claim_age"] = dual_input(
              "勞退開始提領年齡 (法定≥60歲)",
              f"{p_name}_lp_claim",
              60,
              100,
              safe_int(p.get("labor_pension_claim_age", 60)),
          )
          p["labor_ins_claim_age"] = dual_input(
              "勞保年金開始提領年齡 (60~65歲)",
              f"{p_name}_li_claim",
              60,
              65,
              safe_int(p.get("labor_ins_claim_age", 60)),
          )
          p["drawdown_priority"] = st.multiselect(
              "資產扣款優先順序：",
              options=["備用金", "股票", "勞退金額"],
              default=p.get(
                  "drawdown_priority", ["備用金", "股票", "勞退金額"]
              ),
              key=f"{p_name}_drawdown_prio",
          )

      working_df_key = f"df_{p_name}"
      hash_key = f"hash_{p_name}"
      current_hash = json.dumps(p, sort_keys=True)

      if (
          st.session_state.get(hash_key) != current_hash
          or working_df_key not in st.session_state
      ):
        st.session_state[hash_key] = current_hash
        base_df = run_initial_simulation(p)
        st.session_state[working_df_key] = recalculate_dataframe(base_df, p)

      sim_results[p_name] = st.session_state[working_df_key]

# ==========================================
# 共同結果展示區 (圖表與指標卡片)
# ==========================================
st.markdown("---")
st.markdown("## 📊 退休資產成果分析")

if len(profiles_to_calc) == 1:
  master_df = sim_results[profiles_to_calc[0]].copy()
else:
  df1 = sim_results[profiles_to_calc[0]]
  df2 = sim_results[profiles_to_calc[1]]
  master_df = df1[["年齡", "狀態"]].copy()
  master_df["累計勞退金額"] = df1["累計勞退金額"] + df2["累計勞退金額"]
  master_df["累計股票金額"] = df1["累計股票金額"] + df2["累計股票金額"]
  master_df["累計備用金"] = df1["累計備用金"] + df2["累計備用金"]
  master_df["累計總資產"] = df1["累計總資產"] + df2["累計總資產"]

retire_age_ref = safe_int(
    st.session_state["user_profiles"][profiles_to_calc[0]]["retire_age"]
)
life_exp_ref = safe_int(
    st.session_state["user_profiles"][profiles_to_calc[0]]["life_expectancy"]
)

claim_60_idx = master_df[master_df["年齡"] == 60]
claim_ret_idx = master_df[master_df["年齡"] == retire_age_ref]

val_at_retire = (
    claim_ret_idx["累計總資產"].values[0] if len(claim_ret_idx) > 0 else 0
)
val_at_60 = claim_60_idx["累計總資產"].values[0] if len(claim_60_idx) > 0 else 0

row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
with row1_col1:
  st.metric(f"🛑 退休時總資產 ({retire_age_ref}歲)", f"${val_at_retire:,.0f}")
with row1_col2:
  st.metric("📈 60歲時滾動總資產", f"${val_at_60:,.0f}")
with row1_col3:
  total_annuity_monthly = 0
  for p_name in profiles_to_calc:
    p = st.session_state["user_profiles"][p_name]
    tot_yrs = safe_float(p["labor_ins_years"]) + max(
        0, safe_int(p["retire_age"]) - safe_int(p["current_age"])
    )
    total_annuity_monthly += calc_labor_ins_annuity(
        p["labor_ins_salary"], tot_yrs, p["labor_ins_claim_age"]
    )
  st.metric("💵 預估勞保月領年金", f"${total_annuity_monthly:,.0f} /月")
with row1_col4:
  end_val = master_df.iloc[-1]["累計總資產"]
  st.metric(
      f"🏁 {life_exp_ref}歲終點總資產",
      f"${end_val:,.0f}",
      delta_color="normal" if end_val >= 0 else "inverse",
  )

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=master_df["年齡"],
        y=master_df["累計勞退金額"],
        mode="lines",
        name="勞退金額",
        line=dict(color="#2563EB"),
    )
)
fig.add_trace(
    go.Scatter(
        x=master_df["年齡"],
        y=master_df["累計股票金額"],
        mode="lines",
        name="投資股票/基金",
        line=dict(color="#059669"),
    )
)
fig.add_trace(
    go.Scatter(
        x=master_df["年齡"],
        y=master_df["累計總資產"],
        mode="lines+markers",
        name="總資產趨勢線",
        line=dict(color="#1E1B4B", width=3),
    )
)
fig.add_trace(
    go.Scatter(
        x=master_df["年齡"],
        y=master_df["累計備用金"],
        mode="lines",
        name="備用現金/負債 (右軸)",
        line=dict(color="#D97706", width=2, dash="dot"),
        yaxis="y2",
    )
)
fig.add_hline(
    y=0, line_dash="solid", line_color="rgba(239, 68, 68, 0.5)"
)
fig.add_vline(x=retire_age_ref, line_dash="dash", line_color="red")
fig.add_vline(x=60, line_dash="dash", line_color="green")

fig.update_layout(
    xaxis=dict(title="年齡 (歲)"),
    yaxis=dict(title="主要資產金額 (TWD)", side="left"),
    yaxis2=dict(
        title="備用現金/累積負債 (TWD)", side="right", overlaying="y", showgrid=False
    ),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=30, b=20),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
with st.expander(
    "📑 點此展開/隱藏【逐年詳細數據表格與匯出】", expanded=False
):
  # 💡 1. 在夫妻模式下，選單自動動態加入「夫+妻 合併」選項
  detail_options = list(profiles_to_calc)
  if len(profiles_to_calc) > 1:
    detail_options.append("夫+妻 合併")

  selected_detail_profile = st.selectbox(
      "選擇欲檢視/編輯的明細對象", detail_options
  )

  # 💡 2. 處理「夫+妻 合併」檢視邏輯
  if selected_detail_profile == "夫+妻 合併":
    df1 = sim_results[profiles_to_calc[0]].copy()
    df2 = sim_results[profiles_to_calc[1]].copy()

    # 建立合併後的 Dataframe
    display_df = df1[["年齡", "狀態"]].copy()
    display_df["投保級距(雙人合計)"] = df1["投保級距"] + df2["投保級距"]
    display_df["股票每月投入"] = (
        df1["股票每月投入"] + df2["股票每月投入"]
    )
    display_df["備用金每月投入(含年金併入)"] = (
        df1["備用金每月投入(含年金併入)"]
        + df2["備用金每月投入(含年金併入)"]
    )
    display_df["年度獎金/年終注入 (元)"] = (
        df1.get("年度獎金/年終注入 (元)", 0)
        + df2.get("年度獎金/年終注入 (元)", 0)
    )
    display_df["退休月生活費"] = (
        df1["退休月生活費"] + df2["退休月生活費"]
    )
    display_df["當年額外大額支出 (元)"] = (
        df1["當年額外大額支出 (元)"]
        + df2["當年額外大額支出 (元)"]
    )
    display_df["大額支出備註/用途"] = df1["大額支出備註/用途"]

    # 資產類別加總
    display_df["累計勞退金額"] = (
        df1["累計勞退金額"] + df2["累計勞退金額"]
    )
    display_df["累計股票金額"] = (
        df1["累計股票金額"] + df2["累計股票金額"]
    )
    display_df["累計備用金"] = df1["累計備用金"] + df2["累計備用金"]
    display_df["累計總資產"] = df1["累計總資產"] + df2["累計總資產"]

    st.info("💡 **提示**：目前顯示為【家庭合併數據】唯讀模式。如需修改細項金額，請切換至「夫」或「妻」個人選單進行編輯。")

    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "投保級距(雙人合計)": st.column_config.NumberColumn(format="$%d"),
            "股票每月投入": st.column_config.NumberColumn(format="$%d"),
            "備用金每月投入(含年金併入)": st.column_config.NumberColumn(format="$%d"),
            "年度獎金/年終注入 (元)": st.column_config.NumberColumn(format="$%d"),
            "退休月生活費": st.column_config.NumberColumn(format="$%d"),
            "當年額外大額支出 (元)": st.column_config.NumberColumn(format="$%d"),
            "累計勞退金額": st.column_config.NumberColumn(format="$%d"),
            "累計股票金額": st.column_config.NumberColumn(format="$%d"),
            "累計備用金": st.column_config.NumberColumn(format="$%d"),
            "累計總資產": st.column_config.NumberColumn(format="$%d"),
        },
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 下載家庭合併逐年明細 CSV 表格",
        data=csv_data,
        file_name="家庭合併_退休規劃明細.csv",
        mime="text/csv",
    )

  # 💡 3. 單人（夫 或 妻 或 個人）互動編輯邏輯
  else:
    working_key = f"df_{selected_detail_profile}"
    profile_obj = st.session_state["user_profiles"][selected_detail_profile]

    def on_table_edited():
      editor_key = f"editor_{selected_detail_profile}"
      if (
          editor_key in st.session_state
          and "edited_rows" in st.session_state[editor_key]
      ):
        changes_dict = st.session_state[editor_key]["edited_rows"]
        if changes_dict:
          curr_df = st.session_state[working_key].copy()
          for r_idx_str, row_changes in changes_dict.items():
            r_idx = int(r_idx_str)
            for col_name, new_val in row_changes.items():
              curr_df.at[r_idx, col_name] = (
                  safe_float(new_val)
                  if isinstance(curr_df.at[r_idx, col_name], (int, float))
                  else new_val
              )
          st.session_state[working_key] = recalculate_dataframe(
              curr_df, profile_obj
          )

    edited_df = st.data_editor(
        st.session_state[working_key],
        num_rows="fixed",
        use_container_width=True,
        disabled=["累計勞退金額", "累計股票金額", "累計備用金", "累計總資產"],
        column_config={
            "投保級距": st.column_config.NumberColumn("投保級距", format="$%d"),
            "股票每月投入": st.column_config.NumberColumn("股票每月投入", format="$%d"),
            "備用金每月投入(含年金併入)": st.column_config.NumberColumn("備用金每月投入", format="$%d"),
            "年度獎金/年終注入 (元)": st.column_config.NumberColumn("年度獎金/年終注入 (元)", format="$%d"),
            "退休月生活費": st.column_config.NumberColumn("退休月生活費", format="$%d"),
            "當年額外大額支出 (元)": st.column_config.NumberColumn("當年額外大額支出 (元)", format="$%d"),
            "大額支出備註/用途": st.column_config.TextColumn("大額支出備註/用途"),
            "累計勞退金額": st.column_config.NumberColumn("累計勞退金額", format="$%d"),
            "累計股票金額": st.column_config.NumberColumn("累計股票金額", format="$%d"),
            "累計備用金": st.column_config.NumberColumn("累計備用金", format="$%d"),
            "累計總資產": st.column_config.NumberColumn("累計總資產", format="$%d"),
        },
        key=f"editor_{selected_detail_profile}",
        on_change=on_table_edited,
    )

    csv_data = edited_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label=f"📥 下載 {selected_detail_profile} 之逐年明細 CSV 表格",
        data=csv_data,
        file_name=f"{selected_detail_profile}_退休規劃明細.csv",
        mime="text/csv",
    )
