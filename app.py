import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Page Config
st.set_page_config(
    page_title="Retirement Planning System present by Wayne SHIH",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .author-sub { font-size: 0.95rem; font-weight: 500; color: #6B7280; font-style: italic; margin-bottom: 0.6rem; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 1.5rem; }
    .stNumberInput input { font-weight: 600; }
</style>
""",
    unsafe_allow_html=True,
)


# Helper: Fully Synchronized Dual Input (Slider <-> Number Input)
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


# Labor Insurance Salary Grade Table
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


def get_labor_pension_level(salary):
  for lvl in LABOR_PENSION_LEVELS:
    if salary <= lvl:
      return lvl
  return LABOR_PENSION_LEVELS[-1]


# Default Profiles
DEFAULT_PROFILES = {
    "夫": {
        "current_age": 30,
        "retire_age": 55,
        "labor_pension_claim_age": 60,
        "labor_ins_claim_age": 60,
        "labor_pension_balance": 500000,
        "insured_salary": 105600,
        "salary_growth_rate": 2.0,
        "labor_pension_rate": 12.0,
        "labor_pension_return": 7.64,
        "labor_pension_reinvest_return": 5.0,
        "stock_balance": 4000000,
        "stock_monthly": 35000,
        "stock_return": 6.0,
        "cash_balance": 2000000,
        "cash_monthly": 12000,
        "cash_return": 2.0,
        "labor_ins_years": 10,
        "labor_ins_salary": 45800,
        "post_retire_expense": 100000,
        "drawdown_priority": ["備用金", "股票", "勞退金額"],
    },
    "妻": {
        "current_age": 30,
        "retire_age": 55,
        "labor_pension_claim_age": 60,
        "labor_ins_claim_age": 60,
        "labor_pension_balance": 500000,
        "insured_salary": 55400,
        "salary_growth_rate": 2.0,
        "labor_pension_rate": 12.0,
        "labor_pension_return": 7.64,
        "labor_pension_reinvest_return": 5.0,
        "stock_balance": 2500000,
        "stock_monthly": 20000,
        "stock_return": 6.0,
        "cash_balance": 1500000,
        "cash_monthly": 8000,
        "cash_return": 2.0,
        "labor_ins_years": 10,
        "labor_ins_salary": 45800,
        "post_retire_expense": 40000,
        "drawdown_priority": ["備用金", "股票", "勞退金額"],
    },
}


def calc_labor_ins_annuity(avg_salary, total_years, claim_age):
  base_monthly = avg_salary * total_years * 0.0155
  diff_years = claim_age - 65
  adj_factor = max(0.6, min(1.2, 1.0 + (diff_years * 0.04)))
  return base_monthly * adj_factor


# Initial Base Simulation Engine
def run_initial_simulation(p):
  end_age = 85
  records = []
  cur_salary = p["insured_salary"]

  for age in range(p["current_age"], end_age + 1):
    is_working = age < p["retire_age"]
    status = "工作中" if is_working else "已退休"

    if is_working and age > p["current_age"]:
      cur_salary = cur_salary * (1 + p["salary_growth_rate"] / 100.0)

    cur_level = get_labor_pension_level(cur_salary)

    if is_working:
      pension_rate = p["labor_pension_rate"]
      stock_m = p["stock_monthly"]
      cash_m = p["cash_monthly"]
      expense = 0
    else:
      pension_rate = 0.0
      stock_m = 0
      cash_m = 0
      expense = p["post_retire_expense"]

    labor_ins_annuity_monthly = 0
    if age >= p["labor_ins_claim_age"]:
      service_years = p["labor_ins_years"] + max(
          0, p["retire_age"] - p["current_age"]
      )
      labor_ins_annuity_monthly = calc_labor_ins_annuity(
          p["labor_ins_salary"], service_years, p["labor_ins_claim_age"]
      )

    eff_pension_ret = (
        p["labor_pension_return"]
        if age < p["labor_pension_claim_age"]
        else p["labor_pension_reinvest_return"]
    )

    records.append({
        "年齡": age,
        "狀態": status,
        "投保級距": round(cur_level),
        "當期提撥率(%)": pension_rate,
        "勞退當期報酬率(%)": eff_pension_ret,
        "股票每月投入": stock_m,
        "當期股票報酬率(%)": p["stock_return"],
        "備用金每月投入(含年金併入)": round(
            cash_m + labor_ins_annuity_monthly
        ),
        "備用金報酬率(%)": p["cash_return"],
        "退休月生活費": expense,
        "當頁額外大額支出 (元)": 0,
        "大額支出備註/用途": "",
        "累計勞退金額": 0,
        "累計股票金額": 0,
        "累計備用金": 0,
        "累計總資產": 0,
    })
  return pd.DataFrame(records)


# Dynamic Recalculation Engine
def recalculate_dataframe(df, p):
  cur_pension = p["labor_pension_balance"]
  cur_stock = p["stock_balance"]
  cur_cash = p["cash_balance"]

  updated_rows = []
  priority = p.get("drawdown_priority", ["備用金", "股票", "勞退金額"])
  claim_age = p.get("labor_pension_claim_age", 60)

  for _, row in df.iterrows():
    age = int(row["年齡"])
    level = float(row["投保級距"])
    pension_rate = float(row["當期提撥率(%)"])
    pension_ret = float(row["勞退當期報酬率(%)"])
    stock_m = float(row["股票每月投入"])
    stock_ret = float(row["當期股票報酬率(%)"])
    cash_m = float(row["備用金每月投入(含年金併入)"])
    cash_ret = float(row["備用金報酬率(%)"])
    monthly_expense = float(row["退休月生活費"])
    extra_expense = float(row.get("當頁額外大額支出 (元)", 0))

    # 1. Labor Pension Accumulation / Growth
    pension_contrib = level * (pension_rate / 100.0) * 12
    cur_pension = (cur_pension + pension_contrib) * (1 + pension_ret / 100.0)

    # 2. Total Expense Drawdown (Monthly Expense * 12 + Extra Expense)
    tot_annual_draw = (monthly_expense * 12) + extra_expense
    if tot_annual_draw > 0:
      rem_expense = tot_annual_draw

      for source in priority:
        if rem_expense <= 0:
          break

        if source == "備用金":
          draw = min(cur_cash, rem_expense)
          cur_cash -= draw
          rem_expense -= draw
        elif source == "股票":
          draw = min(cur_stock, rem_expense)
          cur_stock -= draw
          rem_expense -= draw
        elif source == "勞退金額":
          if age >= claim_age:
            draw = min(cur_pension, rem_expense)
            cur_pension -= draw
            rem_expense -= draw

    # 3. Stock & Cash Asset Growth
    cur_stock = (cur_stock + stock_m * 12) * (1 + stock_ret / 100.0)
    cur_cash = (cur_cash + cash_m * 12) * (1 + cash_ret / 100.0)
    tot_asset = cur_pension + cur_stock + cur_cash

    row_dict = row.to_dict()
    row_dict["累計勞退金額"] = round(cur_pension)
    row_dict["累計股票金額"] = round(cur_stock)
    row_dict["累計備用金"] = round(cur_cash)
    row_dict["累計總資產"] = round(tot_asset)
    updated_rows.append(row_dict)

  return pd.DataFrame(updated_rows)


# UI Starts
st.markdown(
    '<div class="main-header">Retirement Planning System</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="author-sub">present by Wayne SHIH</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-header">試算勞退新制、股票投資、備用現金與勞保年金，掌握退休資產變化</div>',
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.header("⚙️ 模式與檔案管理")
calc_mode = st.sidebar.radio("選擇計算模式", ["個人獨立規劃", "夫妻共同規劃"])

st.sidebar.subheader("💾 儲存/讀取評估方案")
scenario_name = st.sidebar.text_input("方案名稱", "預設規劃案")

if "user_profiles" not in st.session_state:
  st.session_state["user_profiles"] = DEFAULT_PROFILES.copy()

if st.sidebar.button("💾 儲存目前規劃設定"):
  saved_data = json.dumps(
      st.session_state["user_profiles"], ensure_ascii=False, indent=2
  )
  st.sidebar.download_button(
      label="📥 下載 JSON 設定檔",
      data=saved_data,
      file_name=f"{scenario_name}_退休規劃.json",
      mime="application/json",
  )

uploaded_file = st.sidebar.file_uploader(
    "📤 讀取已存方案 (JSON)", type=["json"]
)
if uploaded_file is not None:
  try:
    st.session_state["user_profiles"] = json.load(uploaded_file)
    st.sidebar.success("成功載入方案！")
  except Exception:
    st.sidebar.error("載入失敗，檔案格式不符。")

profiles_to_calc = ["個人"] if calc_mode == "個人獨立規劃" else ["夫", "妻"]
tab_list = st.tabs([f"👤 {p_name} 參數設定" for p_name in profiles_to_calc])

sim_results = {}

for idx, p_name in enumerate(profiles_to_calc):
  if p_name not in st.session_state["user_profiles"]:
    st.session_state["user_profiles"][p_name] = DEFAULT_PROFILES["夫"].copy()

  with tab_list[idx]:
    p = st.session_state["user_profiles"][p_name]
    st.markdown(f"### 📋 {p_name} 基本參數配置")

    col_a, col_b = st.columns(2)
    with col_a:
      st.subheader("1. 年齡與退休時間規劃")
      p["current_age"] = dual_input(
          "目前年齡", f"{p_name}_cur_age", 20, 70, p.get("current_age", 35)
      )
      p["retire_age"] = dual_input(
          "預計停止工作年齡", f"{p_name}_ret_age", 40, 75, p.get("retire_age", 55)
      )
      p["labor_pension_claim_age"] = dual_input(
          "勞退新制開始提領年齡 (法定≥60歲)",
          f"{p_name}_lp_claim",
          60,
          75,
          p.get("labor_pension_claim_age", 60),
      )
      p["labor_ins_claim_age"] = dual_input(
          "勞保老年年金開始提領年齡 (60~65歲)",
          f"{p_name}_li_claim",
          60,
          65,
          p.get("labor_ins_claim_age", 60),
      )

      st.subheader("2. 薪資與勞工退休金新制")
      p["insured_salary"] = dual_input(
          "目前月投保薪資級距 (元)",
          f"{p_name}_ins_sal",
          15000,
          150000,
          p.get("insured_salary", 105600),
          step=1000,
      )
      p["salary_growth_rate"] = dual_input(
          "預估薪資年成長率 (%)",
          f"{p_name}_sal_growth",
          0.0,
          10.0,
          p.get("salary_growth_rate", 2.0),
          step=0.1,
          format_fmt="%.1f",
      )
      p["labor_pension_balance"] = dual_input(
          "勞退新制目前累計金額 (元)",
          f"{p_name}_lp_bal",
          0,
          20000000,
          p.get("labor_pension_balance", 809477),
          step=10000,
      )
      p["labor_pension_rate"] = dual_input(
          "勞退提撥率 (雇主+自提 %)",
          f"{p_name}_lp_rate",
          6.0,
          12.0,
          p.get("labor_pension_rate", 12.0),
          step=1.0,
      )
      p["labor_pension_return"] = dual_input(
          "提領前：勞退基金預估年報酬率 (%)",
          f"{p_name}_lp_ret",
          0.0,
          15.0,
          p.get("labor_pension_return", 7.64),
          step=0.01,
          format_fmt="%.2f",
      )
      p["labor_pension_reinvest_return"] = dual_input(
          "提領後：一次請領帳戶投資年報酬率 (%)",
          f"{p_name}_lp_reinv_ret",
          0.0,
          20.0,
          p.get("labor_pension_reinvest_return", 5.0),
          step=0.1,
          format_fmt="%.1f",
      )

    with col_b:
      st.subheader("3. 投資股票")
      p["stock_balance"] = dual_input(
          "股票目前累計金額 (元)",
          f"{p_name}_stk_bal",
          0,
          50000000,
          p.get("stock_balance", 5000000),
          step=50000,
      )
      p["stock_monthly"] = dual_input(
          "股票每月投入金額 (元)",
          f"{p_name}_stk_m",
          0,
          300000,
          p.get("stock_monthly", 45000),
          step=1000,
      )
      p["stock_return"] = dual_input(
          "股票預估年報酬率 (%)",
          f"{p_name}_stk_ret",
          0.0,
          20.0,
          p.get("stock_return", 6.0),
          step=0.1,
          format_fmt="%.1f",
      )

      st.subheader("4. 備用現金與定存")
      p["cash_balance"] = dual_input(
          "備用金目前累計金額 (元)",
          f"{p_name}_csh_bal",
          0,
          20000000,
          p.get("cash_balance", 2000000),
          step=50000,
      )
      p["cash_monthly"] = dual_input(
          "備用金每月投入金額 (元)",
          f"{p_name}_csh_m",
          0,
          100000,
          p.get("cash_monthly", 12000),
          step=1000,
      )
      p["cash_return"] = dual_input(
          "備用金預估年報酬率 (%)",
          f"{p_name}_csh_ret",
          0.0,
          10.0,
          p.get("cash_return", 2.0),
          step=0.1,
          format_fmt="%.1f",
      )

      st.subheader("5. 勞保老年給付與退休生活費")
      p["labor_ins_years"] = dual_input(
          "目前勞保投保年資 (年)",
          f"{p_name}_li_yrs",
          0,
          40,
          p.get("labor_ins_years", 10),
      )
      p["labor_ins_salary"] = dual_input(
          "勞保平均最高月投保薪資 (上限45800元)",
          f"{p_name}_li_sal",
          10000,
          45800,
          p.get("labor_ins_salary", 45800),
          step=1000,
      )
      p["post_retire_expense"] = dual_input(
          "退休後預估每月生活費 (元)",
          f"{p_name}_exp",
          10000,
          300000,
          p.get("post_retire_expense", 50000),
          step=2000,
      )

      st.markdown("**退休生活費及大額支出扣算順序 (依序排列)：**")
      p["drawdown_priority"] = st.multiselect(
          "請依序選擇扣款資產項目（第一個選取的將最優先扣抵）",
          options=["備用金", "股票", "勞退金額"],
          default=p.get("drawdown_priority", ["備用金", "股票", "勞退金額"]),
          key=f"{p_name}_drawdown_prio",
      )

    # Session State Management for Editable Table
    working_df_key = f"df_{p_name}"
    hash_key = f"hash_{p_name}"
    current_hash = json.dumps(p, sort_keys=True)

    # If parameters change, reset base dataframe
    if (
        st.session_state.get(hash_key) != current_hash
        or working_df_key not in st.session_state
    ):
      st.session_state[hash_key] = current_hash
      base_df = run_initial_simulation(p)
      st.session_state[working_df_key] = recalculate_dataframe(base_df, p)

    # Store in dict for master overview
    sim_results[p_name] = st.session_state[working_df_key]

# Dashboard Overview
st.markdown("---")
st.markdown("## 📊 退休資產試算總覽與里程碑比較")

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

row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
retire_age_ref = st.session_state["user_profiles"][profiles_to_calc[0]][
    "retire_age"
]
claim_60_idx = master_df[master_df["年齡"] == 60]
claim_ret_idx = master_df[master_df["年齡"] == retire_age_ref]

val_at_retire = (
    claim_ret_idx["累計總資產"].values[0] if len(claim_ret_idx) > 0 else 0
)
val_at_60 = claim_60_idx["累計總資產"].values[0] if len(claim_60_idx) > 0 else 0

with row1_col1:
  st.metric(f"停止工作時總資產 ({retire_age_ref}歲)", f"${val_at_retire:,.0f}")
with row1_col2:
  st.metric("到期繼續複利總資產 (60歲)", f"${val_at_60:,.0f}")
with row1_col3:
  total_annuity_monthly = 0
  for p_name in profiles_to_calc:
    p = st.session_state["user_profiles"][p_name]
    tot_yrs = p["labor_ins_years"] + max(0, p["retire_age"] - p["current_age"])
    total_annuity_monthly += calc_labor_ins_annuity(
        p["labor_ins_salary"], tot_yrs, p["labor_ins_claim_age"]
    )
  st.metric("預估勞保月領年金總額", f"${total_annuity_monthly:,.0f} /月")
with row1_col4:
  end_val = master_df.iloc[-1]["累計總資產"]
  st.metric("85歲終點預估剩餘總資產", f"${end_val:,.0f}")

# Chart
st.subheader("📈 退休累積資產增長趨勢圖 (動態即時連動)")
fig = go.Figure()

# 主要 Y 軸（左側）：累計勞退金額、累計股票金額、累計總資產
fig.add_trace(
    go.Scatter(
        x=master_df["年齡"],
        y=master_df["累計勞退金額"],
        mode="lines",
        name="勞退金額 (含請領後投資)",
        line=dict(color="#2563EB"),
    )
)
fig.add_trace(
    go.Scatter(
        x=master_df["年齡"],
        y=master_df["累計股票金額"],
        mode="lines",
        name="投資股票",
        line=dict(color="#059669"),
    )
)
fig.add_trace(
    go.Scatter(
        x=master_df["年齡"],
        y=master_df["累計總資產"],
        mode="lines+markers",
        name="總資產線",
        line=dict(color="#1E1B4B", width=3),
    )
)

# 獨立 Y 軸（右側）：備用現金（設定 yaxis='y2'）
fig.add_trace(
    go.Scatter(
        x=master_df["年齡"],
        y=master_df["累計備用金"],
        mode="lines",
        name="備用現金 (右軸)",
        line=dict(color="#D97706", width=2, dash="dot"),
        yaxis="y2",
    )
)

fig.add_vline(
    x=retire_age_ref,
    line_dash="dash",
    line_color="red",
    annotation_text=f"停止工作 ({retire_age_ref}歲)",
)
fig.add_vline(
    x=60,
    line_dash="dash",
    line_color="green",
    annotation_text="勞退請領轉自營 (60歲)",
)

# 設定雙 Y 軸配置
fig.update_layout(
    xaxis=dict(title="年齡"),
    yaxis=dict(title="主要資產金額 (TWD)", side="left"),
    yaxis2=dict(
        title="備用現金金額 (TWD)",
        side="right",
        overlaying="y",
        showgrid=False,
    ),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=30, b=20),
)
st.plotly_chart(fig, use_container_width=True)

# Interactive Data Table with Real-time Recalculation Callback
st.markdown("---")
st.subheader("📑 逐年明細 (雙擊可修改參數)")
selected_detail_profile = st.selectbox(
    "選擇欲檢視/編輯的明細對象", profiles_to_calc
)

working_key = f"df_{selected_detail_profile}"
profile_obj = st.session_state["user_profiles"][selected_detail_profile]


# Callback triggered when user edits table cells
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
          curr_df.at[r_idx, col_name] = new_val

      # Perform sequential recalculation
      st.session_state[working_key] = recalculate_dataframe(curr_df, profile_obj)


edited_df = st.data_editor(
    st.session_state[working_key],
    num_rows="fixed",
    use_container_width=True,
    disabled=["累計勞退金額", "累計股票金額", "累計備用金", "累計總資產"],
    column_config={
        "投保級距": st.column_config.NumberColumn("投保級距", format="$%d"),
        "股票每月投入": st.column_config.NumberColumn(
            "股票每月投入", format="$%d"
        ),
        "備用金每月投入(含年金併入)": st.column_config.NumberColumn(
            "備用金每月投入", format="$%d"
        ),
        "退休月生活費": st.column_config.NumberColumn(
            "退休月生活費", format="$%d"
        ),
        "當頁額外大額支出 (元)": st.column_config.NumberColumn(
            "當頁額外大額支出 (元)",
            format="$%d",
            help="請在此處輸入該年齡一次性的大額支出金額 (如: 買車、買房頭期款)",
        ),
        "大額支出備註/用途": st.column_config.TextColumn(
            "大額支出備註/用途", help="可自由紀錄該筆支出的用途，防止未來遺忘"
        ),
        "累計勞退金額": st.column_config.NumberColumn(
            "累計勞退金額", format="$%d"
        ),
        "累計股票金額": st.column_config.NumberColumn(
            "累計股票金額", format="$%d"
        ),
        "累計備用金": st.column_config.NumberColumn(
            "累計備用金", format="$%d"
        ),
        "累計總資產": st.column_config.NumberColumn(
            "累計總資產", format="$%d"
        ),
    },
    key=f"editor_{selected_detail_profile}",
    on_change=on_table_edited,
)

st.subheader("📥 匯出明細資料")
csv_data = edited_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="下載此對象之逐年明細 CSV",
    data=csv_data,
    file_name=f"{selected_detail_profile}_退休規劃明細.csv",
    mime="text/csv",
)
