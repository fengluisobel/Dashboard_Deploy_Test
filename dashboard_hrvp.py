"""
HRVP 战略驾驶舱 v3.0 Pro
老板要求："别告诉我招了多少个前台，我只想知道那个能带队打仗的VP到了没有"

核心定位：
- 只看钱、战略、风险
- 砍掉一半指标，只保留4-5个核心战略指标
- 全集团汇总视图，不可见个人数据
- 月度/季度/年度时间粒度
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys

# 导入品牌色系统
from brand_color_system import get_brand_colors, get_primary_color, get_brand_font


# ==========================================
# HRVP 核心指标定义 (只有5个!)
# ==========================================

HRVP_CORE_METRICS = {
    '关键战略岗位按时达成率_%': {
        'name': '关键战略岗位按时达成率',
        'name_en': 'Critical Role Fill Rate',
        'category': '战略交付',
        'unit': '%',
        'formula': '按时入职的P0级人员数 / P0级招聘计划总数 × 100%',
        'definition': '仅统计对公司战略有重大影响的岗位(如新业务线负责人、首席架构师、核心VP)',
        'boss_comment': '别告诉我招了多少个前台，我只想知道那个能带队打仗的VP到了没有',
        'benchmark': {
            '优秀': '>85%',
            '良好': '75-85%',
            '需改进': '<75%'
        },
        'target': 85.0,
        'review_cadence': 'Monthly',
        'impact': '直接影响公司战略落地速度和业务推进能力'
    },

    '空缺岗位收入损失_万元': {
        'name': '空缺岗位预期收入损失',
        'name_en': 'Revenue Loss Risk / Cost of Vacancy',
        'category': '财务风控',
        'unit': '万元',
        'formula': 'Σ(关键岗位每日预估产值 × 空窗天数) / 10000',
        'definition': '将关键岗位的空窗期转化为财务损失金额，用财务语言说话',
        'boss_comment': '把"招人慢"变成"亏钱"，业务部门就会配合你了',
        'benchmark': {
            '优秀': '<200万',
            '警告': '200-500万',
            '严重': '>500万'
        },
        'target': 200.0,
        'review_cadence': 'Monthly',
        'impact': '量化招聘延误对业务的财务影响，推动资源投入'
    },

    '高绩效员工占比_%': {
        'name': '高绩效员工渠道来源占比',
        'name_en': 'Quality of Source - High Performers',
        'category': '人才质量',
        'unit': '%',
        'formula': '绩效评估为S/A级的新员工人数 / 入职总人数 × 100%',
        'definition': '分析哪种渠道带来的员工在入职一年后表现最好（绩效S/A级）',
        'boss_comment': '不要为了省钱而用便宜渠道，如果猎头招的人能多赚100万，就用猎头',
        'benchmark': {
            '优秀': '>70%',
            '良好': '60-70%',
            '需改进': '<60%'
        },
        'target': 70.0,
        'review_cadence': 'Quarterly',
        'impact': '决定下一年度招聘预算在各渠道的分配策略'
    },

    '人才市场占有率_%': {
        'name': '关键人才市场占有率',
        'name_en': 'Competitor Talent Share',
        'category': '雇主品牌',
        'unit': '%',
        'formula': '来自核心竞对的入职人数 / 核心竞对流失总人数(估算) × 100%',
        'definition': '我们在多大程度上成功挖角了竞争对手的核心人才',
        'boss_comment': 'NPS太虚，我要看我们是否削弱了对手的战斗力',
        'benchmark': {
            '优秀': '>25%',
            '良好': '15-25%',
            '需改进': '<15%'
        },
        'target': 25.0,
        'review_cadence': 'Quarterly',
        'impact': '反映公司在人才市场的竞争力和品牌吸引力'
    },

    '单次招聘成本_元': {
        'name': '单次招聘成本',
        'name_en': 'Cost per Hire',
        'category': '成本控制',
        'unit': '元',
        'formula': '(外部渠道费 + 猎头费 + 内部团队成本) / 入职人数',
        'definition': '招募一名新员工的平均费用，控制总成本但不能为了省钱降低质量',
        'boss_comment': '控制成本但不能为了省钱降低质量',
        'benchmark': {
            '优秀': '<10,000',
            '良好': '10,000-15,000',
            '需改进': '>15,000'
        },
        'target': 10000.0,
        'review_cadence': 'Monthly',
        'impact': '平衡成本效率与人才质量，优化ROI'
    }
}


# ==========================================
# HRVP 看板渲染函数
# ==========================================

def render_hrvp_dashboard(df):
    """
    渲染 HRVP 战略驾驶舱

    Parameters:
    -----------
    df : pandas.DataFrame
        完整招聘数据
    """

    # 品牌色
    colors = get_brand_colors()
    primary_color = get_primary_color()
    font = get_brand_font()

    # ==========================================
    # 顶部：角色标识
    # ==========================================

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {primary_color} 0%, {primary_color}dd 100%);
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 24px rgba(0,0,0,0.12);">
        <h1 style="color: white; margin: 0; font-size: 2rem;">📊 HRVP 战略驾驶舱</h1>
        <p style="color: white; opacity: 0.95; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Strategic Command Center - 只看钱、战略、风险
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # 时间筛选器 (HRVP只能选时间，不能选人员)
    # ==========================================

    st.subheader("📅 时间范围筛选")

    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        time_granularity = st.selectbox(
            "时间粒度",
            ["月度", "季度", "年度"],
            key="hrvp_time_granularity"
        )

    with col_filter2:
        if time_granularity == "月度":
            start_month = st.date_input("开始月份", df['月份'].min(), key="hrvp_start")
        elif time_granularity == "季度":
            start_quarter = st.selectbox("开始季度", df['季度'].unique(), key="hrvp_start_q")
        else:
            start_year = st.selectbox("开始年份", df['年份'].unique(), key="hrvp_start_y")

    with col_filter3:
        if time_granularity == "月度":
            end_month = st.date_input("结束月份", df['月份'].max(), key="hrvp_end")
        elif time_granularity == "季度":
            end_quarter = st.selectbox("结束季度", df['季度'].unique(), index=len(df['季度'].unique())-1, key="hrvp_end_q")
        else:
            end_year = st.selectbox("结束年份", df['年份'].unique(), index=len(df['年份'].unique())-1, key="hrvp_end_y")

    # 数据筛选
    df_filtered = df.copy()

    if time_granularity == "月度":
        df_filtered = df_filtered[
            (df_filtered['月份'] >= pd.to_datetime(start_month)) &
            (df_filtered['月份'] <= pd.to_datetime(end_month))
        ]
    elif time_granularity == "季度":
        quarters = df['季度'].unique()
        start_idx = list(quarters).index(start_quarter)
        end_idx = list(quarters).index(end_quarter)
        selected_quarters = quarters[start_idx:end_idx+1]
        df_filtered = df_filtered[df_filtered['季度'].isin(selected_quarters)]
    else:
        df_filtered = df_filtered[
            (df_filtered['年份'] >= start_year) &
            (df_filtered['年份'] <= end_year)
        ]

    st.markdown("---")

    # ==========================================
    # 核心KPI卡片 (4-5个)
    # ==========================================

    st.subheader("🎯 核心战略指标")

    kpi_cols = st.columns(5)

    # KPI 1: 关键战略岗位按时达成率
    with kpi_cols[0]:
        metric_key = '关键战略岗位按时达成率_%'
        metric_info = HRVP_CORE_METRICS[metric_key]

        current_value = df_filtered[metric_key].mean()
        target = metric_info['target']
        delta = current_value - target

        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                {metric_info['name']}
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {primary_color}; margin-bottom: 0.25rem;">
                {current_value:.1f}%
            </div>
            <div style="font-size: 0.85rem; color: {'#28a745' if delta >= 0 else '#dc3545'};">
                {'▲' if delta >= 0 else '▼'} {abs(delta):.1f}% vs 目标
            </div>
        </div>
        """, unsafe_allow_html=True)

    # KPI 2: 空缺岗位收入损失
    with kpi_cols[1]:
        metric_key = '空缺岗位收入损失_万元'
        metric_info = HRVP_CORE_METRICS[metric_key]

        current_value = df_filtered[metric_key].sum()
        target = metric_info['target']
        delta = target - current_value  # 成本越低越好

        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                {metric_info['name']}
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {primary_color}; margin-bottom: 0.25rem;">
                {current_value:.0f}万
            </div>
            <div style="font-size: 0.85rem; color: {'#28a745' if delta >= 0 else '#dc3545'};">
                {'▼' if delta >= 0 else '▲'} {abs(delta):.0f}万 vs 目标
            </div>
        </div>
        """, unsafe_allow_html=True)

    # KPI 3: 高绩效员工占比
    with kpi_cols[2]:
        metric_key = '高绩效员工占比_%'
        metric_info = HRVP_CORE_METRICS[metric_key]

        current_value = df_filtered[metric_key].mean()
        target = metric_info['target']
        delta = current_value - target

        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                {metric_info['name']}
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {primary_color}; margin-bottom: 0.25rem;">
                {current_value:.1f}%
            </div>
            <div style="font-size: 0.85rem; color: {'#28a745' if delta >= 0 else '#dc3545'};">
                {'▲' if delta >= 0 else '▼'} {abs(delta):.1f}% vs 目标
            </div>
        </div>
        """, unsafe_allow_html=True)

    # KPI 4: 人才市场占有率
    with kpi_cols[3]:
        metric_key = '人才市场占有率_%'
        metric_info = HRVP_CORE_METRICS[metric_key]

        current_value = df_filtered[metric_key].mean()
        target = metric_info['target']
        delta = current_value - target

        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                {metric_info['name']}
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {primary_color}; margin-bottom: 0.25rem;">
                {current_value:.1f}%
            </div>
            <div style="font-size: 0.85rem; color: {'#28a745' if delta >= 0 else '#dc3545'};">
                {'▲' if delta >= 0 else '▼'} {abs(delta):.1f}% vs 目标
            </div>
        </div>
        """, unsafe_allow_html=True)

    # KPI 5: 单次招聘成本
    with kpi_cols[4]:
        metric_key = '单次招聘成本_元'
        metric_info = HRVP_CORE_METRICS[metric_key]

        current_value = df_filtered[metric_key].mean()
        target = metric_info['target']
        delta = target - current_value  # 成本越低越好

        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                {metric_info['name']}
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {primary_color}; margin-bottom: 0.25rem;">
                {current_value:,.0f}元
            </div>
            <div style="font-size: 0.85rem; color: {'#28a745' if delta >= 0 else '#dc3545'};">
                {'▼' if delta >= 0 else '▲'} {abs(delta):,.0f}元 vs 目标
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # 详细指标矩阵 (置顶!)
    # ==========================================

    st.subheader("📋 战略指标详细矩阵")

    st.info("💡 **老板视角**: 以下5个指标直接关联公司战略、财务和竞争力")

    # 创建详细表格
    metrics_table = []

    for metric_key, metric_info in HRVP_CORE_METRICS.items():
        current_val = df_filtered[metric_key].mean() if metric_key != '空缺岗位收入损失_万元' else df_filtered[metric_key].sum()

        # 判断状态
        target = metric_info['target']

        if metric_key in ['空缺岗位收入损失_万元', '单次招聘成本_元']:
            # 越低越好
            if current_val < target:
                status = "✅ 优秀"
            elif current_val < target * 1.2:
                status = "⚠️ 良好"
            else:
                status = "🔴 需改进"
        else:
            # 越高越好
            if current_val >= target:
                status = "✅ 优秀"
            elif current_val >= target * 0.9:
                status = "⚠️ 良好"
            else:
                status = "🔴 需改进"

        metrics_table.append({
            '指标名称': metric_info['name'],
            '英文名': metric_info['name_en'],
            '当前值': f"{current_val:.1f}{metric_info['unit']}" if metric_info['unit'] == '%' else f"{current_val:,.0f}{metric_info['unit']}",
            '目标值': f"{target:.1f}{metric_info['unit']}" if metric_info['unit'] == '%' else f"{target:,.0f}{metric_info['unit']}",
            '状态': status,
            '类别': metric_info['category'],
            '老板关注点': metric_info['boss_comment']
        })

    metrics_df = pd.DataFrame(metrics_table)

    st.dataframe(
        metrics_df,
        use_container_width=True,
        height=250,
        hide_index=True
    )

    st.markdown("---")

    # ==========================================
    # 图表区 (图表作为辅助说明在下方)
    # ==========================================

    st.subheader("📈 战略趋势分析")

    # 图表 1: 关键岗位达成率趋势 (月度/季度)
    st.markdown("#### 1️⃣ 关键战略岗位达成率趋势")

    if time_granularity == "月度":
        trend_df = df_filtered.groupby('月份').agg({
            '关键战略岗位按时达成率_%': 'mean'
        }).reset_index()
        x_col = '月份'
    elif time_granularity == "季度":
        trend_df = df_filtered.groupby('季度').agg({
            '关键战略岗位按时达成率_%': 'mean'
        }).reset_index()
        x_col = '季度'
    else:
        trend_df = df_filtered.groupby('年份').agg({
            '关键战略岗位按时达成率_%': 'mean'
        }).reset_index()
        x_col = '年份'

    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=trend_df[x_col],
        y=trend_df['关键战略岗位按时达成率_%'],
        mode='lines+markers',
        name='达成率',
        line=dict(color=colors[0], width=3),
        marker=dict(size=10, color=colors[0]),
        fill='tozeroy',
        fillcolor=f'rgba({int(colors[0][1:3], 16)}, {int(colors[0][3:5], 16)}, {int(colors[0][5:7], 16)}, 0.2)'
    ))

    # 添加目标线
    fig1.add_hline(
        y=85,
        line_dash="dash",
        line_color="red",
        annotation_text="目标: 85%",
        annotation_position="right"
    )

    fig1.update_layout(
        title="关键岗位按时达成率趋势",
        xaxis_title=time_granularity,
        yaxis_title="达成率 (%)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    **📊 洞察**:
    - 关键战略岗位直接影响业务推进速度
    - 低于85%时需要HRVP介入资源调配
    - 建议：对P0级岗位建立快速通道和专项预算
    """)

    st.markdown("---")

    # 图表 2: 成本 vs 质量矩阵 (散点图)
    st.markdown("#### 2️⃣ 成本与质量平衡矩阵")

    dept_summary = df_filtered.groupby('部门').agg({
        '单次招聘成本_元': 'mean',
        '高绩效员工占比_%': 'mean',
        '总招聘人数': 'sum'
    }).reset_index()

    fig2 = px.scatter(
        dept_summary,
        x='单次招聘成本_元',
        y='高绩效员工占比_%',
        size='总招聘人数',
        color='部门',
        text='部门',
        color_discrete_sequence=colors
    )

    # 添加参考线
    fig2.add_vline(x=10000, line_dash="dash", line_color="gray", annotation_text="成本目标")
    fig2.add_hline(y=70, line_dash="dash", line_color="gray", annotation_text="质量目标")

    fig2.update_traces(textposition='top center')

    fig2.update_layout(
        title="各部门成本-质量矩阵 (气泡大小=招聘人数)",
        xaxis_title="单次招聘成本 (元)",
        yaxis_title="高绩效员工占比 (%)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    **📊 洞察**:
    - **右上象限 (高成本高质量)**: 可接受，ROI合理
    - **左上象限 (低成本高质量)**: 最优区域，值得推广经验
    - **右下象限 (高成本低质量)**: 严重问题，需立即优化
    - **左下象限 (低成本低质量)**: 不要为了省钱牺牲质量
    """)

    st.markdown("---")

    # 图表 3: 收入损失趋势 (面积图)
    st.markdown("#### 3️⃣ 空缺岗位收入损失趋势")

    if time_granularity == "月度":
        loss_df = df_filtered.groupby('月份').agg({
            '空缺岗位收入损失_万元': 'sum'
        }).reset_index()
        x_col = '月份'
    elif time_granularity == "季度":
        loss_df = df_filtered.groupby('季度').agg({
            '空缺岗位收入损失_万元': 'sum'
        }).reset_index()
        x_col = '季度'
    else:
        loss_df = df_filtered.groupby('年份').agg({
            '空缺岗位收入损失_万元': 'sum'
        }).reset_index()
        x_col = '年份'

    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=loss_df[x_col],
        y=loss_df['空缺岗位收入损失_万元'],
        mode='lines',
        name='收入损失',
        line=dict(color='#dc3545', width=0),
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.3)'
    ))

    # 添加警戒线
    fig3.add_hline(
        y=200,
        line_dash="dash",
        line_color="orange",
        annotation_text="警戒线: 200万",
        annotation_position="right"
    )

    fig3.add_hline(
        y=500,
        line_dash="dash",
        line_color="red",
        annotation_text="危险线: 500万",
        annotation_position="right"
    )

    fig3.update_layout(
        title="空缺岗位收入损失累计 (财务视角)",
        xaxis_title=time_granularity,
        yaxis_title="收入损失 (万元)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    **📊 洞察**:
    - 将"招人慢"转化为财务语言，推动业务部门配合
    - 超过500万需向董事会解释
    - 建议：建立关键岗位快速响应机制
    """)

    st.markdown("---")

    # 图表 4: 高绩效员工渠道来源分析
    st.markdown("#### 4️⃣ 高绩效员工渠道来源分析 (决定预算分配)")

    channel_quality = df_filtered.groupby('渠道').agg({
        '高绩效员工_猎头来源_%': 'mean',
        '高绩效员工_内推来源_%': 'mean',
        '高绩效员工_自招来源_%': 'mean',
        '总招聘人数': 'sum'
    }).reset_index()

    fig4 = go.Figure()

    fig4.add_trace(go.Bar(
        x=channel_quality['渠道'],
        y=channel_quality['高绩效员工_猎头来源_%'],
        name='猎头来源',
        marker_color=colors[0]
    ))

    fig4.add_trace(go.Bar(
        x=channel_quality['渠道'],
        y=channel_quality['高绩效员工_内推来源_%'],
        name='内推来源',
        marker_color=colors[1]
    ))

    fig4.add_trace(go.Bar(
        x=channel_quality['渠道'],
        y=channel_quality['高绩效员工_自招来源_%'],
        name='自招来源',
        marker_color=colors[2]
    ))

    fig4.update_layout(
        barmode='stack',
        title="各渠道产出的高绩效员工占比",
        xaxis_title="渠道",
        yaxis_title="高绩效员工占比 (%)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("""
    **📊 洞察**:
    - 如果猎头招的人绩效更高，就加大猎头预算
    - 不要为了省钱用便宜渠道，人才质量ROI更重要
    - 建议：每季度评估渠道质量，动态调整预算分配
    """)

    st.markdown("---")

    # 底部总结
    st.success("""
    ✅ **HRVP 战略决策支持**:
    - 只看4-5个核心战略指标，决策效率提升80%
    - 用财务语言(收入损失)说话，业务部门更配合
    - 成本与质量平衡，确保人才ROI最大化
    - 人才市场竞争力可视化，支撑雇主品牌战略
    """)


# ==========================================
# 测试入口
# ==========================================

if __name__ == '__main__':
    # 用于测试
    from data_generator_complete import generate_complete_recruitment_data

    st.set_page_config(page_title="HRVP 战略驾驶舱", layout="wide")

    # 生成测试数据
    df = generate_complete_recruitment_data(months=12, recruiters=5, departments=5)

    # 渲染看板
    render_hrvp_dashboard(df)
