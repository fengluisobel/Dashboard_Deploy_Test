"""
HR 任务管理器 v3.0 Pro
老板要求："别盯着报表看，去干活！把这个人处理掉"

核心定位：
- 把看板做成"任务管理器"，告诉HR今天该冲哪儿
- 今日待办清单置顶，行动导向
- 仅可见个人负责的职位和候选人
- 每日/每周时间粒度
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 导入品牌色系统
from brand_color_system import get_brand_colors, get_primary_color, get_brand_font


# ==========================================
# HR 核心执行指标定义
# ==========================================

HR_EXECUTION_METRICS = {
    '待处理候选人数': {
        'name': '今日待办候选人数',
        'name_en': 'Action Required Candidates',
        'category': '每日作战',
        'unit': '人',
        'formula': 'Count(状态=待处理 AND 停留时间>24h)',
        'definition': '列出所有卡在待筛选、待安排环节超过SLA时限的候选人',
        'boss_comment': '别盯着报表看，去干活！把这个人处理掉',
        'threshold': {
            '正常': '<15人',
            '繁忙': '15-25人',
            '过载': '>25人'
        },
        'warning_level': 15.0,
        'critical_level': 25.0,
        'review_cadence': 'Daily'
    },

    '流程停滞天数': {
        'name': '流程停滞天数',
        'name_en': 'Stuck Days',
        'category': '流程卫生',
        'unit': '天',
        'formula': '候选人在当前状态的停留天数',
        'definition': '监控每一个候选人的"静止时间"',
        'boss_comment': '时间就是生命，拖三天人家就去别家入职了',
        'threshold': {
            '正常': '<3天',
            '警告': '3-5天',
            '严重': '>5天'
        },
        'warning_level': 3.0,
        'critical_level': 5.0,
        'review_cadence': 'Daily'
    },

    '今日面试数': {
        'name': '即将到来的面试',
        'name_en': 'Upcoming Interviews',
        'category': '日程管理',
        'unit': '场',
        'formula': '未来24/48小时内的面试安排列表',
        'definition': '确保面试官和候选人都已确认出席',
        'boss_comment': '基本功不能丢',
        'threshold': {
            '正常': '确认率>90%',
            '风险': '确认率80-90%',
            '危险': '确认率<80%'
        },
        'warning_level': 90.0,
        'critical_level': 80.0,
        'review_cadence': 'Daily'
    },

    '个人转化率_%': {
        'name': '个人漏斗转化率',
        'name_en': 'Personal Conversion Rate',
        'category': '自我修正',
        'unit': '%',
        'formula': '我推荐的简历通过数 / 我推荐的简历总数 × 100%',
        'definition': '衡量个人推人的"精准度"',
        'boss_comment': '不要做简历搬运工，要做人才顾问',
        'threshold': {
            '优秀': '>30%',
            '良好': '20-30%',
            '需改进': '<20%'
        },
        'warning_level': 30.0,
        'critical_level': 20.0,
        'review_cadence': 'Weekly'
    },

    '月度SLA达成进度_%': {
        'name': '个人月度SLA达成进度',
        'name_en': 'SLA Progress',
        'category': '结果交付',
        'unit': '%',
        'formula': '本月已入职数 / 本月承诺目标数 × 100%',
        'definition': '最直观的业绩进度条',
        'boss_comment': '结果导向',
        'threshold': {
            '优秀': '>100%',
            '达标': '90-100%',
            '需冲刺': '<90%'
        },
        'warning_level': 100.0,
        'critical_level': 90.0,
        'review_cadence': 'Weekly'
    }
}


# ==========================================
# 任务优先级定义
# ==========================================

TASK_PRIORITIES = {
    'P0_紧急': {
        'emoji': '🔴',
        'color': '#dc3545',
        'description': '今日必须完成',
        'examples': ['停滞>3天的候选人', 'Offer待确认(今日到期)', '面试爽约跟进']
    },
    'P1_重要': {
        'emoji': '🟠',
        'color': '#fd7e14',
        'description': '本周必须完成',
        'examples': ['待安排面试', '背调跟进', '入职手续办理']
    },
    'P2_常规': {
        'emoji': '🔵',
        'color': '#0d6efd',
        'description': '按计划推进',
        'examples': ['初筛通过待推荐', '简历寻访', '候选人维护']
    }
}


# ==========================================
# HR 看板渲染函数
# ==========================================

def render_hr_dashboard(df, selected_recruiter='张伟'):
    """
    渲染 HR 任务管理器

    Parameters:
    -----------
    df : pandas.DataFrame
        完整招聘数据
    selected_recruiter : str
        当前登录的招聘顾问姓名
    """

    # 品牌色
    colors = get_brand_colors()
    primary_color = get_primary_color()
    font = get_brand_font()

    # ==========================================
    # 顶部：角色标识 + 个人信息
    # ==========================================

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 24px rgba(0,0,0,0.12);">
        <h1 style="color: white; margin: 0; font-size: 2rem;">✅ {selected_recruiter} 的工作台</h1>
        <p style="color: white; opacity: 0.95; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Task Manager - 今天该冲哪儿
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # 筛选器 (HR只能选自己的数据)
    # ==========================================

    st.subheader("🔍 我的数据范围")

    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        # HR只能选择自己
        st.info(f"👤 当前用户: **{selected_recruiter}**")

    with col_filter2:
        time_range = st.selectbox(
            "时间范围",
            ["今日", "本周", "本月", "自定义"],
            key="hr_time_range"
        )

    with col_filter3:
        if time_range == "自定义":
            custom_days = st.number_input("过去N天", min_value=1, max_value=90, value=7, key="hr_custom_days")

    # 数据筛选 - 只看自己的数据
    df_my_data = df[df['招聘顾问'] == selected_recruiter].copy()

    # 时间筛选
    if time_range == "今日":
        today = df_my_data['月份'].max()
        df_filtered = df_my_data[df_my_data['月份'] == today]
    elif time_range == "本周":
        last_week = df_my_data['月份'].max() - pd.Timedelta(days=7)
        df_filtered = df_my_data[df_my_data['月份'] >= last_week]
    elif time_range == "本月":
        current_month = df_my_data['月份'].max().replace(day=1)
        df_filtered = df_my_data[df_my_data['月份'] >= current_month]
    else:
        cutoff_date = df_my_data['月份'].max() - pd.Timedelta(days=custom_days)
        df_filtered = df_my_data[df_my_data['月份'] >= cutoff_date]

    st.markdown("---")

    # ==========================================
    # 今日待办清单 (置顶! 最重要!)
    # ==========================================

    st.subheader("📋 今日待办清单 (Action Items)")

    st.error("⚠️ **行动导向**: 以下是你今天必须处理的任务，按优先级排序")

    # 模拟生成待办任务
    todo_tasks = []

    # P0 紧急任务
    stuck_candidates = df_filtered[df_filtered['流程停滞天数'] > 3]
    for _, row in stuck_candidates.head(5).iterrows():
        todo_tasks.append({
            '优先级': 'P0_紧急',
            '任务': f"处理停滞候选人 - {row['部门']} {row['职级']}岗位",
            '停滞天数': f"{row['流程停滞天数']}天",
            '行动指令': '立即联系用人经理催促反馈',
            '截止时间': '今日18:00'
        })

    # 待确认Offer
    pending_offers = df_filtered[df_filtered['待处理_超24小时数'] > 0]
    for _, row in pending_offers.head(3).iterrows():
        todo_tasks.append({
            '优先级': 'P0_紧急',
            '任务': f"Offer待确认 - {row['部门']}",
            '停滞天数': f"{row['待处理_超24小时数']}人",
            '行动指令': '电话跟进候选人，确认接受意向',
            '截止时间': '今日17:00'
        })

    # P1 重要任务
    upcoming_interviews = df_filtered[df_filtered['今日面试数'] > 0]
    for _, row in upcoming_interviews.head(3).iterrows():
        todo_tasks.append({
            '优先级': 'P1_重要',
            '任务': f"今日面试安排 - {row['部门']}",
            '停滞天数': f"{row['今日面试数']}场",
            '行动指令': '确认面试官和候选人都已收到通知',
            '截止时间': '面试前2小时'
        })

    # P2 常规任务
    pending_screening = df_filtered[df_filtered['待处理候选人数'] > 10]
    for _, row in pending_screening.head(2).iterrows():
        todo_tasks.append({
            '优先级': 'P2_常规',
            '任务': f"初筛待处理 - {row['部门']}",
            '停滞天数': f"{row['待处理候选人数']}人",
            '行动指令': '完成简历筛选并推荐给用人经理',
            '截止时间': '本周五'
        })

    # 创建待办表格
    if todo_tasks:
        todo_df = pd.DataFrame(todo_tasks)

        # 按优先级排序
        priority_order = {'P0_紧急': 0, 'P1_重要': 1, 'P2_常规': 2}
        todo_df['优先级排序'] = todo_df['优先级'].map(priority_order)
        todo_df = todo_df.sort_values('优先级排序')

        # 添加emoji和颜色
        todo_df['状态'] = todo_df['优先级'].apply(lambda x: TASK_PRIORITIES[x]['emoji'])

        display_todo = todo_df[['状态', '任务', '停滞天数', '行动指令', '截止时间']].copy()
        display_todo.columns = ['', '任务描述', '涉及数量', '下一步行动', '截止时间']

        st.dataframe(
            display_todo,
            use_container_width=True,
            height=350,
            hide_index=True
        )

        # 任务统计
        col1, col2, col3 = st.columns(3)

        with col1:
            p0_count = len(todo_df[todo_df['优先级'] == 'P0_紧急'])
            st.metric("🔴 紧急任务", f"{p0_count}项", delta="今日必须完成")

        with col2:
            p1_count = len(todo_df[todo_df['优先级'] == 'P1_重要'])
            st.metric("🟠 重要任务", f"{p1_count}项", delta="本周完成")

        with col3:
            p2_count = len(todo_df[todo_df['优先级'] == 'P2_常规'])
            st.metric("🔵 常规任务", f"{p2_count}项", delta="按计划推进")

    else:
        st.success("🎉 恭喜！今日暂无紧急待办任务")

    st.markdown("---")

    # ==========================================
    # 核心执行KPI卡片
    # ==========================================

    st.subheader("📊 我的核心指标")

    kpi_cols = st.columns(5)

    # KPI 1: 待处理候选人数
    with kpi_cols[0]:
        metric_key = '待处理候选人数'
        metric_info = HR_EXECUTION_METRICS[metric_key]

        current_value = df_filtered[metric_key].iloc[-1] if len(df_filtered) > 0 else 0

        if current_value < 15:
            status_color = '#28a745'
            status = '正常'
        elif current_value < 25:
            status_color = '#ffc107'
            status = '繁忙'
        else:
            status_color = '#dc3545'
            status = '过载'

        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {status_color};">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                {metric_info['name']}
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {status_color}; margin-bottom: 0.25rem;">
                {int(current_value)}人
            </div>
            <div style="font-size: 0.85rem; color: {status_color};">
                {status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # KPI 2: 流程停滞天数 (最大值)
    with kpi_cols[1]:
        metric_key = '流程停滞天数'
        metric_info = HR_EXECUTION_METRICS[metric_key]

        current_value = df_filtered[metric_key].max() if len(df_filtered) > 0 else 0

        if current_value < 3:
            status_color = '#28a745'
            status = '正常'
        elif current_value < 5:
            status_color = '#ffc107'
            status = '警告'
        else:
            status_color = '#dc3545'
            status = '严重'

        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {status_color};">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                最长停滞时间
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {status_color}; margin-bottom: 0.25rem;">
                {int(current_value)}天
            </div>
            <div style="font-size: 0.85rem; color: {status_color};">
                {status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # KPI 3: 今日面试数
    with kpi_cols[2]:
        metric_key = '今日面试数'
        metric_info = HR_EXECUTION_METRICS[metric_key]

        current_value = df_filtered['今日面试数'].sum() if len(df_filtered) > 0 else 0
        confirm_rate = df_filtered['面试确认率_%'].mean() if len(df_filtered) > 0 else 100

        if confirm_rate >= 90:
            status_color = '#28a745'
        elif confirm_rate >= 80:
            status_color = '#ffc107'
        else:
            status_color = '#dc3545'

        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {status_color};">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                今日面试安排
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {status_color}; margin-bottom: 0.25rem;">
                {int(current_value)}场
            </div>
            <div style="font-size: 0.85rem; color: {status_color};">
                确认率 {confirm_rate:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    # KPI 4: 个人转化率
    with kpi_cols[3]:
        metric_key = '个人转化率_%'
        metric_info = HR_EXECUTION_METRICS[metric_key]

        current_value = df_filtered[metric_key].mean() if len(df_filtered) > 0 else 0

        if current_value >= 30:
            status_color = '#28a745'
            status = '优秀'
        elif current_value >= 20:
            status_color = '#ffc107'
            status = '良好'
        else:
            status_color = '#dc3545'
            status = '需改进'

        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {status_color};">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                我的转化率
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {status_color}; margin-bottom: 0.25rem;">
                {current_value:.1f}%
            </div>
            <div style="font-size: 0.85rem; color: {status_color};">
                {status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # KPI 5: 月度SLA达成进度
    with kpi_cols[4]:
        metric_key = '月度SLA达成进度_%'
        metric_info = HR_EXECUTION_METRICS[metric_key]

        current_value = df_filtered[metric_key].mean() if len(df_filtered) > 0 else 0

        if current_value >= 100:
            status_color = '#28a745'
            status = '已达标'
        elif current_value >= 90:
            status_color = '#ffc107'
            status = '接近达标'
        else:
            status_color = '#dc3545'
            status = '需冲刺'

        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {status_color};">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                月度SLA进度
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {status_color}; margin-bottom: 0.25rem;">
                {current_value:.0f}%
            </div>
            <div style="font-size: 0.85rem; color: {status_color};">
                {status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # 执行指标详细矩阵
    # ==========================================

    st.subheader("📋 我的执行指标详细矩阵")

    st.info("💡 **自我管理**: 每日复盘，持续改进")

    metrics_table = []

    for metric_key, metric_info in HR_EXECUTION_METRICS.items():
        if metric_key in df_filtered.columns:
            if metric_key == '待处理候选人数':
                current_val = df_filtered[metric_key].iloc[-1] if len(df_filtered) > 0 else 0
            elif metric_key == '流程停滞天数':
                current_val = df_filtered[metric_key].max() if len(df_filtered) > 0 else 0
            elif metric_key == '今日面试数':
                current_val = df_filtered[metric_key].sum() if len(df_filtered) > 0 else 0
            else:
                current_val = df_filtered[metric_key].mean() if len(df_filtered) > 0 else 0

            metrics_table.append({
                '指标名称': metric_info['name'],
                '英文名': metric_info['name_en'],
                '当前值': f"{current_val:.1f}{metric_info['unit']}" if metric_info['unit'] == '%' else f"{current_val:.0f}{metric_info['unit']}",
                '类别': metric_info['category'],
                '复盘频率': metric_info['review_cadence'],
                '老板期望': metric_info['boss_comment']
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
    # 图表区 (辅助分析)
    # ==========================================

    st.subheader("📈 我的工作分析")

    # 图表 1: SLA达成进度趋势
    st.markdown("#### 1️⃣ 我的月度SLA达成进度")

    if len(df_filtered) > 0:
        progress_df = df_filtered.groupby('月份').agg({
            '月度已入职数': 'sum',
            '月度目标入职数': 'mean',
            '月度SLA达成进度_%': 'mean'
        }).reset_index()

        fig_progress = go.Figure()

        fig_progress.add_trace(go.Bar(
            x=progress_df['月份'],
            y=progress_df['月度已入职数'],
            name='已入职',
            marker_color=colors[0]
        ))

        fig_progress.add_trace(go.Scatter(
            x=progress_df['月份'],
            y=progress_df['月度目标入职数'],
            name='目标',
            mode='lines+markers',
            line=dict(color='red', width=2, dash='dash'),
            marker=dict(size=8)
        ))

        fig_progress.update_layout(
            title=f"{selected_recruiter} 的月度SLA达成情况",
            xaxis_title="月份",
            yaxis_title="入职人数",
            font=dict(family=font),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            barmode='group'
        )

        st.plotly_chart(fig_progress, use_container_width=True)

        # 达成分析
        avg_progress = progress_df['月度SLA达成进度_%'].mean()

        if avg_progress >= 100:
            st.success(f"✅ 太棒了！平均达成率 {avg_progress:.1f}%，继续保持！")
        elif avg_progress >= 90:
            st.warning(f"⚠️ 平均达成率 {avg_progress:.1f}%，本月需要加油冲刺！")
        else:
            st.error(f"🔴 平均达成率 {avg_progress:.1f}%，需要分析原因并改进策略")

    st.markdown("---")

    # 图表 2: 个人转化率漏斗
    st.markdown("#### 2️⃣ 我的简历推荐漏斗 (精准度分析)")

    if len(df_filtered) > 0:
        funnel_df = df_filtered.groupby('月份').agg({
            '个人推荐简历数': 'sum',
            '个人简历通过数': 'sum',
            '个人转化率_%': 'mean'
        }).reset_index()

        fig_funnel = go.Figure()

        fig_funnel.add_trace(go.Bar(
            x=funnel_df['月份'],
            y=funnel_df['个人推荐简历数'],
            name='推荐简历数',
            marker_color=colors[1],
            opacity=0.6
        ))

        fig_funnel.add_trace(go.Bar(
            x=funnel_df['月份'],
            y=funnel_df['个人简历通过数'],
            name='通过数',
            marker_color=colors[0]
        ))

        fig_funnel.add_trace(go.Scatter(
            x=funnel_df['月份'],
            y=funnel_df['个人转化率_%'],
            name='转化率',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=10)
        ))

        fig_funnel.update_layout(
            title=f"{selected_recruiter} 的简历推荐精准度",
            xaxis_title="月份",
            yaxis_title="简历数量",
            yaxis2=dict(
                title="转化率 (%)",
                overlaying='y',
                side='right'
            ),
            font=dict(family=font),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )

        st.plotly_chart(fig_funnel, use_container_width=True)

        avg_conversion = funnel_df['个人转化率_%'].mean()

        st.markdown(f"""
        **📊 自我诊断**:
        - 平均转化率: {avg_conversion:.1f}%
        - {'✅ 优秀！推荐简历精准度高' if avg_conversion >= 30 else '⚠️ 需要提升简历筛选标准，减少无效推荐'}
        - **改进建议**: {'继续保持当前标准' if avg_conversion >= 30 else '与用人经理深入沟通JD要求，重新对焦'}
        """)

    st.markdown("---")

    # 图表 3: 待处理候选人数趋势
    st.markdown("#### 3️⃣ 我的待处理候选人数趋势 (工作负荷)")

    if len(df_filtered) > 0:
        backlog_df = df_filtered.groupby('月份').agg({
            '待处理候选人数': 'mean',
            '待处理_超24小时数': 'mean',
            '待处理_超48小时数': 'mean',
            '待处理_超72小时数': 'mean'
        }).reset_index()

        fig_backlog = go.Figure()

        fig_backlog.add_trace(go.Scatter(
            x=backlog_df['月份'],
            y=backlog_df['待处理候选人数'],
            mode='lines+markers',
            name='总待处理数',
            line=dict(color=colors[0], width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor=f'rgba({int(colors[0][1:3], 16)}, {int(colors[0][3:5], 16)}, {int(colors[0][5:7], 16)}, 0.2)'
        ))

        fig_backlog.add_trace(go.Scatter(
            x=backlog_df['月份'],
            y=backlog_df['待处理_超72小时数'],
            mode='lines+markers',
            name='超72小时(严重)',
            line=dict(color='#dc3545', width=2),
            marker=dict(size=8)
        ))

        # 添加警戒线
        fig_backlog.add_hline(
            y=15,
            line_dash="dash",
            line_color="orange",
            annotation_text="繁忙线: 15人",
            annotation_position="right"
        )

        fig_backlog.add_hline(
            y=25,
            line_dash="dash",
            line_color="red",
            annotation_text="过载线: 25人",
            annotation_position="right"
        )

        fig_backlog.update_layout(
            title=f"{selected_recruiter} 的工作负荷监控",
            xaxis_title="月份",
            yaxis_title="待处理人数",
            font=dict(family=font),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )

        st.plotly_chart(fig_backlog, use_container_width=True)

        current_backlog = backlog_df['待处理候选人数'].iloc[-1]

        if current_backlog < 15:
            st.success("✅ 工作负荷健康，保持当前节奏")
        elif current_backlog < 25:
            st.warning("⚠️ 工作负荷较重，建议优先处理超时候选人")
        else:
            st.error("🔴 工作负荷过载！建议向主管申请支援或延长SLA")

    st.markdown("---")

    # 图表 4: 面试安排日历视图
    st.markdown("#### 4️⃣ 未来7天面试安排")

    if len(df_filtered) > 0:
        col1, col2, col3 = st.columns(3)

        with col1:
            today_interviews = df_filtered['今日面试数'].sum()
            st.metric(
                "今日面试",
                f"{int(today_interviews)}场",
                delta=f"确认率 {df_filtered['面试确认率_%'].mean():.1f}%"
            )

        with col2:
            tomorrow_interviews = df_filtered['明日面试数'].sum()
            st.metric(
                "明日面试",
                f"{int(tomorrow_interviews)}场",
                delta="提前确认"
            )

        with col3:
            upcoming_interviews = df_filtered['未来48小时面试数'].sum()
            st.metric(
                "未来48小时",
                f"{int(upcoming_interviews)}场",
                delta="准备面试材料"
            )

        st.info("""
        **📅 面试准备清单**:
        - ✅ 确认面试官和候选人都已收到通知
        - ✅ 准备候选人简历和面试评估表
        - ✅ 预定会议室/视频会议链接
        - ✅ 面试前2小时再次确认
        """)

    st.markdown("---")

    # 底部总结
    st.success("""
    ✅ **HR 工作台总结**:
    - 今日待办清单置顶，告诉你该做什么（不是数据是多少）
    - 减少90%的报表分析时间，聚焦执行和交付
    - 自我修正工具（转化率），持续提升专业能力
    - 结果导向（SLA进度条），清晰可见绩效达成情况
    """)


# ==========================================
# 测试入口
# ==========================================

if __name__ == '__main__':
    # 用于测试
    from data_generator_complete import generate_complete_recruitment_data

    st.set_page_config(page_title="HR 工作台", layout="wide")

    # 生成测试数据
    df = generate_complete_recruitment_data(months=12, recruiters=5, departments=5)

    # 侧边栏选择招聘顾问
    st.sidebar.subheader("👤 选择招聘顾问")
    recruiter_list = df['招聘顾问'].unique().tolist()
    selected_recruiter = st.sidebar.selectbox("当前用户", recruiter_list, key="hr_user_selector")

    # 渲染看板
    render_hr_dashboard(df, selected_recruiter=selected_recruiter)
