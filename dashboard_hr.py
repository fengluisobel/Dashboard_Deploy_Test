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
            Task Manager - 智能工作推荐与重点指引
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # 使用预筛选数据（数据已在主程序侧边栏中筛选）
    # ==========================================
    
    # 数据已在主程序中筛选完成，直接使用传入的 df
    df_filtered = df.copy()


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
        
        # [Data Capture] 今日待办清单
        st.session_state['current_charts_data']['HR - 今日待办清单'] = todo_df

        # 按优先级排序

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
    
    # [Data Capture] 核心指标矩阵
    st.session_state['current_charts_data']['HR - 核心指标矩阵'] = metrics_df

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
        # 模拟生成过去6个月的数据（含本月）
        current_date = datetime.now()
        months = []
        targets = []
        actuals = []
        
        # 固定的模拟趋势数据
        base_targets = [18, 20, 22, 20, 25, 22] # 过去5个月+本月
        
        for i in range(5, -1, -1):
            m = current_date - timedelta(days=30*i)
            m_str = m.strftime('%Y-%m')
            
            # 目标
            tgt = base_targets[5-i]
            
            # 实际完成：模拟一些波动
            if i == 0: # 本月
                act = tgt * 1.02 # 本月刚好达标一点点
            else:
                # 历史数据随机波动 0.8 ~ 1.1
                variance = 0.8 + (0.3 * np.random.rand()) 
                act = int(tgt * variance)
            
            months.append(m_str)
            targets.append(tgt)
            actuals.append(int(act))

        progress_df = pd.DataFrame({
            '月份': months,
            '目标': targets,
            '实际': actuals
        })
        
        # [Data Capture] 月度指标达成
        st.session_state['current_charts_data']['HR - 月度指标达成进度'] = progress_df
        
        # 计算达成率
        progress_df['达成率'] = (progress_df['实际'] / progress_df['目标'] * 100).round(1)

        # 绘图
        fig_progress = go.Figure()
        
        # 1. 目标柱状图 (背景)
        fig_progress.add_trace(go.Bar(
            x=progress_df['月份'],
            y=progress_df['目标'],
            name='目标人数',
            marker_color='rgba(200,200,200,0.3)',
            width=0.6,
            hoverinfo='y+name'
        ))

        # 2. 实际完成柱状图 (前景)
        # 为当前月份设置高亮色
        bar_colors = [colors[0]] * 5 + ['#ffc107'] # 最后一个月用醒目的黄色/橙色
        
        fig_progress.add_trace(go.Bar(
            x=progress_df['月份'],
            y=progress_df['实际'],
            name='实际入职',
            marker_color=bar_colors,
            width=0.4,
            text=progress_df['实际'].apply(lambda x: f'{x}人'),
            textposition='auto',
            hoverinfo='y+name'
        ))

        # 3. 添加本月高亮框 (Annotation)
        current_month_x = list(progress_df['月份'])[-1]
        current_month_y = max(list(progress_df['目标'])[-1], list(progress_df['实际'])[-1])
        
        fig_progress.add_annotation(
            x=current_month_x,
            y=current_month_y + 2,
            text="本月最新",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#ffc107"
        )

        fig_progress.update_layout(
            title=f"{selected_recruiter} 的月度招聘指标达成趋势",
            xaxis_title="月份",
            yaxis_title="入职人数",
            font=dict(family=font),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            barmode='overlay', # 覆盖模式实现子弹图效果
            xaxis=dict(type='category'), # 关键修正：强制使用分类轴，解决柱子过细问题
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )

        st.plotly_chart(fig_progress, use_container_width=True)

        # 达成分析
        current_rate = list(progress_df['达成率'])[-1]
        
        if current_rate >= 100:
            st.success(f"✅ 本月目前达成率 {current_rate}%，势头不错，继续保持！")
        elif current_rate >= 90:
            st.warning(f"⚠️ 本月目前达成率 {current_rate}%，距离目标只有一步之遥！")
        else:
            st.error(f"🔴 本月目前达成率 {current_rate}%，需要加大搜寻力度！")
            
    st.markdown("---")

    # 图表 2: 个人转化率漏斗 - 精准度分析
    st.markdown("#### 2️⃣ 我的简历推荐精准度分析")

    if len(df_filtered) > 0:
        # 重新模拟严格递减的漏斗数据
        # 逻辑：推荐 > 初筛 > 面试 > 录用
        
        # 基于真实数据的基础量级
        base_recommend = df_filtered['个人推荐简历数'].sum()
        if base_recommend == 0: base_recommend = 150 # 默认值防止为空
        
        # 强制设置递减比例
        n_recommend = int(base_recommend)
        n_screen = int(n_recommend * 0.65)   # 初筛通过率 ~65%
        n_interview = int(n_screen * 0.45)   # 面试通过率 ~45%
        n_hired = int(n_interview * 0.35)    # 最终录用率 ~35%
        
        funnel_data = pd.DataFrame({
            '阶段': ['推荐简历', '初筛通过', '面试通过', '最终录用'],
            '人数': [n_recommend, n_screen, n_interview, n_hired]
        })
        
        # [Data Capture] 简历漏斗
        st.session_state['current_charts_data']['HR - 简历转化漏斗'] = funnel_data
        
        # 计算相对于上一环节的转化率
        funnel_data['转化率'] = [
            '100%', 
            f'{(n_screen/n_recommend*100):.1f}%',
            f'{(n_interview/n_screen*100):.1f}%',
            f'{(n_hired/n_interview*100):.1f}%'
        ]
        
        overall_conversion = (n_hired / n_recommend * 100)

        col1, col2 = st.columns([1, 2])
        
        with col1:
            # 精准度仪表盘 (使用整体转化率)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=overall_conversion,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "简历推荐 → 录用转化率", 'font': {'size': 16}},
                gauge={
                    'axis': {'range': [0, 50], 'tickwidth': 1},
                    'bar': {'color': colors[0]},
                    'steps': [
                        {'range': [0, 5], 'color': 'rgba(220,53,69,0.3)'},   # <5% 差
                        {'range': [5, 10], 'color': 'rgba(255,193,7,0.3)'},  # 5-10% 一般
                        {'range': [10, 50], 'color': 'rgba(40,167,69,0.3)'}  # >10% 优秀 (行业平均通常在1-5%左右，这里为了演示好看设高点)
                    ],
                    'threshold': {
                        'line': {'color': "green", 'width': 4},
                        'thickness': 0.75,
                        'value': 10
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # 简短评价
            if overall_conversion >= 10:
                st.success("✅ **推人很准！**\n每推荐10人就有1人入职")
            else:
                st.info("💡 **提高精准度**\n建议多与业务对齐JD")
        
        with col2:
            # 漏斗图
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_data['阶段'],
                x=funnel_data['人数'],
                textinfo="value+percent previous", # 显示数值和相对于上一环节的百分比
                marker=dict(color=[colors[0], colors[1], '#6610f2', '#28a745']),
                connector=dict(line=dict(color="rgba(128,128,128,0.5)", width=2))
            ))
            
            fig_funnel.update_layout(
                title=f"{selected_recruiter} 的简历转化漏斗 (本月)",
                font=dict(family=font),
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            # Call-out for drop-off
            fig_funnel.add_annotation(
                text="📉 面试流失严重 (-55%)",
                x=n_interview, y='面试通过',
                showarrow=True, arrowhead=1, ax=100, ay=0,
                font=dict(color="red")
            )
            
            st.plotly_chart(fig_funnel, use_container_width=True)

    st.markdown("---")

    # 图表 3: 待处理候选人数趋势
    st.markdown("#### 3️⃣ 我的待处理候选人数趋势 (工作负荷)")

    if len(df_filtered) > 0:
        # A. 负荷趋势图 (折线图)
        st.markdown("##### ⏳ 招聘流程耗时月度趋势")
        
        # 1. 模拟过去12个月的"平均流程耗时"
        dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
        months_str = [d.strftime('%Y-%m') for d in dates]
        
        # 模拟耗时数据：假设最近稍微由于hc增加变慢了
        avg_days = [15, 14, 16, 15, 18, 20, 22, 21, 19, 20, 23, 25]
        
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=months_str,
            y=avg_days,
            mode='lines+markers+text',
            name='平均流程天数',
            text=[f'{d}天' for d in avg_days],
            textposition='top center',
            line=dict(color='#fd7e14', width=3),
            marker=dict(size=8, color='#fd7e14')
        ))
        
        # 警戒线
        fig_trend.add_hline(y=20, line_dash="dash", line_color="red", annotation_text="警戒线 (20天)")
        
        fig_trend.update_layout(
            autosize=True,
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis_title="平均流程天数(Day)",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        
        # B. 超时候选人分布 (散点图)
        st.markdown("##### 🚨 待处理候选人积压分布 (按岗位)")
        
        # 模拟当下积压的候选人数据
        # 字段: 候选人姓名, 应聘岗位, 当前停留天数, 状态
        
        positions = ['Java研发专家', '高级前端', '产品经理', 'HRBP', '算法工程师', '测试开发']
        
        backlog_data = []
        for i in range(30): # 模拟30个待处理
            pos = np.random.choice(positions)
            days = np.random.randint(1, 40) # 1-40天
            
            # 定义严重程度
            if days > 15:
                status = '严重超时'
                color = '#dc3545' # Red
                size = 15 + (days-15) # 越久球越大
            elif days > 7:
                status = '即将超时'
                color = '#ffc107' # Warning
                size = 12
            else:
                status = '正常'
                color = '#28a745' # Green
                size = 8
                
            backlog_data.append({
                '候选人': f'候选人_{i+100}',
                '岗位': pos,
                '停留天数': days,
                '状态': status,
                'Color': color,
                'Size': size
            })
            
        df_backlog = pd.DataFrame(backlog_data)
        
        # 绘制散点图
        fig_scatter = px.scatter(
            df_backlog,
            x='岗位',
            y='停留天数',
            color='状态',
            color_discrete_map={'严重超时': '#dc3545', '即将超时': '#ffc107', '正常': '#28a745'},
            hover_data=['候选人', '停留天数'],
            size='Size', # 大小映射
            size_max=25
        )
        
        fig_scatter.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="严重积压线")
        
        fig_scatter.update_layout(
            height=400,
            yaxis_title="当前积压天数",
            showlegend=True,
            plot_bgcolor='rgba(240,240,240,0.5)'
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # 找出最严重的几个
        critical_ones = df_backlog[df_backlog['停留天数'] > 15].sort_values('停留天数', ascending=False)
        if len(critical_ones) > 0:
            st.error(f"🔥 **严重积压报警**: 发现 {len(critical_ones)} 位候选人停留超过15天！")
            
            cols = st.columns(3)
            for i, (idx, row) in enumerate(critical_ones.head(3).iterrows()):
                with cols[i]:
                    st.markdown(f"""
                    <div style="background-color: #ffebec; padding: 10px; border-radius: 5px; border: 1px solid #dc3545;">
                        <div style="font-weight: bold; color: #dc3545;">{row['候选人']}</div>
                        <div style="font-size: 0.9em; color: #666;">{row['岗位']}</div>
                        <div style="font-size: 0.8em; color: #999;">已卡 {row['停留天数']} 天</div>
                        <div style="text-align: right; margin-top: 5px;">
                            <a href="#" style="color: #dc3545; font-weight: bold; text-decoration: none;">👉 立即催办</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

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

        # 模拟拒签候选人数据（使用更真实的分布）
        rejected_candidates = []
        
        # 更加真实的拒签原因分布权重
        rejection_reasons = ['接受其他Offer', '薪资未达预期', '工作地点不合适', '继续深造', '家庭原因', '发展空间顾虑', '公司文化不匹配']
        reason_weights = [0.35, 0.25, 0.15, 0.10, 0.08, 0.05, 0.02]  # 权重不同
        
        # 生成更多样本数据
        np.random.seed(42)
        num_samples = max(15, len(df_filtered))
        
        for i in range(num_samples):
            reason = np.random.choice(rejection_reasons, p=reason_weights)
            rejected_candidates.append({
                '候选人': f"候选人{i+1}",
                '学校': np.random.choice(['清华大学', '北京大学', '上海交大', '浙江大学', '复旦大学', '南京大学', '武汉大学', '中科大']),
                '部门': np.random.choice(['技术部', '产品部', '市场部', '运营部', '财务部']),
                '拒签原因': reason,
                '拒签日期': f'2026-01-{np.random.randint(1, 25):02d}',
                '建议回访时间': f'2026-01-{np.random.randint(25, 31):02d}',
                '回访目的': {
                    '接受其他Offer': '了解竞品优势',
                    '薪资未达预期': '收集薪资市场信息',
                    '工作地点不合适': '维护候选人关系',
                    '继续深造': '了解学生就业倾向',
                    '家庭原因': '保持联系待未来机会',
                    '发展空间顾虑': '收集职业发展期望',
                    '公司文化不匹配': '收集文化认知反馈'
                }.get(reason, '常规跟进'),
                '回访状态': np.random.choice(['待回访', '已安排', '已完成'], p=[0.5, 0.3, 0.2])
            })

        rejected_df = pd.DataFrame(rejected_candidates)

        # 筛选待回访
        pending_callback = rejected_df[rejected_df['回访状态'] == '待回访']

        if len(pending_callback) > 0:
            st.warning(f"⚠️ 有 {len(pending_callback)} 位拒签候选人待回访")

            st.dataframe(
                pending_callback[['候选人', '学校', '部门', '拒签原因', '拒签日期', '回访目的']],
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

        # 拒签原因统计 - 使用联动环形图(Sunburst)
        st.markdown("##### 📊 拒签原因分析")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 按部门和原因统计
            sunburst_data = rejected_df.groupby(['部门', '拒签原因']).size().reset_index(name='人数')
            
            # 创建Sunburst图（联动环形图）
            fig_sunburst = px.sunburst(
                sunburst_data,
                path=['部门', '拒签原因'],
                values='人数',
                color='人数',
                color_continuous_scale='RdYlGn_r',
                title="校招拒签原因分布 (按部门细分)"
            )
            
            fig_sunburst.update_layout(
                font=dict(family=font),
                height=400,
                margin=dict(l=10, r=10, t=50, b=10)
            )
            
            fig_sunburst.update_traces(
                textinfo='label+percent entry',
                insidetextorientation='radial'
            )
            
            st.plotly_chart(fig_sunburst, use_container_width=True)
        
        with col2:
            # 原因排名
            reason_stats = rejected_df['拒签原因'].value_counts()
            
            st.markdown("**拒签原因排名**")
            for idx, (reason, count) in enumerate(reason_stats.items()):
                pct = count / len(rejected_df) * 100
                emoji = ['🥇', '🥈', '🥉'][idx] if idx < 3 else '📌'
                color = '#dc3545' if idx == 0 else ('#ffc107' if idx == 1 else '#6c757d')
                st.markdown(f"""
                <div style="padding: 8px; margin: 4px 0; border-radius: 8px; 
                            background: linear-gradient(90deg, {color}30 {pct}%, transparent {pct}%);">
                    {emoji} <b>{reason}</b>: {count}人 ({pct:.1f}%)
                </div>
                """, unsafe_allow_html=True)
            
            # 关键行动
            st.markdown("---")
            st.markdown("**🎯 关键行动**")
            top_reason = reason_stats.index[0] if len(reason_stats) > 0 else "未知"
            action_map = {
                '接受其他Offer': '加强竞品分析，优化面试节奏',
                '薪资未达预期': '更新薪资结构，提前沟通预期',
                '工作地点不合适': '考虑远程/弹性工作政策',
                '继续深造': '建立暑期实习→全职通道',
                '家庭原因': '完善候选人池，保持长期联系',
                '发展空间顾虑': '强化职业发展路径介绍',
                '公司文化不匹配': '优化校园宣讲内容'
            }
            st.info(f"**{top_reason}**是主因\n\n💡 {action_map.get(top_reason, '持续优化招聘策略')}")

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

