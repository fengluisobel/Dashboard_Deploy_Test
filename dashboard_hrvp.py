"""
HRVP 战略驾驶舱 v3.0 Pro
老板要求："别告诉我招了多少个前台，我只想知道那个能带队打仗的VP到了没有"

核心定位：
- 只看金钱、战略、风险
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

# 导入翻转卡片系统
from flip_card_system import inject_flip_card_css, render_metric_flip_card


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

    # 注入翻转卡片 CSS
    inject_flip_card_css(primary_color)

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
    # 时间筛选器 (HRVP只能选时间，不能选人员) + 快捷筛选按钮
    # ==========================================

    st.subheader("📅 时间范围筛选")

    # 快捷筛选按钮
    st.markdown("**⚡ 快捷筛选:**")
    quick_filter_cols = st.columns([1, 1, 1, 3])

    with quick_filter_cols[0]:
        if st.button("近3个月", key="hrvp_quick_3m", use_container_width=True):
            st.session_state.hrvp_quick_filter = "3m"

    with quick_filter_cols[1]:
        if st.button("近半年", key="hrvp_quick_6m", use_container_width=True):
            st.session_state.hrvp_quick_filter = "6m"

    with quick_filter_cols[2]:
        if st.button("全部时间", key="hrvp_quick_all", use_container_width=True):
            st.session_state.hrvp_quick_filter = "all"

    st.markdown("")

    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        time_granularity = st.selectbox(
            "时间粒度",
            ["月度", "季度", "年度"],
            key="hrvp_time_granularity"
        )

    # 处理快捷筛选
    if 'hrvp_quick_filter' in st.session_state and st.session_state.hrvp_quick_filter != "all":
        # 根据快捷筛选计算时间范围
        end_date = df['月份'].max()

        if st.session_state.hrvp_quick_filter == "3m":
            start_date = end_date - pd.DateOffset(months=3)
            st.info(f"🔍 已应用快捷筛选: 近3个月 ({start_date.strftime('%Y-%m')} 至 {end_date.strftime('%Y-%m')})")
        elif st.session_state.hrvp_quick_filter == "6m":
            start_date = end_date - pd.DateOffset(months=6)
            st.info(f"🔍 已应用快捷筛选: 近半年 ({start_date.strftime('%Y-%m')} 至 {end_date.strftime('%Y-%m')})")

        df_filtered = df[df['月份'] >= start_date].copy()

    else:
        # 常规筛选
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
    # 核心KPI卡片 (4-5个) - 翻转卡片展示
    # ==========================================

    st.subheader("🎯 核心战略指标")
    st.info("💡 **悬停卡片查看公式和数据明细** - Hover over cards to see formulas and benchmarks")

    kpi_cols = st.columns(5)

    # KPI 1: 关键战略岗位按时达成率
    with kpi_cols[0]:
        metric_key = '关键战略岗位按时达成率_%'
        metric_info = HRVP_CORE_METRICS[metric_key]
        current_value = df_filtered[metric_key].mean()
        target = metric_info['target']

        # 计算原始数据 (模拟)
        total_p0_positions = len(df_filtered)
        hired_on_time = int(total_p0_positions * current_value / 100)

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=target,
            role='HRVP',
            raw_data_dict={
                '按时入职P0级人员': hired_on_time,
                'P0级招聘计划总数': total_p0_positions
            }
        )

    # KPI 2: 空缺岗位收入损失
    with kpi_cols[1]:
        metric_key = '空缺岗位收入损失_万元'
        metric_info = HRVP_CORE_METRICS[metric_key]
        current_value = df_filtered[metric_key].sum()
        target = metric_info['target']

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=target,
            role='HRVP',
            raw_data_dict={
                '累计收入损失': f'{current_value:.0f}万元',
                '目标控制线': f'{target:.0f}万元'
            }
        )

    # KPI 3: 高绩效员工占比
    with kpi_cols[2]:
        metric_key = '高绩效员工占比_%'
        metric_info = HRVP_CORE_METRICS[metric_key]
        current_value = df_filtered[metric_key].mean()
        target = metric_info['target']

        # 计算原始数据
        total_hires = df_filtered['总招聘人数'].sum()
        high_performers = int(total_hires * current_value / 100)

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=target,
            role='HRVP',
            raw_data_dict={
                '高绩效员工数(S/A级)': high_performers,
                '入职总人数': total_hires
            }
        )

    # KPI 4: 人才市场占有率
    with kpi_cols[3]:
        metric_key = '人才市场占有率_%'
        metric_info = HRVP_CORE_METRICS[metric_key]
        current_value = df_filtered[metric_key].mean()
        target = metric_info['target']

        # 计算原始数据
        total_hires = df_filtered['总招聘人数'].sum()
        from_competitors = int(total_hires * current_value / 100)

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=target,
            role='HRVP',
            raw_data_dict={
                '来自核心竞对人数': from_competitors,
                '总入职人数': total_hires
            }
        )

    # KPI 5: 单次招聘成本
    with kpi_cols[4]:
        metric_key = '单次招聘成本_元'
        metric_info = HRVP_CORE_METRICS[metric_key]
        current_value = df_filtered[metric_key].mean()
        target = metric_info['target']

        # 计算原始数据
        total_hires = df_filtered['总招聘人数'].sum()
        total_cost = current_value * total_hires

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=target,
            role='HRVP',
            raw_data_dict={
                '总招聘成本': f'{total_cost:,.0f}元',
                '总入职人数': total_hires
            }
        )

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

    # ==========================================
    # 图表 5: HR负载与效能分析 (碳硅协同视角)
    # ==========================================

    st.markdown("#### 5️⃣ HR 招聘负载与效能趋势 (碳硅协同视角)")
    st.info("💡 **核心洞察**: 展示HR工作负载、招聘效率、资源缺口的关联关系，为资源配置决策提供数据支持")

    # 模拟生成HR负载数据 (实际应从数据源获取)
    if time_granularity == "月度":
        workload_df = df_filtered.groupby('月份').agg({
            '总招聘人数': 'sum',
            '简历筛选总数': 'sum'
        }).reset_index()
        x_col = '月份'
    elif time_granularity == "季度":
        workload_df = df_filtered.groupby('季度').agg({
            '总招聘人数': 'sum',
            '简历筛选总数': 'sum'
        }).reset_index()
        x_col = '季度'
    else:
        workload_df = df_filtered.groupby('年份').agg({
            '总招聘人数': 'sum',
            '简历筛选总数': 'sum'
        }).reset_index()
        x_col = '年份'

    # 计算HR人均负载 (假设HR团队规模为5人)
    hr_team_size = 5
    workload_df['HR人均招聘负载(人/HR)'] = workload_df['总招聘人数'] / hr_team_size
    workload_df['HR人均简历筛选负载(份/HR)'] = workload_df['简历筛选总数'] / hr_team_size

    # 计算招聘效率 (入职人数/简历筛选数)
    workload_df['招聘转化率(%)'] = (workload_df['总招聘人数'] / workload_df['简历筛选总数'] * 100).fillna(0)

    # 创建双轴图表 (Bar + Line)
    fig5 = make_subplots(specs=[[{"secondary_y": True}]])

    # 添加柱状图 - HR人均招聘负载
    fig5.add_trace(
        go.Bar(
            x=workload_df[x_col],
            y=workload_df['HR人均招聘负载(人/HR)'],
            name='HR人均招聘负载(人/HR)',
            marker=dict(
                color='#4A5FE8',
                opacity=0.85
            ),
            width=0.6
        ),
        secondary_y=False
    )

    # 添加折线图 - 招聘转化率
    fig5.add_trace(
        go.Scatter(
            x=workload_df[x_col],
            y=workload_df['招聘转化率(%)'],
            name='招聘转化率(%)',
            line=dict(color='#0D7C3A', width=4),
            marker=dict(size=10, color='#0D7C3A', symbol='circle'),
            mode='lines+markers'
        ),
        secondary_y=True
    )

    # 添加基准线 - 健康负载阈值
    avg_load = workload_df['HR人均招聘负载(人/HR)'].mean()
    fig5.add_hline(
        y=avg_load * 1.2,
        line_dash="dash",
        line_color='#A66800',
        annotation_text=f"负载警戒线: {avg_load*1.2:.1f}人/HR",
        annotation_position="right",
        secondary_y=False
    )

    # 更新布局
    fig5.update_layout(
        title=f"HR 招聘负载与转化效率趋势 ({time_granularity})",
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        xaxis_title=time_granularity,
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )

    # 更新Y轴
    fig5.update_yaxes(
        title_text="HR人均招聘负载 (人/HR)",
        secondary_y=False,
        color="#4A5FE8",
        tickfont=dict(size=11)
    )

    fig5.update_yaxes(
        title_text="招聘转化率 (%)",
        secondary_y=True,
        color="#0D7C3A",
        tickfont=dict(size=11),
        range=[0, max(workload_df['招聘转化率(%)']) * 1.2]
    )

    st.plotly_chart(fig5, use_container_width=True)

    # 负载分析洞察
    current_avg_load = workload_df['HR人均招聘负载(人/HR)'].iloc[-1] if len(workload_df) > 0 else 0
    current_conversion = workload_df['招聘转化率(%)'].iloc[-1] if len(workload_df) > 0 else 0
    load_trend = "上升" if len(workload_df) > 1 and workload_df['HR人均招聘负载(人/HR)'].iloc[-1] > workload_df['HR人均招聘负载(人/HR)'].iloc[0] else "下降"

    # 资源缺口判断
    if current_avg_load > avg_load * 1.2:
        resource_status = "🔴 负载过高"
        recommendation = "建议增加HR人力或优化流程，当前负载已超过健康阈值20%"
    elif current_avg_load > avg_load * 1.1:
        resource_status = "⚠️ 负载偏高"
        recommendation = "建议关注HR负载趋势，考虑流程优化或临时增援"
    else:
        resource_status = "✅ 负载健康"
        recommendation = "当前HR负载在健康范围内，继续保持"

    col_insight1, col_insight2 = st.columns(2)

    with col_insight1:
        st.markdown(f"""
        **📊 负载分析**:
        - **当前人均负载**: {current_avg_load:.1f} 人/HR
        - **负载趋势**: {load_trend}
        - **资源状态**: {resource_status}
        """)

    with col_insight2:
        st.markdown(f"""
        **📈 效率分析**:
        - **当前转化率**: {current_conversion:.2f}%
        - **平均转化率**: {workload_df['招聘转化率(%)'].mean():.2f}%
        - **优化建议**: {recommendation}
        """)

    st.markdown("---")

    # 图表 6: 资源缺口矩阵
    st.markdown("#### 6️⃣ HR 资源配置与缺口分析")

    # 按部门分析负载和缺口
    dept_workload = df_filtered.groupby('部门').agg({
        '总招聘人数': 'sum',
        '简历筛选总数': 'sum',
        '关键战略岗位按时达成率_%': 'mean'
    }).reset_index()

    # 假设每个部门有1个HR
    dept_workload['HR人均负载'] = dept_workload['总招聘人数']
    dept_workload['转化率(%)'] = (dept_workload['总招聘人数'] / dept_workload['简历筛选总数'] * 100).fillna(0)

    # 判断资源缺口
    avg_dept_load = dept_workload['HR人均负载'].mean()
    dept_workload['资源缺口状态'] = dept_workload['HR人均负载'].apply(
        lambda x: '🔴 需增员' if x > avg_dept_load * 1.3 else ('⚠️ 关注' if x > avg_dept_load * 1.1 else '✅ 健康')
    )

    # 创建散点图 - 负载 vs 达成率
    fig6 = px.scatter(
        dept_workload,
        x='HR人均负载',
        y='关键战略岗位按时达成率_%',
        size='简历筛选总数',
        color='资源缺口状态',
        text='部门',
        color_discrete_map={
            '✅ 健康': '#0D7C3A',
            '⚠️ 关注': '#C17A00',
            '🔴 需增员': '#C01C28'
        }
    )

    fig6.update_traces(textposition='top center', marker=dict(line=dict(width=2, color='white')))

    # 添加参考线
    fig6.add_vline(
        x=avg_dept_load,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"平均负载: {avg_dept_load:.0f}人"
    )

    fig6.add_hline(
        y=85,
        line_dash="dash",
        line_color="gray",
        annotation_text="目标达成率: 85%"
    )

    fig6.update_layout(
        title="部门HR负载 vs 岗位达成率 (气泡大小=简历筛选量)",
        xaxis_title="HR人均招聘负载 (人)",
        yaxis_title="关键战略岗位达成率 (%)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.markdown("""
    **📊 资源配置洞察**:
    - **右上象限**: 高负载+高达成 → 团队效能优秀，但需关注可持续性
    - **左上象限**: 低负载+高达成 → 最优状态，值得推广经验
    - **右下象限**: 高负载+低达成 → 严重问题，需立即增援或流程优化
    - **左下象限**: 低负载+低达成 → 效能问题，需分析根因(非负载导致)
    """)

    st.markdown("---")

    # ==========================================
    # 图表 7: 硅碳比分析 (AI + HR协同效能)
    # ==========================================

    st.markdown("#### 7️⃣ 硅碳比分析 - 团队负载与资源配置决策")
    st.info("💡 **核心洞察**: 分析AI(硅基)与HR(碳基)资源的协同效能，为资源扩充决策提供量化依据")

    # 计算硅碳比数据
    silicon_carbon_df = df_filtered.groupby('部门').agg({
        'HR团队人数': 'mean',
        'AI平均承接率_%': 'mean',
        'HR人均月招聘负载_人': 'mean',
        'HR负载释放率_%': 'mean',
        '碳硅协同效率提升_%': 'mean',
        '总招聘人数': 'sum',
        '硅碳比': 'mean',
        '硅碳协同健康度_得分': 'mean'
    }).reset_index()

    # 计算AI等效人力
    silicon_carbon_df['AI等效人力'] = silicon_carbon_df['HR团队人数'] * silicon_carbon_df['AI平均承接率_%'] / 100

    # 创建双轴图表 - 硅碳比 + 负载释放率
    fig7 = make_subplots(specs=[[{"secondary_y": True}]])

    # 柱状图 - 硅碳比
    fig7.add_trace(
        go.Bar(
            x=silicon_carbon_df['部门'],
            y=silicon_carbon_df['硅碳比'],
            name='硅碳比 (AI/HR)',
            marker=dict(
                color='#6366F1',
                opacity=0.85
            ),
            text=[f"{v:.2f}" for v in silicon_carbon_df['硅碳比']],
            textposition='auto',
            width=0.5
        ),
        secondary_y=False
    )

    # 折线图 - HR负载释放率
    fig7.add_trace(
        go.Scatter(
            x=silicon_carbon_df['部门'],
            y=silicon_carbon_df['HR负载释放率_%'],
            name='HR负载释放率(%)',
            line=dict(color='#10B981', width=4),
            marker=dict(size=12, color='#10B981', symbol='diamond'),
            mode='lines+markers'
        ),
        secondary_y=True
    )

    # 添加基准线
    avg_silicon_carbon = silicon_carbon_df['硅碳比'].mean()
    fig7.add_hline(
        y=avg_silicon_carbon,
        line_dash="dash",
        line_color='#94A3B8',
        annotation_text=f"平均硅碳比: {avg_silicon_carbon:.2f}",
        annotation_position="right",
        secondary_y=False
    )

    fig7.update_layout(
        title="各部门硅碳比 vs HR负载释放率",
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        xaxis_title="部门",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )

    fig7.update_yaxes(
        title_text="硅碳比 (AI等效人力/HR人数)",
        secondary_y=False,
        color="#6366F1",
        range=[0, max(silicon_carbon_df['硅碳比']) * 1.3]
    )

    fig7.update_yaxes(
        title_text="HR负载释放率 (%)",
        secondary_y=True,
        color="#10B981",
        range=[0, 100]
    )

    st.plotly_chart(fig7, use_container_width=True)

    # 硅碳比详细数据表
    st.markdown("**📊 硅碳比详细数据**")

    silicon_carbon_display = silicon_carbon_df[['部门', 'HR团队人数', 'AI等效人力', '硅碳比',
                                                 'HR负载释放率_%', '碳硅协同效率提升_%',
                                                 '硅碳协同健康度_得分']].copy()

    silicon_carbon_display.columns = ['部门', 'HR人数', 'AI等效人力', '硅碳比',
                                       '负载释放率(%)', '效率提升(%)', '协同健康度']

    # 格式化数值
    silicon_carbon_display['AI等效人力'] = silicon_carbon_display['AI等效人力'].apply(lambda x: f"{x:.2f}")
    silicon_carbon_display['硅碳比'] = silicon_carbon_display['硅碳比'].apply(lambda x: f"{x:.2f}")
    silicon_carbon_display['负载释放率(%)'] = silicon_carbon_display['负载释放率(%)'].apply(lambda x: f"{x:.1f}%")
    silicon_carbon_display['效率提升(%)'] = silicon_carbon_display['效率提升(%)'].apply(lambda x: f"{x:.1f}%")
    silicon_carbon_display['协同健康度'] = silicon_carbon_display['协同健康度'].apply(lambda x: f"{x:.1f}")

    st.dataframe(silicon_carbon_display, use_container_width=True, hide_index=True)

    # 资源配置建议
    col_sc1, col_sc2, col_sc3 = st.columns(3)

    with col_sc1:
        avg_hr_load = silicon_carbon_df['HR人均月招聘负载_人'].mean()
        st.metric(
            "平均HR月负载",
            f"{avg_hr_load:.1f}人/HR",
            delta=f"{'偏高' if avg_hr_load > 6 else '健康'}",
            delta_color="inverse" if avg_hr_load > 6 else "normal"
        )

    with col_sc2:
        avg_ai_coverage = silicon_carbon_df['AI平均承接率_%'].mean()
        st.metric(
            "AI平均承接率",
            f"{avg_ai_coverage:.1f}%",
            delta=f"{'优秀' if avg_ai_coverage > 70 else '待提升'}",
            delta_color="normal" if avg_ai_coverage > 70 else "inverse"
        )

    with col_sc3:
        avg_efficiency_boost = silicon_carbon_df['碳硅协同效率提升_%'].mean()
        st.metric(
            "协同效率提升",
            f"{avg_efficiency_boost:.1f}%",
            delta=f"vs 纯人工模式"
        )

    st.markdown("""
    **🔍 硅碳比决策指南**:
    - **硅碳比 > 0.7**: AI承接充分，碳基HR可聚焦高价值工作，资源配置优秀
    - **硅碳比 0.4-0.7**: AI发挥作用，但仍有提升空间，建议优化AI模型或扩充算力
    - **硅碳比 < 0.4**: AI承接不足，碳基HR负载重，建议：
        - **优先选择1**: 优化AI模型能力(低成本)
        - **备选方案**: 增加碳基HR人力(高成本)

    **💡 资源配置决策建议**:
    1. **HR负载 > 6人/月 且 硅碳比 < 0.5** → 优先增加AI算力
    2. **HR负载 > 8人/月 且 硅碳比 > 0.6** → 增加碳基HR人力
    3. **AI承接率 < 60%** → 需要AI模型优化或流程改进
    """)

    st.markdown("---")

    # ==========================================
    # 图表 8: 校招候选人质量分析 (战略人才储备视角)
    # ==========================================

    st.markdown("#### 8️⃣ 校招人才质量分析 - 未来战略人才储备")
    st.info("💡 **战略视角**: 校招是未来3-5年战略人才的核心来源，质量直接影响组织长期竞争力")

    # 校招质量数据汇总
    campus_quality = {
        '平均笔试分': df_filtered['校招_平均笔试分'].mean(),
        '平均面试分': df_filtered['校招_平均面试分'].mean(),
        'S级SSP占比': df_filtered['校招_S级SSP占比_%'].mean(),
        'A级SP占比': df_filtered['校招_A级SP占比_%'].mean(),
        '综合质量得分': df_filtered['校招_综合质量得分'].mean(),
        '总签约率': df_filtered['校招_签约率_%'].mean(),
        'S级签约率': df_filtered['校招_S级签约率_%'].mean()
    }

    # 顶部KPI卡片
    campus_cols = st.columns(4)

    with campus_cols[0]:
        st.metric(
            "校招综合质量",
            f"{campus_quality['综合质量得分']:.1f}分",
            delta=f"{'优秀' if campus_quality['综合质量得分'] > 80 else '待提升'}"
        )

    with campus_cols[1]:
        st.metric(
            "S级人才占比",
            f"{campus_quality['S级SSP占比']:.1f}%",
            delta=f"目标: 15%",
            delta_color="normal" if campus_quality['S级SSP占比'] >= 15 else "inverse"
        )

    with campus_cols[2]:
        st.metric(
            "总体签约率",
            f"{campus_quality['总签约率']:.1f}%",
            delta=f"{'健康' if campus_quality['总签约率'] > 70 else '流失严重'}"
        )

    with campus_cols[3]:
        st.metric(
            "S级签约率",
            f"{campus_quality['S级签约率']:.1f}%",
            delta=f"⚠️ 高端流失",
            delta_color="inverse"
        )

    st.markdown("")

    # 质量九宫格 - 笔试 vs 面试
    st.markdown("**📊 人才质量矩阵 (笔试硬技能 vs 面试软技能)**")

    # 按部门分组计算
    campus_matrix = df_filtered.groupby('部门').agg({
        '校招_平均笔试分': 'mean',
        '校招_平均面试分': 'mean',
        '校招_Offer发放数': 'sum',
        '校招_质量象限': lambda x: x.mode()[0] if len(x.mode()) > 0 else '未知'
    }).reset_index()

    fig8 = px.scatter(
        campus_matrix,
        x='校招_平均笔试分',
        y='校招_平均面试分',
        size='校招_Offer发放数',
        color='校招_质量象限',
        text='部门',
        color_discrete_map={
            '右上-双高人才': '#10B981',
            '右下-技术强沟通弱': '#F59E0B',
            '左上-沟通强技术弱': '#3B82F6',
            '左下-双低': '#EF4444'
        },
        title="校招候选人质量分布 (气泡大小 = Offer发放数)"
    )

    # 添加参考线
    fig8.add_hline(
        y=80,
        line_dash="dot",
        line_color="gray",
        annotation_text="高潜线 (软技能)"
    )

    fig8.add_vline(
        x=80,
        line_dash="dot",
        line_color="gray",
        annotation_text="高潜线 (硬技能)"
    )

    # 高亮右上角区域
    fig8.add_shape(
        type="rect",
        x0=80, y0=80, x1=100, y1=100,
        line=dict(color="#10B981", width=2),
        fillcolor="rgba(16, 185, 129, 0.1)"
    )

    fig8.update_traces(textposition='top center', marker=dict(line=dict(width=2, color='white')))

    fig8.update_layout(
        xaxis_title="笔试分数 (硬技能)",
        yaxis_title="面试分数 (软技能)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        xaxis=dict(range=[60, 95]),
        yaxis=dict(range=[60, 95])
    )

    st.plotly_chart(fig8, use_container_width=True)

    # 院校来源分析
    st.markdown("**🎓 院校来源质量分析**")

    campus_school_cols = st.columns(3)

    with campus_school_cols[0]:
        # 顶级院校占比
        top_schools = df_filtered['校招_C9联盟_%'].mean() + df_filtered['校招_海外QS50_%'].mean()
        st.metric("顶级院校占比", f"{top_schools:.1f}%", delta="C9+QS50")

    with campus_school_cols[1]:
        # 985/211占比
        mid_schools = df_filtered['校招_985非C9_%'].mean() + df_filtered['校招_211核心_%'].mean()
        st.metric("985/211占比", f"{mid_schools:.1f}%", delta="中坚力量")

    with campus_school_cols[2]:
        # 海外院校占比
        overseas = df_filtered['校招_海外QS50_%'].mean() + df_filtered['校招_海外QS100_%'].mean()
        st.metric("海外院校占比", f"{overseas:.1f}%", delta="国际化")

    # 拒签原因分析
    st.markdown("**⚠️ S级人才流失原因 (为什么优秀的人不来)**")

    reject_data = pd.DataFrame({
        '拒签原因': ['薪资不达预期', '竞对(BAT)截胡', '工作地点不符', '其他原因'],
        '占比': [
            df_filtered['校招_拒签原因_薪资_%'].mean(),
            df_filtered['校招_拒签原因_竞对_%'].mean(),
            df_filtered['校招_拒签原因_地点_%'].mean(),
            df_filtered['校招_拒签原因_其他_%'].mean()
        ]
    })

    fig9 = px.bar(
        reject_data,
        x='拒签原因',
        y='占比',
        text='占比',
        color='拒签原因',
        color_discrete_sequence=['#EF4444', '#F59E0B', '#3B82F6', '#94A3B8']
    )

    fig9.update_traces(texttemplate='%{text:.1f}%', textposition='outside')

    fig9.update_layout(
        title="S级人才拒签原因分布",
        xaxis_title="",
        yaxis_title="占比 (%)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig9, use_container_width=True)

    st.markdown("""
    **📊 校招战略洞察**:
    - **S级人才签约率低于50%**: 说明我们在顶尖人才争夺战中处于劣势
    - **主要流失原因-薪资**: 建议建立校招SSP(Special Salary Package)机制
    - **主要流失原因-竞对**: 需要加强雇主品牌和早期接触(大二/大三实习)
    - **右上象限(双高人才)集中度**: 决定未来3-5年组织战斗力

    **💡 战略决策建议**:
    1. **S级人才专项**: 设立SSP特殊薪资包，签约率目标提升至65%+
    2. **提前布局**: 大二暑期实习计划，锁定潜力人才
    3. **差异化竞争**: 避开BAT主战场(算法/架构)，聚焦新兴赛道人才
    """)

    st.markdown("---")

    # 底部总结
    st.success("""
    ✅ **HRVP 战略决策支持**:
    - 只看4-5个核心战略指标，决策效率提升80%
    - 用财务语言(收入损失)说话，业务部门更配合
    - 成本与质量平衡，确保人才ROI最大化
    - 人才市场竞争力可视化，支撑雇主品牌战略
    - 硅碳比分析，优化资源配置(AI vs HR)
    - 校招质量前瞻，布局未来3-5年战略人才储备
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
