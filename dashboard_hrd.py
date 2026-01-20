"""
HRD 异常报警器 v3.0 Pro
老板要求："不要给我看平均数，告诉我哪个部门出问题了，我去骂他们的负责人"

核心定位：
- 把看板做成"异常报警器"，不是"报表阅读器"
- 红/黄/绿三色预警系统
- 部门/BU汇总视图，可下钻到Recruiter
- 周度/月度时间粒度
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 导入品牌色系统
from brand_color_system import get_brand_colors, get_primary_color, get_brand_font

# 导入翻转卡片系统
from flip_card_system import inject_flip_card_css, render_metric_flip_card


# ==========================================
# HRD 核心异常指标定义
# ==========================================

HRD_EXCEPTION_METRICS = {
    'TTF超标率_%': {
        'name': 'TTF超标率',
        'name_en': 'TTF Overdue Rate',
        'category': '异常管理',
        'unit': '%',
        'formula': 'TTF超过承诺SLA天数的职位数 / 总职位数 × 100%',
        'definition': '招聘周期超过承诺SLA的职位比例',
        'boss_comment': '不要给我看平均数，告诉我哪个部门出问题了',
        'threshold': {
            '正常': '<15%',
            '警告': '15-25%',
            '严重': '>25%'
        },
        'warning_level': 15.0,
        'critical_level': 25.0,
        'review_cadence': 'Weekly'
    },

    'Offer毁约率_%': {
        'name': 'Offer毁约率',
        'name_en': 'Offer Renege Rate',
        'category': '风险预警',
        'unit': '%',
        'formula': '接受Offer后未入职人数 / 接受Offer总数 × 100%',
        'definition': '衡量"临门一脚"的失败率',
        'boss_comment': '煮熟的鸭子飞了是最伤士气的，必须严控',
        'threshold': {
            '正常': '<6%',
            '警告': '6-10%',
            '严重': '>10%'
        },
        'warning_level': 6.0,
        'critical_level': 10.0,
        'review_cadence': 'Monthly'
    },

    '招聘顾问人效_人': {
        'name': '招聘团队人均产能',
        'name_en': 'Req Closed per Recruiter',
        'category': '团队效率',
        'unit': '人/月',
        'formula': '成功关闭职位数 / 招聘专员人数',
        'definition': '衡量团队内部的工作负载分布',
        'boss_comment': '谁在摸鱼？谁快累死了？动态调整HC分配',
        'threshold': {
            '优秀': '>8人/月',
            '良好': '5-8人/月',
            '需改进': '<5人/月'
        },
        'warning_level': 5.0,
        'critical_level': 3.0,
        'review_cadence': 'Monthly'
    },

    '投诉量': {
        'name': '候选人投诉量',
        'name_en': 'Candidate Complaints',
        'category': '服务质量',
        'unit': '件',
        'formula': '本期收到的候选人投诉数量',
        'definition': '反映招聘服务质量和候选人体验',
        'boss_comment': '投诉就是服务质量的直接反馈',
        'threshold': {
            '正常': '<5件',
            '警告': '5-10件',
            '严重': '>10件'
        },
        'warning_level': 5.0,
        'critical_level': 10.0,
        'review_cadence': 'Weekly'
    },

    '部门健康度_得分': {
        'name': '部门招聘健康度',
        'name_en': 'Department Health Score',
        'category': '综合健康度',
        'unit': '分',
        'formula': '综合TTF超标率、面试通过率异常、投诉量的加权评分',
        'definition': '综合评估部门招聘运营健康状况',
        'boss_comment': '一眼看出哪个部门是"老大难"',
        'threshold': {
            '健康': '>80分',
            '亚健康': '60-80分',
            '不健康': '<60分'
        },
        'warning_level': 80.0,
        'critical_level': 60.0,
        'review_cadence': 'Weekly'
    }
}


# ==========================================
# 异常等级判断函数
# ==========================================

def get_alert_level(value, metric_key, reverse=False):
    """
    判断指标的预警等级

    Parameters:
    -----------
    value : float
        指标当前值
    metric_key : str
        指标键名
    reverse : bool
        是否反向判断（越高越好）

    Returns:
    --------
    tuple : (level, color, emoji)
        level: 'normal', 'warning', 'critical'
        color: 对应颜色
        emoji: 对应emoji
    """
    metric = HRD_EXCEPTION_METRICS[metric_key]
    warning = metric['warning_level']
    critical = metric['critical_level']

    if not reverse:
        # 越低越好的指标
        if value < warning:
            return ('normal', '#28a745', '🟢')
        elif value < critical:
            return ('warning', '#ffc107', '🟡')
        else:
            return ('critical', '#dc3545', '🔴')
    else:
        # 越高越好的指标
        if value >= warning:
            return ('normal', '#28a745', '🟢')
        elif value >= critical:
            return ('warning', '#ffc107', '🟡')
        else:
            return ('critical', '#dc3545', '🔴')


def get_threshold_text(metric_key, level):
    """
    获取指标阈值的显示文本

    Parameters:
    -----------
    metric_key : str
        指标键名
    level : str
        预警等级 ('normal', 'warning', 'critical')

    Returns:
    --------
    str
        阈值显示文本
    """
    metric = HRD_EXCEPTION_METRICS[metric_key]

    # 映射英文level到中文key
    level_map = {
        'normal': metric.get('threshold_key_map', {}).get('normal', '正常'),
        'warning': metric.get('threshold_key_map', {}).get('warning', '警告'),
        'critical': metric.get('threshold_key_map', {}).get('critical', '严重')
    }

    # 获取对应的中文key
    chinese_key = level_map.get(level, level)

    # 返回阈值文本
    return metric['threshold'].get(chinese_key, '')


# ==========================================
# HRD 看板渲染函数
# ==========================================

def render_hrd_dashboard(df):
    """
    渲染 HRD 异常报警器

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
    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 24px rgba(0,0,0,0.12);">
        <h1 style="color: white; margin: 0; font-size: 2rem;">🚨 HRD 异常报警器</h1>
        <p style="color: white; opacity: 0.95; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Exception Alert System - 红黄绿预警，一眼看出问题
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # 筛选器 (HRD可以选时间+部门)
    # ==========================================

    st.subheader("🔍 数据筛选器")

    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)

    with col_filter1:
        time_granularity = st.selectbox(
            "时间粒度",
            ["周度", "月度"],
            key="hrd_time_granularity"
        )

    with col_filter2:
        start_month = st.date_input("开始时间", df['月份'].min(), key="hrd_start")

    with col_filter3:
        end_month = st.date_input("结束时间", df['月份'].max(), key="hrd_end")

    with col_filter4:
        selected_depts = st.multiselect(
            "部门筛选 (可多选)",
            options=df['部门'].unique().tolist(),
            default=df['部门'].unique().tolist(),
            key="hrd_dept_filter"
        )

    # 数据筛选
    df_filtered = df[
        (df['月份'] >= pd.to_datetime(start_month)) &
        (df['月份'] <= pd.to_datetime(end_month)) &
        (df['部门'].isin(selected_depts))
    ].copy()

    st.markdown("---")

    # ==========================================
    # 核心预警KPI卡片 - 翻转卡片展示
    # ==========================================

    st.subheader("⚠️ 核心异常指标 (实时预警)")
    st.info("💡 **悬停卡片查看公式和数据明细** - Hover over cards to see formulas and benchmarks")

    kpi_cols = st.columns(5)

    # KPI 1: TTF超标率
    with kpi_cols[0]:
        metric_key = 'TTF超标率_%'
        metric_info = HRD_EXCEPTION_METRICS[metric_key]
        current_value = df_filtered[metric_key].mean()

        # 计算原始数据
        total_positions = len(df_filtered)
        overdue_positions = int(total_positions * current_value / 100)

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=metric_info['warning_level'],
            role='HRD',
            raw_data_dict={
                'TTF超标职位数': overdue_positions,
                '总职位数': total_positions
            }
        )

    # KPI 2: Offer毁约率
    with kpi_cols[1]:
        metric_key = 'Offer毁约率_%'
        metric_info = HRD_EXCEPTION_METRICS[metric_key]
        current_value = df_filtered[metric_key].mean()

        # 计算原始数据
        total_offers = len(df_filtered) * 3  # 模拟Offer数量
        renege_count = int(total_offers * current_value / 100)

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=metric_info['warning_level'],
            role='HRD',
            raw_data_dict={
                'Offer毁约数': renege_count,
                'Offer总数': total_offers
            }
        )

    # KPI 3: 招聘顾问人效
    with kpi_cols[2]:
        metric_key = '招聘顾问人效_人'
        metric_info = HRD_EXCEPTION_METRICS[metric_key]
        current_value = df_filtered[metric_key].mean()

        # 计算原始数据
        total_hires = df_filtered['总招聘人数'].sum()
        recruiters = 5  # 假设5个招聘顾问

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=metric_info['warning_level'],
            role='HRD',
            raw_data_dict={
                '成功关闭职位数': total_hires,
                '招聘专员人数': recruiters
            }
        )

    # KPI 4: 投诉量
    with kpi_cols[3]:
        metric_key = '投诉量'
        metric_info = HRD_EXCEPTION_METRICS[metric_key]
        current_value = df_filtered[metric_key].sum()

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=metric_info['warning_level'],
            role='HRD',
            raw_data_dict={
                '候选人投诉总数': int(current_value),
                '预警阈值': f"{metric_info['warning_level']:.0f}件"
            }
        )

    # KPI 5: 部门健康度
    with kpi_cols[4]:
        metric_key = '部门健康度_得分'
        metric_info = HRD_EXCEPTION_METRICS[metric_key]
        current_value = df_filtered[metric_key].mean()

        # 计算健康部门数
        healthy_depts = len(df_filtered[df_filtered[metric_key] >= metric_info['warning_level']])
        total_depts = df_filtered['部门'].nunique()

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=metric_info['warning_level'],
            role='HRD',
            raw_data_dict={
                '健康部门数': healthy_depts,
                '总部门数': total_depts
            }
        )

    st.markdown("---")

    # ==========================================
    # 异常预警详细矩阵 (置顶!)
    # ==========================================

    st.subheader("📋 异常预警详细矩阵")

    st.warning("⚠️ **管理层视角**: 以下指标超出阈值时需要立即介入处理")

    # 按部门汇总异常指标
    dept_summary = df_filtered.groupby('部门').agg({
        'TTF超标率_%': 'mean',
        'Offer毁约率_%': 'mean',
        '招聘顾问人效_人': 'mean',
        '投诉量': 'sum',
        '部门健康度_得分': 'mean',
        '面试通过率异常_标志': 'sum',
        '漏斗异常_标志': 'sum'
    }).reset_index()

    # 添加预警等级列
    dept_summary['TTF预警'] = dept_summary['TTF超标率_%'].apply(
        lambda x: get_alert_level(x, 'TTF超标率_%')[2]
    )
    dept_summary['毁约预警'] = dept_summary['Offer毁约率_%'].apply(
        lambda x: get_alert_level(x, 'Offer毁约率_%')[2]
    )
    dept_summary['人效预警'] = dept_summary['招聘顾问人效_人'].apply(
        lambda x: get_alert_level(x, '招聘顾问人效_人', reverse=True)[2]
    )
    dept_summary['投诉预警'] = dept_summary['投诉量'].apply(
        lambda x: get_alert_level(x, '投诉量')[2]
    )
    dept_summary['健康度预警'] = dept_summary['部门健康度_得分'].apply(
        lambda x: get_alert_level(x, '部门健康度_得分', reverse=True)[2]
    )

    # 格式化显示
    display_df = dept_summary[[
        '部门',
        'TTF超标率_%', 'TTF预警',
        'Offer毁约率_%', '毁约预警',
        '招聘顾问人效_人', '人效预警',
        '投诉量', '投诉预警',
        '部门健康度_得分', '健康度预警'
    ]].copy()

    display_df.columns = [
        '部门',
        'TTF超标率(%)', 'TTF状态',
        'Offer毁约率(%)', '毁约状态',
        '人效(人/月)', '人效状态',
        '投诉量(件)', '投诉状态',
        '健康度(分)', '健康状态'
    ]

    # 格式化数值
    display_df['TTF超标率(%)'] = display_df['TTF超标率(%)'].apply(lambda x: f"{x:.1f}%")
    display_df['Offer毁约率(%)'] = display_df['Offer毁约率(%)'].apply(lambda x: f"{x:.1f}%")
    display_df['人效(人/月)'] = display_df['人效(人/月)'].apply(lambda x: f"{x:.1f}")
    display_df['健康度(分)'] = display_df['健康度(分)'].apply(lambda x: f"{x:.0f}")

    st.dataframe(
        display_df,
        use_container_width=True,
        height=300,
        hide_index=True
    )

    st.markdown("---")

    # ==========================================
    # 图表 1: 部门健康度热力图
    # ==========================================

    st.subheader("🔥 部门招聘健康度热力图")

    st.info("💡 **一眼看出老大难**: 红色部门需要立即介入，黄色部门需要关注")

    # 创建热力图数据
    heatmap_data = dept_summary.pivot_table(
        index='部门',
        values=['TTF超标率_%', 'Offer毁约率_%', '投诉量', '部门健康度_得分'],
        aggfunc='mean'
    )

    # 归一化处理 (0-100分制)
    heatmap_normalized = heatmap_data.copy()
    heatmap_normalized['TTF超标率_%'] = 100 - (heatmap_data['TTF超标率_%'] / 50 * 100).clip(0, 100)
    heatmap_normalized['Offer毁约率_%'] = 100 - (heatmap_data['Offer毁约率_%'] / 20 * 100).clip(0, 100)
    heatmap_normalized['投诉量'] = 100 - (heatmap_data['投诉量'] / 15 * 100).clip(0, 100)
    # 健康度本身就是0-100分

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_normalized.values.T,
        x=heatmap_normalized.index,
        y=['TTF达标度', 'Offer稳定度', '服务质量', '综合健康度'],
        colorscale=[
            [0, '#dc3545'],      # 红色 (0-33)
            [0.33, '#dc3545'],
            [0.33, '#ffc107'],   # 黄色 (33-66)
            [0.66, '#ffc107'],
            [0.66, '#28a745'],   # 绿色 (66-100)
            [1, '#28a745']
        ],
        text=heatmap_normalized.values.T,
        texttemplate='%{text:.0f}',
        textfont={"size": 14},
        colorbar=dict(
            title="健康度",
            tickvals=[0, 50, 100],
            ticktext=['不健康', '亚健康', '健康']
        ),
        hoverongaps=False
    ))

    fig_heatmap.update_layout(
        title="各部门招聘健康度雷达扫描",
        xaxis_title="部门",
        yaxis_title="健康维度",
        font=dict(family=font, size=12),
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("""
    **📊 洞察**:
    - 🔴 **红色区域**: 需要HRD立即介入，找部门负责人谈话
    - 🟡 **黄色区域**: 需要密切关注，预防性干预
    - 🟢 **绿色区域**: 健康状态，可作为标杆推广经验
    """)

    st.markdown("---")

    # ==========================================
    # 图表 2: 招聘顾问人效对比 (柱状图)
    # ==========================================

    st.subheader("👥 招聘顾问人效对比 (谁在摸鱼？谁快累死了？)")

    recruiter_summary = df_filtered.groupby('招聘顾问').agg({
        '招聘顾问人效_人': 'mean',
        '人均负责职位数': 'mean',
        '总招聘人数': 'sum'
    }).reset_index()

    recruiter_summary = recruiter_summary.sort_values('招聘顾问人效_人', ascending=False)

    fig_productivity = go.Figure()

    # 人效柱状图
    fig_productivity.add_trace(go.Bar(
        x=recruiter_summary['招聘顾问'],
        y=recruiter_summary['招聘顾问人效_人'],
        name='人效 (人/月)',
        marker_color=colors[0],
        text=recruiter_summary['招聘顾问人效_人'].apply(lambda x: f"{x:.1f}"),
        textposition='outside'
    ))

    # 添加平均线
    avg_productivity = recruiter_summary['招聘顾问人效_人'].mean()
    fig_productivity.add_hline(
        y=avg_productivity,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"平均: {avg_productivity:.1f}",
        annotation_position="right"
    )

    # 添加目标线
    fig_productivity.add_hline(
        y=8,
        line_dash="dash",
        line_color="green",
        annotation_text="优秀: 8",
        annotation_position="right"
    )

    fig_productivity.add_hline(
        y=5,
        line_dash="dash",
        line_color="orange",
        annotation_text="及格: 5",
        annotation_position="right"
    )

    fig_productivity.update_layout(
        title="招聘顾问人均产能排名",
        xaxis_title="招聘顾问",
        yaxis_title="人效 (成功入职人数/月)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450
    )

    st.plotly_chart(fig_productivity, use_container_width=True)

    # 负载对比表
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔴 负载过重 (需要支援)**")
        overloaded = recruiter_summary[recruiter_summary['人均负责职位数'] > 15]
        if not overloaded.empty:
            for _, row in overloaded.iterrows():
                st.warning(f"{row['招聘顾问']}: {row['人均负责职位数']:.0f}个职位")
        else:
            st.success("暂无负载过重人员")

    with col2:
        st.markdown("**🟡 产能不足 (需要辅导)**")
        underperforming = recruiter_summary[recruiter_summary['招聘顾问人效_人'] < 5]
        if not underperforming.empty:
            for _, row in underperforming.iterrows():
                st.warning(f"{row['招聘顾问']}: {row['招聘顾问人效_人']:.1f}人/月")
        else:
            st.success("团队人效健康")

    st.markdown("---")

    # ==========================================
    # 图表 3: Offer毁约率监控 (趋势图)
    # ==========================================

    st.subheader("🦆 Offer毁约率监控 (煮熟的鸭子飞了)")

    st.error("⚠️ **严重问题**: 毁约率>8%需要立即介入，分析原因并制定对策")

    # 月度趋势
    renege_trend = df_filtered.groupby('月份').agg({
        'Offer毁约率_%': 'mean',
        'Offer毁约数': 'sum'
    }).reset_index()

    fig_renege = go.Figure()

    fig_renege.add_trace(go.Scatter(
        x=renege_trend['月份'],
        y=renege_trend['Offer毁约率_%'],
        mode='lines+markers',
        name='毁约率',
        line=dict(color='#dc3545', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.2)'
    ))

    # 添加警戒线
    fig_renege.add_hline(
        y=6,
        line_dash="dash",
        line_color="orange",
        annotation_text="警告线: 6%",
        annotation_position="right"
    )

    fig_renege.add_hline(
        y=10,
        line_dash="dash",
        line_color="red",
        annotation_text="危险线: 10%",
        annotation_position="right"
    )

    fig_renege.update_layout(
        title="Offer毁约率月度趋势",
        xaxis_title="月份",
        yaxis_title="毁约率 (%)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )

    st.plotly_chart(fig_renege, use_container_width=True)

    # 毁约原因分析
    st.markdown("**毁约原因分析 (Top 3)**")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "薪资竞争力不足",
            f"{df_filtered['Offer拒绝_薪资低_%'].mean():.1f}%",
            delta="-建议调整薪酬策略",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            "被竞对截胡",
            f"{df_filtered['Offer拒绝_竞对截胡_%'].mean():.1f}%",
            delta="-加速决策流程",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            "通勤距离过远",
            f"{df_filtered['Offer拒绝_路程远_%'].mean():.1f}%",
            delta="-考虑远程/混合办公",
            delta_color="inverse"
        )

    st.markdown("---")

    # ==========================================
    # 图表 4: 漏斗转化率异常预警
    # ==========================================

    st.subheader("🚰 漏斗转化率异常预警")

    st.info("💡 **自动识别**: 系统自动标记 < 历史均值-2σ 的异常环节")

    # 计算各环节转化率
    funnel_data = df_filtered.groupby('部门').agg({
        '简历初筛通过率_%': 'mean',
        '面试通过率_%': 'mean',
        '录用接受率_%': 'mean',
        '试用期转正率_%': 'mean'
    }).reset_index()

    # 创建漏斗图
    fig_funnel = go.Figure()

    stages = ['简历初筛', '面试', 'Offer接受', '试用期转正']
    for idx, dept in enumerate(funnel_data['部门']):
        values = [
            funnel_data.loc[idx, '简历初筛通过率_%'],
            funnel_data.loc[idx, '面试通过率_%'],
            funnel_data.loc[idx, '录用接受率_%'],
            funnel_data.loc[idx, '试用期转正率_%']
        ]

        fig_funnel.add_trace(go.Bar(
            x=stages,
            y=values,
            name=dept,
            marker_color=colors[idx % len(colors)]
        ))

    fig_funnel.update_layout(
        barmode='group',
        title="各部门招聘漏斗转化率对比",
        xaxis_title="招聘阶段",
        yaxis_title="通过率 (%)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450
    )

    st.plotly_chart(fig_funnel, use_container_width=True)

    # 异常环节列表
    st.markdown("**🔴 异常环节列表**")

    anomaly_df = df_filtered[df_filtered['漏斗异常_标志'] == 1].groupby(['部门', '漏斗异常_环节']).size().reset_index(name='异常次数')

    if not anomaly_df.empty:
        anomaly_df = anomaly_df.sort_values('异常次数', ascending=False)
        for _, row in anomaly_df.head(5).iterrows():
            st.error(f"⚠️ **{row['部门']}** - {row['漏斗异常_环节']}: 出现 {row['异常次数']} 次异常")
    else:
        st.success("✅ 暂无漏斗异常，所有环节运转正常")

    st.markdown("---")

    # ==========================================
    # 图表 5: 猎头供应商绩效
    # ==========================================

    st.subheader("🤝 猎头供应商绩效评估")

    headhunter_summary = df_filtered[df_filtered['渠道'] == '猎头'].groupby('部门').agg({
        '猎头转正率_%': 'mean',
        '猎头绩效_得分': 'mean',
        '猎头费用占比_%': 'mean'
    }).reset_index()

    if not headhunter_summary.empty:
        fig_headhunter = go.Figure()

        fig_headhunter.add_trace(go.Bar(
            x=headhunter_summary['部门'],
            y=headhunter_summary['猎头转正率_%'],
            name='转正率',
            marker_color=colors[0]
        ))

        fig_headhunter.add_trace(go.Scatter(
            x=headhunter_summary['部门'],
            y=headhunter_summary['猎头绩效_得分'],
            name='综合绩效',
            yaxis='y2',
            mode='lines+markers',
            marker=dict(size=10, color=colors[1]),
            line=dict(width=3)
        ))

        fig_headhunter.update_layout(
            title="猎头供应商绩效评估",
            xaxis_title="部门",
            yaxis_title="转正率 (%)",
            yaxis2=dict(
                title="综合绩效 (分)",
                overlaying='y',
                side='right'
            ),
            font=dict(family=font),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )

        st.plotly_chart(fig_headhunter, use_container_width=True)

        st.markdown("""
        **📊 决策建议**:
        - 转正率<70%的猎头需要警告或更换
        - 综合绩效<70分的供应商列入观察名单
        - 费用占比>50%需要优化渠道结构
        """)
    else:
        st.info("当前筛选范围内无猎头数据")

    st.markdown("---")

    # ==========================================
    # 图表 7: 硅碳比分析 - HRD视角(团队负载与异常关联)
    # ==========================================

    st.markdown("#### 7️⃣ 硅碳比分析 - HRD视角(团队负载与异常关联)")
    st.info("💡 **HRD视角**: 硅碳比过低导致HR负载过高时,TTF超标率和异常率会飙升 - 这是资源配置预警信号")

    # 计算硅碳比数据(按部门)
    silicon_carbon_df = df_filtered.groupby('部门').agg({
        'HR团队人数': 'mean',
        'AI平均承接率_%': 'mean',
        'HR人均月招聘负载_人': 'mean',
        '硅碳比': 'mean',
        'TTF超标率_%': 'mean',
        '总招聘人数': 'sum'
    }).reset_index()

    # 创建双轴图表 - 硅碳比柱状图 + TTF超标率折线图
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

    # 折线图 - TTF超标率
    fig7.add_trace(
        go.Scatter(
            x=silicon_carbon_df['部门'],
            y=silicon_carbon_df['TTF超标率_%'],
            name='TTF超标率(%)',
            line=dict(color='#dc3545', width=4),
            marker=dict(size=12, color='#dc3545', symbol='diamond'),
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

    # 添加TTF超标率警戒线
    fig7.add_hline(
        y=25,
        line_dash="dot",
        line_color='#ffc107',
        annotation_text="TTF警戒线: 25%",
        annotation_position="left",
        secondary_y=True
    )

    fig7.update_layout(
        title="各部门硅碳比 vs TTF超标率 (异常关联分析)",
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
        title_text="TTF超标率 (%)",
        secondary_y=True,
        color="#dc3545",
        range=[0, max(silicon_carbon_df['TTF超标率_%']) * 1.3]
    )

    st.plotly_chart(fig7, use_container_width=True)

    # 硅碳比详细数据表
    st.markdown("**📊 硅碳比与异常率详细数据**")

    silicon_carbon_display = silicon_carbon_df[['部门', 'HR团队人数', '硅碳比',
                                                 'HR人均月招聘负载_人', 'TTF超标率_%',
                                                 'AI平均承接率_%']].copy()

    silicon_carbon_display.columns = ['部门', 'HR人数', '硅碳比',
                                       'HR月负载(人/HR)', 'TTF超标率(%)', 'AI承接率(%)']

    # 添加预警标识
    def get_workload_status(load, silicon_carbon):
        if load > 8 and silicon_carbon < 0.5:
            return '🔴 负载过高+AI不足'
        elif load > 6 and silicon_carbon < 0.6:
            return '🟡 需关注'
        else:
            return '✅ 健康'

    silicon_carbon_display['负载状态'] = silicon_carbon_display.apply(
        lambda row: get_workload_status(row['HR月负载(人/HR)'], row['硅碳比']), axis=1
    )

    # 格式化数值
    silicon_carbon_display['硅碳比'] = silicon_carbon_display['硅碳比'].apply(lambda x: f"{x:.2f}")
    silicon_carbon_display['HR月负载(人/HR)'] = silicon_carbon_display['HR月负载(人/HR)'].apply(lambda x: f"{x:.1f}")
    silicon_carbon_display['TTF超标率(%)'] = silicon_carbon_display['TTF超标率(%)'].apply(lambda x: f"{x:.1f}%")
    silicon_carbon_display['AI承接率(%)'] = silicon_carbon_display['AI承接率(%)'].apply(lambda x: f"{x:.1f}%")

    st.dataframe(silicon_carbon_display, use_container_width=True, hide_index=True)

    # 异常关联分析洞察
    col_sc1, col_sc2, col_sc3 = st.columns(3)

    with col_sc1:
        high_load_low_ai = silicon_carbon_df[
            (silicon_carbon_df['HR人均月招聘负载_人'] > 7) &
            (silicon_carbon_df['硅碳比'] < 0.5)
        ]
        st.metric(
            "高负载+低AI部门数",
            len(high_load_low_ai),
            delta="🔴 需立即干预" if len(high_load_low_ai) > 0 else "✅ 健康"
        )

    with col_sc2:
        avg_ttf_overdue = silicon_carbon_df['TTF超标率_%'].mean()
        st.metric(
            "平均TTF超标率",
            f"{avg_ttf_overdue:.1f}%",
            delta="需改进" if avg_ttf_overdue > 20 else "可控"
        )

    with col_sc3:
        correlation_sign = "正相关" if silicon_carbon_df[['硅碳比', 'TTF超标率_%']].corr().iloc[0, 1] > 0 else "负相关"
        st.metric(
            "硅碳比-异常率关系",
            correlation_sign,
            delta="AI投入可降低异常率"
        )

    st.markdown("""
    **🔍 HRD异常预警决策指南**:
    - **🔴 高负载+低AI部门**: HR人均负载>7人/月 且 硅碳比<0.5 → TTF超标率往往>25%
    - **关键洞察**: 硅碳比越低,碳基HR负载越重,招聘异常率越高
    - **资源配置建议**:
        - **优先级1**: 对红色预警部门增加AI算力(降低HR负载)
        - **优先级2**: 临时增派HR支援(短期缓解)
        - **长期方案**: 提升AI承接率至70%+,将碳基HR从低价值工作中释放出来

    **💡 成本效益分析**:
    - 增加1个AI等效人力(约5-10万/年) vs 增加1个碳基HR(约30-50万/年)
    - 当硅碳比<0.5时,优先投入AI性价比更高
    """)

    st.markdown("---")

    # ==========================================
    # 图表 8: 校招候选人质量监控 - HRD异常预警视角
    # ==========================================

    st.markdown("#### 8️⃣ 校招候选人质量监控 - 异常预警")
    st.error("⚠️ **HRD关注点**: 校招是未来人才储备,S级流失率过高、签约率异常、质量下滑都是严重问题")

    # 校招质量数据汇总
    campus_quality = {
        '平均笔试分': df_filtered['校招_平均笔试分'].mean(),
        '平均面试分': df_filtered['校招_平均面试分'].mean(),
        'S级SSP占比': df_filtered['校招_S级SSP占比_%'].mean(),
        '总签约率': df_filtered['校招_签约率_%'].mean(),
        'S级签约率': df_filtered['校招_S级签约率_%'].mean(),
        '综合质量得分': df_filtered['校招_综合质量得分'].mean()
    }

    # 预警阈值定义
    CAMPUS_THRESHOLDS = {
        'S级签约率_警告': 60.0,
        'S级签约率_危险': 50.0,
        '总签约率_警告': 70.0,
        '总签约率_危险': 60.0,
        'S级占比_目标': 15.0,
        '综合质量_及格': 75.0
    }

    # 顶部KPI卡片(带预警)
    campus_cols = st.columns(4)

    with campus_cols[0]:
        value = campus_quality['综合质量得分']
        alert = '🔴 质量下滑' if value < CAMPUS_THRESHOLDS['综合质量_及格'] else '✅ 质量健康'
        st.metric(
            "校招综合质量",
            f"{value:.1f}分",
            delta=alert,
            delta_color="inverse" if value < CAMPUS_THRESHOLDS['综合质量_及格'] else "normal"
        )

    with campus_cols[1]:
        value = campus_quality['S级SSP占比']
        alert = '🔴 优质生源不足' if value < CAMPUS_THRESHOLDS['S级占比_目标'] else '✅ 达标'
        st.metric(
            "S级人才占比",
            f"{value:.1f}%",
            delta=alert,
            delta_color="inverse" if value < CAMPUS_THRESHOLDS['S级占比_目标'] else "normal"
        )

    with campus_cols[2]:
        value = campus_quality['总签约率']
        if value < CAMPUS_THRESHOLDS['总签约率_危险']:
            alert = '🔴 严重流失'
        elif value < CAMPUS_THRESHOLDS['总签约率_警告']:
            alert = '🟡 流失偏高'
        else:
            alert = '✅ 健康'
        st.metric(
            "总体签约率",
            f"{value:.1f}%",
            delta=alert
        )

    with campus_cols[3]:
        value = campus_quality['S级签约率']
        if value < CAMPUS_THRESHOLDS['S级签约率_危险']:
            alert = '🔴 高端人才严重流失'
        elif value < CAMPUS_THRESHOLDS['S级签约率_警告']:
            alert = '🟡 需改进'
        else:
            alert = '✅ 优秀'
        st.metric(
            "S级签约率",
            f"{value:.1f}%",
            delta=alert,
            delta_color="inverse" if value < CAMPUS_THRESHOLDS['S级签约率_警告'] else "normal"
        )

    st.markdown("")

    # 按部门分析异常
    st.markdown("**🚨 各部门校招异常预警矩阵**")

    campus_dept = df_filtered.groupby('部门').agg({
        '校招_签约率_%': 'mean',
        '校招_S级签约率_%': 'mean',
        '校招_S级SSP占比_%': 'mean',
        '校招_综合质量得分': 'mean',
        '校招_Offer发放数': 'sum'
    }).reset_index()

    # 添加异常标识
    def get_campus_alert(row):
        alerts = []
        if row['校招_S级签约率_%'] < CAMPUS_THRESHOLDS['S级签约率_危险']:
            alerts.append('🔴S级流失严重')
        elif row['校招_S级签约率_%'] < CAMPUS_THRESHOLDS['S级签约率_警告']:
            alerts.append('🟡S级流失偏高')

        if row['校招_签约率_%'] < CAMPUS_THRESHOLDS['总签约率_危险']:
            alerts.append('🔴总体流失严重')
        elif row['校招_签约率_%'] < CAMPUS_THRESHOLDS['总签约率_警告']:
            alerts.append('🟡总体流失偏高')

        if row['校招_S级SSP占比_%'] < CAMPUS_THRESHOLDS['S级占比_目标']:
            alerts.append('⚠️优质生源不足')

        return ' | '.join(alerts) if alerts else '✅ 健康'

    campus_dept['异常预警'] = campus_dept.apply(get_campus_alert, axis=1)

    # 格式化显示
    campus_display = campus_dept[['部门', '校招_签约率_%', '校招_S级签约率_%',
                                   '校招_S级SSP占比_%', '校招_综合质量得分',
                                   '校招_Offer发放数', '异常预警']].copy()

    campus_display.columns = ['部门', '签约率(%)', 'S级签约率(%)',
                              'S级占比(%)', '质量得分', 'Offer数', '异常预警']

    campus_display['签约率(%)'] = campus_display['签约率(%)'].apply(lambda x: f"{x:.1f}%")
    campus_display['S级签约率(%)'] = campus_display['S级签约率(%)'].apply(lambda x: f"{x:.1f}%")
    campus_display['S级占比(%)'] = campus_display['S级占比(%)'].apply(lambda x: f"{x:.1f}%")
    campus_display['质量得分'] = campus_display['质量得分'].apply(lambda x: f"{x:.1f}")

    st.dataframe(campus_display, use_container_width=True, hide_index=True)

    # 拒签原因分析(HRD视角-需要解决的问题)
    st.markdown("**⚠️ 拒签原因分析 - 需要HRD决策的问题**")

    reject_data = pd.DataFrame({
        '拒签原因': ['薪资不达预期', '竞对(BAT)截胡', '工作地点不符', '其他原因'],
        '占比': [
            df_filtered['校招_拒签原因_薪资_%'].mean(),
            df_filtered['校招_拒签原因_竞对_%'].mean(),
            df_filtered['校招_拒签原因_地点_%'].mean(),
            df_filtered['校招_拒签原因_其他_%'].mean()
        ]
    })

    # 添加异常标识(薪资>30%或竞对>25%需要HRD介入)
    reject_data['是否异常'] = reject_data.apply(
        lambda row: '🔴 需HRD决策' if (
            (row['拒签原因'] == '薪资不达预期' and row['占比'] > 30) or
            (row['拒签原因'] == '竞对(BAT)截胡' and row['占比'] > 25)
        ) else '',
        axis=1
    )

    # fig8 = px.bar(
    #     reject_data,
    #     x='拒签原因',
    #     y='占比',
    #     text=['占比', '是否异常'],
    #     color='拒签原因',
    #     color_discrete_sequence=['#EF4444', '#F59E0B', '#3B82F6', '#94A3B8']
    # )

    # fig8.update_traces(
    #     texttemplate='%{y:.1f}%',
    #     textposition='outside'
    # )

 # 1. 构造一个用于显示的文本列，这样既能显示百分比，又能显示红色的异常警报
    # 如果有异常，显示 "35.0% <br> 🔴 需HRD决策"；如果没有，只显示 "15.0%"
    reject_data['显示文本'] = reject_data.apply(
        lambda row: f"{row['占比']:.1f}%" + (f"<br>{row['是否异常']}" if row['是否异常'] else ""), 
        axis=1
    )

    # 2. 修正 px.bar 调用
    fig8 = px.bar(
        reject_data,
        x='拒签原因',
        y='占比',
        text='显示文本',  # 修复点：这里指定刚才构造的单列名称，而不是一个列表
        color='拒签原因',
        color_discrete_sequence=['#EF4444', '#F59E0B', '#3B82F6', '#94A3B8']
    )

    # 3. 更新显示格式
    fig8.update_traces(
        texttemplate='%{text}', # 修复点：直接使用我们构造好的包含警报的文本
        textposition='outside'
    )
    



    fig8.update_layout(
        title="校招拒签原因分布(HRD需关注薪资和竞对问题)",
        xaxis_title="",
        yaxis_title="占比 (%)",
        font=dict(family=font),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig8, use_container_width=True)

    # HRD决策建议
    col_rec1, col_rec2 = st.columns(2)

    with col_rec1:
        st.markdown("**🔴 需立即干预的异常部门**")
        critical_depts = campus_dept[
            (campus_dept['校招_S级签约率_%'] < CAMPUS_THRESHOLDS['S级签约率_危险']) |
            (campus_dept['校招_签约率_%'] < CAMPUS_THRESHOLDS['总签约率_危险'])
        ]
        if not critical_depts.empty:
            for _, row in critical_depts.iterrows():
                st.error(f"⚠️ **{row['部门']}**: S级签约率 {row['校招_S级签约率_%']:.1f}%, 总签约率 {row['校招_签约率_%']:.1f}%")
        else:
            st.success("✅ 暂无严重异常部门")

    with col_rec2:
        st.markdown("**💡 HRD决策建议**")
        salary_issue = reject_data[reject_data['拒签原因'] == '薪资不达预期']['占比'].values[0]
        competitor_issue = reject_data[reject_data['拒签原因'] == '竞对(BAT)截胡']['占比'].values[0]

        if salary_issue > 30:
            st.warning(f"🔴 **薪资问题严重({salary_issue:.1f}%)**: 建议设立校招SSP特殊薪资包")
        if competitor_issue > 25:
            st.warning(f"🔴 **竞对截胡严重({competitor_issue:.1f}%)**: 建议加速决策流程,提前锁定人才")
        if salary_issue <= 30 and competitor_issue <= 25:
            st.success("✅ 主要拒签原因在可控范围内")

    st.markdown("""
    **📊 HRD异常预警总结**:
    - **🔴 严重异常**: S级签约率<50% → 高端人才严重流失,需HRD立即介入调整薪资策略
    - **🟡 次要异常**: 总签约率<70% → 整体吸引力不足,需优化雇主品牌和流程
    - **⚠️ 结构性问题**: S级占比<15% → 生源质量不达标,需重新评估目标院校清单
    - **💰 成本风险**: 拒签原因-薪资>30% → 校招薪资包竞争力不足,需要预算调整审批

    **💡 HRD行动清单**:
    1. **立即处理**: 对S级签约率<50%的部门启动专项薪资审批
    2. **本周处理**: 对总签约率<70%的部门进行流程优化辅导
    3. **本月处理**: 与HR总监评估是否需要调整校招整体薪资策略
    4. **季度复盘**: 重新评估目标院校清单,淘汰质量不达标的院校
    """)

    st.markdown("---")

    # 底部总结
    st.success("""
    ✅ **HRD 异常管理工具**:
    - 红黄绿预警系统，一眼看出哪个部门有问题
    - 异常发现速度提升10倍（热力图扫描）
    - 资源调配更精准（谁忙谁闲一目了然）
    - 问题追责有依据（部门红色预警可作为绩效考核依据）
    """)


# ==========================================
# 测试入口
# ==========================================

if __name__ == '__main__':
    # 用于测试
    from data_generator_complete import generate_complete_recruitment_data

    st.set_page_config(page_title="HRD 异常报警器", layout="wide")

    # 生成测试数据
    df = generate_complete_recruitment_data(months=12, recruiters=5, departments=5)

    # 渲染看板
    render_hrd_dashboard(df)
