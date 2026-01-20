"""
HR 任务管理器 v3.0 Pro
老板要求："别盯着报表看，去干活！把这个人处理掉"

核心定位：
- 把看板做成"任务管理器"，告诉HR今天该做什么
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

# 导入翻转卡片系统
from flip_card_system import inject_flip_card_css, render_metric_flip_card


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
        'definition': '列出所有卡在待筛选、待安排环节超过招聘周期时限的候选人',
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
        'name': '个人月度招聘指标达成进度',
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

    # 注入翻转卡片 CSS
    inject_flip_card_css(primary_color)

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
    # 核心执行KPI卡片 - 翻转卡片系统
    # ==========================================

    st.subheader("📊 我的核心指标")

    kpi_cols = st.columns(5)

    # KPI 1: 待处理候选人数
    with kpi_cols[0]:
        metric_key = '待处理候选人数'
        metric_info = HR_EXECUTION_METRICS[metric_key]

        current_value = df_filtered[metric_key].iloc[-1] if len(df_filtered) > 0 else 0
        target_value = 15.0  # 正常阈值

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=target_value,
            role='HR',
            raw_data_dict={
                '当前待处理': f"{int(current_value)}人",
                '正常阈值': '15人',
                '繁忙阈值': '25人'
            }
        )

    # KPI 2: 流程停滞天数 (最大值)
    with kpi_cols[1]:
        metric_key = '流程停滞天数'
        metric_info = HR_EXECUTION_METRICS[metric_key]

        current_value = df_filtered[metric_key].max() if len(df_filtered) > 0 else 0
        target_value = 3.0  # 正常阈值

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=target_value,
            role='HR',
            raw_data_dict={
                '最长停滞': f"{int(current_value)}天",
                '正常阈值': '3天',
                '警告阈值': '5天'
            }
        )

    # KPI 3: 今日面试数
    with kpi_cols[2]:
        metric_key = '今日面试数'
        metric_info = HR_EXECUTION_METRICS[metric_key]

        current_value = df_filtered['今日面试数'].sum() if len(df_filtered) > 0 else 0
        confirm_rate = df_filtered['面试确认率_%'].mean() if len(df_filtered) > 0 else 100
        target_value = confirm_rate  # 使用确认率作为参考

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=target_value,
            role='HR',
            raw_data_dict={
                '今日面试': f"{int(current_value)}场",
                '确认率': f"{confirm_rate:.1f}%",
                '目标确认率': '90%'
            }
        )

    # KPI 4: 个人转化率
    with kpi_cols[3]:
        metric_key = '个人转化率_%'
        metric_info = HR_EXECUTION_METRICS[metric_key]

        current_value = df_filtered[metric_key].mean() if len(df_filtered) > 0 else 0
        target_value = 30.0  # 优秀标准

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=target_value,
            role='HR',
            raw_data_dict={
                '我的转化率': f"{current_value:.1f}%",
                '优秀标准': '30%',
                '达标线': '20%'
            }
        )

    # KPI 5: 月度SLA达成进度
    with kpi_cols[4]:
        metric_key = '月度SLA达成进度_%'
        metric_info = HR_EXECUTION_METRICS[metric_key]

        current_value = df_filtered[metric_key].mean() if len(df_filtered) > 0 else 0
        target_value = 100.0  # 目标100%

        render_metric_flip_card(
            metric_key=metric_key,
            metric_info=metric_info,
            current_value=current_value,
            target_value=target_value,
            role='HR',
            raw_data_dict={
                '当前进度': f"{current_value:.0f}%",
                '目标': '100%',
                '达标线': '90%'
            }
        )

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
    st.markdown("#### 1️⃣ 我的月度指标达成进度")

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
            title=f"{selected_recruiter} 的月度招聘指标达成情况",
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

    # ==========================================
    # 校招候选人质量执行视图
    # ==========================================

    st.markdown("#### 📋 校招候选人跟进状态")

    st.info("💡 **HR视角关注**: 我负责的校招候选人进度、待处理事项、签约跟进")

    # 模拟校招候选人数据
    # 实际使用时应从 df_filtered 中筛选校招相关数据
    campus_candidates = []

    # 生成待跟进校招候选人列表
    if len(df_filtered) > 0:
        # 模拟校招候选人数据
        campus_招聘类型 = ['校招', '实习生转正', '校招补录']

        for idx, row in df_filtered.head(10).iterrows():
            # 模拟紧急程度
            days_stuck = row.get('流程停滞天数', 0)

            if days_stuck > 5:
                priority = 'P0_紧急'
                priority_emoji = '🔴'
                priority_score = 0
            elif days_stuck > 3:
                priority = 'P1_重要'
                priority_emoji = '🟠'
                priority_score = 1
            else:
                priority = 'P2_常规'
                priority_emoji = '🔵'
                priority_score = 2

            campus_candidates.append({
                '优先级': priority,
                '优先级emoji': priority_emoji,
                '优先级排序': priority_score,
                '候选人': f"张{idx+1}同学",
                '学校': ['清华大学', '北京大学', '上海交大', '浙江大学', '复旦大学'][idx % 5],
                '专业': ['计算机科学', '软件工程', '数据科学', '人工智能', '信息安全'][idx % 5],
                '岗位': row.get('职级', 'P5 软件工程师'),
                '当前状态': ['待安排面试', 'Offer待确认', '背调中', '待入职', '签约谈判中'][idx % 5],
                '停滞天数': int(days_stuck),
                '下一步行动': ['联系候选人确认面试时间', '跟进Offer接受意向', '催促背调公司加快进度', '确认入职日期和材料', '协商薪资待遇'][idx % 5],
                '截止时间': ['今日18:00', '明日12:00', '本周五', '下周一', '3天内'][idx % 5]
            })

    if campus_candidates:
        # 转换为DataFrame并排序
        campus_df = pd.DataFrame(campus_candidates)
        campus_df = campus_df.sort_values('优先级排序')

        # 1. 待跟进校招候选人列表
        st.markdown("##### 📌 待跟进校招候选人列表 (按紧急程度排序)")

        display_campus = campus_df[['优先级emoji', '候选人', '学校', '专业', '岗位', '当前状态', '停滞天数', '下一步行动', '截止时间']].copy()
        display_campus.columns = ['', '候选人', '学校', '专业', '应聘岗位', '当前状态', '停滞天数', '下一步行动', '截止时间']

        st.dataframe(
            display_campus,
            use_container_width=True,
            height=300,
            hide_index=True
        )

        # 统计信息
        col1, col2, col3 = st.columns(3)

        with col1:
            urgent_count = len(campus_df[campus_df['优先级'] == 'P0_紧急'])
            st.metric("🔴 紧急跟进", f"{urgent_count}人", delta="今日必须完成", delta_color="inverse")

        with col2:
            important_count = len(campus_df[campus_df['优先级'] == 'P1_重要'])
            st.metric("🟠 重要跟进", f"{important_count}人", delta="本周完成")

        with col3:
            normal_count = len(campus_df[campus_df['优先级'] == 'P2_常规'])
            st.metric("🔵 常规跟进", f"{normal_count}人", delta="按计划推进")

        st.markdown("---")

        # 2. 校招Offer签约进度
        st.markdown("##### 📊 校招Offer签约进度 (按部门/岗位)")

        # 模拟Offer签约数据
        offer_data = []
        departments = df_filtered['部门'].unique() if len(df_filtered) > 0 else ['技术部', '产品部', '市场部']

        for dept in departments[:5]:
            total_offers = np.random.randint(8, 20)
            signed = np.random.randint(5, total_offers)
            pending = np.random.randint(0, total_offers - signed)
            rejected = total_offers - signed - pending

            offer_data.append({
                '部门': dept,
                '总Offer数': total_offers,
                '已签约': signed,
                '待确认': pending,
                '已拒签': rejected,
                '签约率': f"{(signed/total_offers*100):.1f}%"
            })

        offer_df = pd.DataFrame(offer_data)

        # 可视化
        col1, col2 = st.columns([2, 1])

        with col1:
            # 堆叠柱状图
            fig_offer = go.Figure()

            fig_offer.add_trace(go.Bar(
                x=offer_df['部门'],
                y=offer_df['已签约'],
                name='已签约',
                marker_color='#28a745',
                text=offer_df['已签约'],
                textposition='inside'
            ))

            fig_offer.add_trace(go.Bar(
                x=offer_df['部门'],
                y=offer_df['待确认'],
                name='待确认',
                marker_color='#ffc107',
                text=offer_df['待确认'],
                textposition='inside'
            ))

            fig_offer.add_trace(go.Bar(
                x=offer_df['部门'],
                y=offer_df['已拒签'],
                name='已拒签',
                marker_color='#dc3545',
                text=offer_df['已拒签'],
                textposition='inside'
            ))

            fig_offer.update_layout(
                title="各部门校招Offer签约情况",
                xaxis_title="部门",
                yaxis_title="人数",
                barmode='stack',
                font=dict(family=font),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=350,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            st.plotly_chart(fig_offer, use_container_width=True)

        with col2:
            st.dataframe(
                offer_df,
                use_container_width=True,
                height=350,
                hide_index=True
            )

        # 签约率分析
        avg_sign_rate = offer_df['已签约'].sum() / offer_df['总Offer数'].sum() * 100

        if avg_sign_rate >= 80:
            st.success(f"✅ 整体签约率 {avg_sign_rate:.1f}%，表现优秀！")
        elif avg_sign_rate >= 60:
            st.warning(f"⚠️ 整体签约率 {avg_sign_rate:.1f}%，需要加强候选人沟通和跟进")
        else:
            st.error(f"🔴 整体签约率 {avg_sign_rate:.1f}%，需要分析拒签原因并改进策略")

        st.markdown("---")

        # 3. 校招拒签候选人回访提醒
        st.markdown("##### 📞 校招拒签候选人回访提醒")

        # 模拟拒签候选人数据
        rejected_candidates = []

        for i in range(min(5, len(df_filtered))):
            rejected_candidates.append({
                '候选人': f"李{i+1}同学",
                '学校': ['清华大学', '北京大学', '上海交大', '浙江大学', '复旦大学'][i % 5],
                '拒签原因': ['接受其他Offer', '薪资未达预期', '工作地点不合适', '继续深造', '家庭原因'][i % 5],
                '拒签日期': '2026-01-' + str(15 + i),
                '建议回访时间': '2026-01-' + str(22 + i),
                '回访目的': ['了解竞品优势', '收集薪资市场信息', '维护候选人关系', '了解学生就业倾向', '保持联系待未来机会'][i % 5],
                '回访状态': ['待回访', '已安排', '待回访', '已完成', '待回访'][i % 5]
            })

        rejected_df = pd.DataFrame(rejected_candidates)

        # 筛选待回访
        pending_callback = rejected_df[rejected_df['回访状态'] == '待回访']

        if len(pending_callback) > 0:
            st.warning(f"⚠️ 有 {len(pending_callback)} 位拒签候选人待回访")

            st.dataframe(
                pending_callback,
                use_container_width=True,
                height=200,
                hide_index=True
            )

            st.info("""
            **📋 回访清单**:
            - ✅ 了解候选人真实拒签原因（薪资/发展/团队/地点）
            - ✅ 收集竞争对手信息（哪家公司、什么条件）
            - ✅ 维护候选人关系，为未来合作留下机会
            - ✅ 总结经验，优化后续校招策略
            """)
        else:
            st.success("✅ 所有拒签候选人回访已完成")

        # 拒签原因统计
        st.markdown("##### 📊 拒签原因分析")

        reason_stats = rejected_df['拒签原因'].value_counts()

        fig_reasons = px.pie(
            values=reason_stats.values,
            names=reason_stats.index,
            title="校招拒签原因分布",
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig_reasons.update_layout(
            font=dict(family=font),
            height=300
        )

        st.plotly_chart(fig_reasons, use_container_width=True)

        st.markdown("""
        **💡 改进建议**:
        - 针对主要拒签原因制定针对性应对策略
        - 定期更新薪资待遇和福利政策
        - 加强校招宣讲中的公司文化和发展机会展示
        - 优化面试流程，提升候选人体验
        """)

    else:
        st.info("暂无校招候选人数据")

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
