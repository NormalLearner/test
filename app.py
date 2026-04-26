import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ===================== 页面配置 =====================
st.set_page_config(
    page_title="全国居民收支分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

plt.rcParams['font.sans-serif'] = ["Microsoft YaHei", "SimHei"]
plt.rcParams['axes.unicode_minus'] = False


# ===================== 数据加载 =====================
@st.cache_data
def load_data():
    # 1. 读取收入数据
    income = pd.read_csv("data/全国各省居民收入数据_2021-2025.csv")
    income = income[income["指标"].str.contains("全体居民", na=False)].copy()
    income["年份"] = income["年份"].astype(str)
    income["数值"] = pd.to_numeric(income["数值"], errors="coerce")
    income = income.dropna(subset=["数值"])

    # 2. 读取支出数据
    expense = pd.read_csv("data/全国各省居民支出数据_2021-2025.csv")
    expense = expense[expense["指标"].str.contains("全体居民", na=False)].copy()
    expense["年份"] = expense["年份"].astype(str)
    expense["数值"] = pd.to_numeric(expense["数值"], errors="coerce")
    expense = expense.dropna(subset=["数值"])

    # 3. 直接读取我们生成好的 CSV
    merged = pd.read_csv("data/收支合并数据.csv")
    merged["年份"] = merged["年份"].astype(str)
    merged = merged.dropna()

    return income, expense, merged


# 城乡数据加载函数
@st.cache_data
def load_city_rural_data():
    income = pd.read_csv("data/全国各省居民收入数据_2021-2025.csv")
    expense = pd.read_csv("data/全国各省居民支出数据_2021-2025.csv")

    inc_city = income[income["指标"].str.contains("城镇居民", na=False)].copy()
    inc_rural = income[income["指标"].str.contains("农村居民", na=False)].copy()
    exp_city = expense[expense["指标"].str.contains("城镇居民", na=False)].copy()
    exp_rural = expense[expense["指标"].str.contains("农村居民", na=False)].copy()

    for df in [inc_city, inc_rural, exp_city, exp_rural]:
        df["年份"] = df["年份"].astype(str)
        df["数值"] = pd.to_numeric(df["数值"], errors="coerce")
        # 不在这里 dropna，保留所有年份的行

    return inc_city, inc_rural, exp_city, exp_rural


    return inc_city, inc_rural, exp_city, exp_rural

    for df in [inc_city, inc_rural, exp_city, exp_rural]:
        df["年份"] = df["年份"].astype(str)
        df["数值"] = pd.to_numeric(df["数值"], errors="coerce")
        df.dropna(subset=["数值"], inplace=True)

    return inc_city, inc_rural, exp_city, exp_rural


df_income, df_expense, df_merged = load_data()
inc_city, inc_rural, exp_city, exp_rural = load_city_rural_data()

# ===================== 侧边栏 =====================
with st.sidebar:
    st.title("📊 数据分析面板")
    st.divider()

    data_type = st.radio(
        "选择数据类型",
        ["💰 收入数据", "💸 支出数据", "⚖️ 收支对比", "🏙️ 城乡对比"],
        index=0
    )

    if data_type == "💰 收入数据":
        df = df_income
        years = sorted(df["年份"].unique())
    elif data_type == "💸 支出数据":
        df = df_expense
        years = sorted(df["年份"].unique())
    elif data_type == "🏙️ 城乡对比":
        years = sorted(inc_city["年份"].unique())
    else:
        df = df_merged
        years = sorted(df["年份"].unique())
        if len(years) == 0:
            st.warning("⚠️ 收支对比数据为空")

    selected_year = st.selectbox("选择年份", years)

    if data_type in ["💰 收入数据", "💸 支出数据"]:
        indicators = sorted(df["指标"].unique())
        selected_indicator = st.selectbox("选择指标", indicators)
    else:
        selected_indicator = ""

    sort_order = st.radio("排序方式", ["从高到低", "从低到高"])
    st.divider()
    st.caption("✅ 数据加载完成")

# ===================== 主页面 =====================
# 1. 收入/支出板块逻辑
if data_type in ["💰 收入数据", "💸 支出数据"]:
    type_text = "收入" if data_type == "💰 收入数据" else "支出"
    filtered = df[
        (df["年份"] == selected_year) &
        (df["指标"] == selected_indicator)
        ].copy()

    filtered = filtered.sort_values("数值", ascending=(sort_order == "从低到高"))

    st.markdown(f"""
    <div style="background:#F0F7FF;padding:20px;border-radius:12px;">
        <h1 style="margin:0; color:#111;">📊 全国各省居民人均{type_text}分析</h1>
        <p style="margin:5px 0 0; color:#333;">{selected_year}年 | {selected_indicator}</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"📋 {selected_year}年各省{type_text}数据")
        show_df = filtered.rename(columns={"数值": f"{type_text}（元）"})
        st.dataframe(
            show_df[["省份", f"{type_text}（元）"]],
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.subheader("📈 关键指标")
        if not filtered.empty:
            max_v = int(filtered["数值"].max())
            min_v = int(filtered["数值"].min())
            avg_v = int(filtered["数值"].mean())
            gap = max_v - min_v
        else:
            max_v = min_v = avg_v = gap = 0

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div style="background:#FFFFFF;padding:16px;border-radius:10px;text-align:center;">
                <p style="margin:0;font-size:14px;color:#333;">最高{type_text}</p>
                <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#111;white-space:nowrap;">{max_v} 元</p>
            </div>
            <div style="background:#FFFFFF;padding:16px;border-radius:10px;text-align:center;">
                <p style="margin:0;font-size:14px;color:#333;">最低{type_text}</p>
                <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#111;white-space:nowrap;">{min_v} 元</p>
            </div>
            <div style="background:#FFFFFF;padding:16px;border-radius:10px;text-align:center;">
                <p style="margin:0;font-size:14px;color:#333;">平均{type_text}</p>
                <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#111;white-space:nowrap;">{avg_v} 元</p>
            </div>
            <div style="background:#FFFFFF;padding:16px;border-radius:10px;text-align:center;">
                <p style="margin:0;font-size:14px;color:#333;">地区差距</p>
                <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#c0392b;white-space:nowrap;">{gap} 元</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 柱状图
    st.subheader(f"📊 {selected_year}年各省{type_text}对比")
    if not filtered.empty:
        fig1, ax1 = plt.subplots(figsize=(12, 9))
        bars = ax1.barh(filtered["省份"], filtered["数值"], color="#4A90E2")
        ax1.set_xlabel(f"{type_text}（元）")
        ax1.grid(axis='x', alpha=0.3)
        st.pyplot(fig1)
        plt.close(fig1)
    else:
        st.warning("⚠️ 当前条件下无数据")

    st.divider()

    # 趋势图
    st.subheader(f"📈 2021-2024 年{type_text}变化趋势")
    provinces = sorted(df["省份"].unique())
    selected_provs = st.multiselect("选择省份对比", provinces, default=provinces[:3])

    if selected_provs:
        fig2, ax2 = plt.subplots(figsize=(11, 5))
        for p in selected_provs:
            sub = df[df["省份"] == p].sort_values("年份")
            ax2.plot(sub["年份"], sub["数值"], marker='o', label=p)

        ax2.set_ylabel(f"{type_text}（元）")
        ax2.legend()
        ax2.grid(alpha=0.3)
        st.pyplot(fig2)
        plt.close(fig2)

    # 对应模块局部分析
    st.divider()
    st.subheader("📝 数据分析解读")
    if data_type == "💰 收入数据":
        st.markdown("""
        1. 区域收入差异显著，东部沿海省市人均收入长期领跑全国，产业与就业优势突出。
        2. 中西部内陆省份收入水平相对偏低，区域发展不均衡特征明显。
        3. 近五年全国各省份收入稳步上行，居民民生保障与收入基础持续改善。
        4. 省份间收入差值较大，反映出我国区域经济梯度发展的现实格局。
        """)
    else:
        st.markdown("""
        1. 居民消费与收入水平高度挂钩，高收入地区消费规模与消费层次更高。
        2. 基础生活消费具备刚性特征，各省份刚需消费支出整体波动较小。
        3. 发达地区消费升级趋势明显，欠发达地区仍以基础生活消费为主。
        4. 历年消费数据稳步增长，体现居民生活品质持续提升。
        """)

# 2. 收支对比板块逻辑
elif data_type == "⚖️ 收支对比":
    st.markdown(f"""
    <div style="background:#F0F7FF;padding:20px;border-radius:12px;">
        <h1 style="margin:0; color:#111;">⚖️ {selected_year}年全国各省居民收支对比分析</h1>
        <p style="margin:5px 0 0; color:#333;">收入、支出、结余、消费率联动分析</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    filtered = df_merged[df_merged["年份"] == selected_year].copy()
    filtered = filtered.sort_values("收支差额", ascending=(sort_order == "从低到高"))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📋 {selected_year}年各省收支数据")
        show_df = filtered.rename(columns={
            "收入": "收入（元）",
            "支出": "支出（元）",
            "收支差额": "结余（元）",
            "消费率(%)": "消费率（%）"
        })
        st.dataframe(show_df, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("📈 关键指标")
        if not filtered.empty:
            max_save = int(filtered["收支差额"].max())
            max_spend_rate = round(filtered["消费率(%)"].max(), 1)
        else:
            max_save = max_spend_rate = 0

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr;gap:10px;">
            <div style="background:#FFFFFF;padding:16px;border-radius:10px;text-align:center;">
                <p style="margin:0;font-size:14px;color:#333;">最高结余</p>
                <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#111;white-space:nowrap;">{max_save} 元</p>
            </div>
            <div style="background:#FFFFFF;padding:16px;border-radius:10px;text-align:center;margin-top:10px;">
                <p style="margin:0;font-size:14px;color:#333;">最高消费率</p>
                <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#c0392b;white-space:nowrap;">{max_spend_rate} %</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader(f"📊 {selected_year}年各省收入-支出散点图")
    if not filtered.empty:
        fig1, ax1 = plt.subplots(figsize=(12, 8))
        ax1.scatter(filtered["收入"], filtered["支出"], color="#2E86AB", s=110, alpha=0.7)

        for i, province in enumerate(filtered["省份"]):
            ax1.annotate(
                province,
                (filtered["收入"].iloc[i], filtered["支出"].iloc[i]),
                fontsize=9,
                xytext=(5, 5),
                textcoords="offset points"
            )

        ax1.set_xlim(left=0)
        ax1.set_ylim(bottom=0)

        max_val = max(filtered["收入"].max(), filtered["支出"].max()) * 1.1
        ax1.plot([0, max_val], [0, max_val], 'r--', alpha=0.6, label="收支平衡线")

        ax1.set_xlabel("人均收入（元）")
        ax1.set_ylabel("人均支出（元）")
        ax1.set_title(f"{selected_year} 各省收入 vs 支出")
        ax1.legend()
        ax1.grid(alpha=0.3)

        st.pyplot(fig1)
        plt.close(fig1)
    else:
        st.warning("⚠️ 当前年份暂无收支数据")

    st.subheader(f"📊 {selected_year}年各省消费率对比")
    if not filtered.empty:
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        bars = ax2.bar(filtered["省份"], filtered["消费率(%)"], color="#F24236")
        ax2.set_ylabel("消费率（%）")
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(axis='y', alpha=0.3)
        st.pyplot(fig2)
        plt.close(fig2)

    # 收支对比局部分析
    st.divider()
    st.subheader("📝 数据分析解读")
    st.markdown("""
    1. 散点图直观呈现各省份收支匹配关系，越靠近平衡线，收支结构越均衡稳定。
    2. 消费率高低反映地区居民消费意愿与储蓄习惯差异，经济活力越高消费意愿越强。
    3. 收支结余额度体现家庭财富积累能力与民生抗风险水平。
    4. 高收入省份可同时兼顾高质量消费与合理储蓄，民生发展综合质量更优。
    """)

# 3. 城乡对比板块 —— 已彻底修复支出无数据
# 3. 城乡对比板块 —— 已删除支出对比，仅保留收入对比
elif data_type == "🏙️ 城乡对比":
    st.markdown(f"""
    <div style="background:#E8F4FF;padding:20px;border-radius:12px;">
        <h1 style="margin:0; color:#111;">🏙️ 全国各省城乡收支对比分析</h1>
        <p style="margin:5px 0 0; color:#333;">城镇 vs 农村 收入差距、城乡比分析</p>
    </div>
    """, unsafe_allow_html=True)

    # 固定为收入对比，删除选择器
    compare_type = "收入对比"
    city_df = inc_city.copy()
    rural_df = inc_rural.copy()
    type_text = "收入"

    # 统一：先按选中年份过滤 → 再清理空值
    city_filtered = city_df[city_df["年份"] == selected_year][["省份", "数值"]].dropna(subset=["数值"])
    rural_filtered = rural_df[rural_df["年份"] == selected_year][["省份", "数值"]].dropna(subset=["数值"])

    # 重命名
    city_filtered = city_filtered.rename(columns={"数值": f"城镇{type_text}"})
    rural_filtered = rural_filtered.rename(columns={"数值": f"农村{type_text}"})

    # 合并数据
    compare_df = pd.merge(city_filtered, rural_filtered, on="省份", how="inner")

    # 计算城乡比
    if not compare_df.empty:
        compare_df[f"城乡{type_text}比"] = (compare_df[f"城镇{type_text}"] / compare_df[f"农村{type_text}"]).round(2)
        compare_df = compare_df.sort_values(f"城乡{type_text}比", ascending=(sort_order == "从低到高"))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"📋 {selected_year}年各省城乡{type_text}数据")
        if not compare_df.empty:
            st.dataframe(compare_df, use_container_width=True, hide_index=True)
        else:
            st.info(f"✅ {selected_year} 年无{type_text}数据，请切换年份查看")

    with col2:
        st.subheader("📈 关键指标")
        if not compare_df.empty:
            max_gap = compare_df[f"城乡{type_text}比"].max()
            avg_gap = compare_df[f"城乡{type_text}比"].mean().round(2)
            min_gap = compare_df[f"城乡{type_text}比"].min()
        else:
            max_gap = avg_gap = min_gap = 0

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div style="background:#FFFFFF;padding:16px;border-radius:10px;text-align:center;">
                <p style="margin:0;font-size:14px;color:#333;">最高城乡比</p>
                <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#c0392b;">{max_gap}</p>
            </div>
            <div style="background:#FFFFFF;padding:16px;border-radius:10px;text-align:center;">
                <p style="margin:0;font-size:14px;color:#333;">平均城乡比</p>
                <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#111;">{avg_gap}</p>
            </div>
            <div style="background:#FFFFFF;padding:16px;border-radius:10px;text-align:center;">
                <p style="margin:0;font-size:14px;color:#333;">最低城乡比</p>
                <p style="margin:4px 0 0;font-size:18px;font-weight:bold;color:#27ae60;">{min_gap}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader(f"📊 {selected_year}年各省城乡{type_text}对比柱状图")
    if not compare_df.empty:
        fig, ax = plt.subplots(figsize=(12, 8))
        x = range(len(compare_df))
        width = 0.35

        ax.bar([i - width / 2 for i in x], compare_df[f"城镇{type_text}"], width, label="城镇", color="#4A90E2")
        ax.bar([i + width / 2 for i in x], compare_df[f"农村{type_text}"], width, label="农村", color="#F24236")

        ax.set_xlabel("省份")
        ax.set_ylabel(f"{type_text}（元）")
        ax.set_title(f"{selected_year}年各省城乡{type_text}对比")
        ax.set_xticks(x)
        ax.set_xticklabels(compare_df["省份"], rotation=45, ha="right")
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info(f"📌 {selected_year} 年无{type_text}数据，无法生成图表")

    # 城乡对比局部分析
    st.divider()
    st.subheader("📝 数据分析解读")
    st.markdown("""
    1. 我国城乡二元发展特征明显，城镇收入水平整体高于农村居民。
    2. 城乡收入比值越小，说明该地区城乡发展越均衡，乡村振兴推进效果越好。
    3. 产业结构差异是城乡收入差距的核心原因，城镇二三产业优势明显。
    4. 缩小城乡收入差距，是实现共同富裕、推动区域协调发展的重要方向。
    """)

# 页脚
st.divider()
st.caption("📊 全国居民收支分析平台 | 数据来源：公开统计数据 | 大数据可视化分析作品")