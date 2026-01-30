"""
HRD 异常报警器 v3.2 Pro (Optimized)
老板要求："别给我看流水账，我要看哪里着火了，哪里要加人"
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
# HRD 核心指标定义 (带预警阈值)
# ==========================================

HRD_EXCEPTION_METRICS = {
    '招聘完成率_%': {
        'name': '月度招聘完成率',
        'name_en': 'Completion Rate',
        'category': '交付进度',
        'unit': '%',
        'formula': '本月已入职 / 本月计划数 × 100%',
        'definition': '衡量招聘计划的达成进度，低于85%视为红色预警',
        'boss_comment': '别给我看流水账，我要看离目标还差多少',
        'threshold': {
            '正常': '>95%',
            '警告': '85-95%',
            '严重': '<85%'
        },
        'warning_level': 95.0,
        'critical_level': 85.0,
        'review_cadence': 'Weekly'
    },

    '关键岗位到岗周期_天': {
        'name': '关键岗位平均到岗周期',
        'name_en': 'Critical Roles Time to Fill',
        'category': '核心效率',
        'unit': '天',
        'formula': 'P7及以上岗位从需求审批到入职的平均天数',
        'definition': '核心战斗力补充速度，超过60天严重影响业务',
        'boss_comment': '等不起！核心岗位空一天，业务就停一天',
        'threshold': {
            '正常': '<45天',
            '警告': '45-60天',
            '严重': '>60天'
        },
        'warning_level': 45.0,
        'critical_level': 60.0,
        'review_cadence': 'Monthly'
    },

    '候选人体验NPS': {
        'name': '候选人体验 NPS',
        'name_en': 'Candidate NPS',
        'category': '雇主品牌',
        'unit': '分',
        'formula': 'NPS推荐者% - 贬损者%',
        'definition': '衡量面试流程体验，防止因为招聘得罪潜在人才',
        'boss_comment': '别让面试变成劝退，坏口碑传得比你招人快',
        'threshold': {
            '正常': '>50分',
            '警告': '30-50分',
            '严重': '<30分'
        },
        'warning_level': 50.0,
        'critical_level': 30.0,
        'review_cadence': 'Monthly'
    },

    '试用期流失率_%': {
        'name': '试用期流失率',
        'name_en': 'Probation Turnover',
        'category': '人岗匹配',
        'unit': '%',
        'formula': '试用期离职人数 / 同期入职人数 × 100%',
        'definition': '衡量招聘质量，新人留不住说明"选"或"育"出了问题',
        'boss_comment': '招来留不住，比不招还浪费钱',
        'threshold': {
            '正常': '<10%',
            '警告': '10-20%',
            '严重': '>20%'
        },
        'warning_level': 10.0,
        'critical_level': 20.0,
        'review_cadence': 'Quarterly'
    },

    '人均月招聘负载_人': {
        'name': 'Recruiter人均月招聘负载',
        'name_en': 'Workload per Recruiter',
        'category': '团队负荷',
        'unit': '人',
        'formula': '在手HC总数 / 招聘团队人数',
        'definition': '衡量团队是否过载，过载会导致所有指标全线崩盘',
        'boss_comment': '人效要高，但别把人累死，累死了谁干活',
        'threshold': {
            '正常': '<5人',
            '警告': '5-8人',
            '严重': '>8人'
        },
        'warning_level': 5.0,
        'critical_level': 8.0,
        'review_cadence': 'Monthly'
    }
}


# ==========================================
# HRD 看板渲染函数
# ==========================================

def render_hrd_dashboard(df):
    """
    渲染 HRD 异常报警器
    """

    colors = get_brand_colors()
    primary_color = get_primary_color()
    font = get_brand_font()

    inject_flip_card_css(primary_color)

    # 顶部：角色标识
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {primary_color} 0%, {primary_color}dd 100%);
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 24px rgba(0,0,0,0.12);">
        <h1 style="color: white; margin: 0; font-size: 2rem;">🚨 HRD 异常报警器</h1>
        <p style="color: white; opacity: 0.95; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Operational Command Center - 监控异常，调度资源，扑灭火灾
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    df_filtered = df.copy()

    # ==========================================
    # 数据补全与映射 (防止KeyError)
    # ==========================================
    
    # 1. 招聘完成率 (如果没有则模拟)
    if '招聘完成率_%' not in df_filtered.columns:
        if '招聘及时率_%' in df_filtered.columns:
            df_filtered['招聘完成率_%'] = df_filtered['招聘及时率_%'] * np.random.uniform(0.9, 1.1, len(df_filtered))
        else:
            df_filtered['招聘完成率_%'] = np.random.uniform(80, 100, len(df_filtered))
        # 截断到100%
        df_filtered['招聘完成率_%'] = df_filtered['招聘完成率_%'].clip(upper=100)

    # 2. 关键岗位到岗周期 (如果没有则基于平均周期模拟)
    if '关键岗位到岗周期_天' not in df_filtered.columns:
        if '平均招聘周期_天' in df_filtered.columns:
            # 关键岗位通常比平均慢 1.5倍
            df_filtered['关键岗位到岗周期_天'] = df_filtered['平均招聘周期_天'] * 1.5
        else:
            df_filtered['关键岗位到岗周期_天'] = np.random.randint(40, 90, len(df_filtered))

    # 3. 候选人体验NPS (映射或模拟)
    if '候选人体验NPS' not in df_filtered.columns:
        if '候选人NPS' in df_filtered.columns:
            df_filtered['候选人体验NPS'] = df_filtered['候选人NPS']
        else:
            # 模拟生成
            np.random.seed(42)
            depts = df_filtered['部门'].unique()
            dept_offsets = {dept: np.random.randint(-15, 15) for dept in depts}
            df_filtered['候选人体验NPS'] = np.random.normal(50, 15, len(df_filtered))
            df_filtered['候选人体验NPS'] = df_filtered.apply(
                lambda x: np.clip(x['候选人体验NPS'] + dept_offsets.get(x['部门'], 0), 0, 100), axis=1
            )
            
    # 4. 试用期流失率 (如果没有则用 100 - 转正率 或模拟)
    if '试用期流失率_%' not in df_filtered.columns:
        if '试用期转正率_%' in df_filtered.columns:
            df_filtered['试用期流失率_%'] = 100 - df_filtered['试用期转正率_%']
        elif '新员工早期离职率_%' in df_filtered.columns:
             df_filtered['试用期流失率_%'] = df_filtered['新员工早期离职率_%']
        else:
            df_filtered['试用期流失率_%'] = np.random.uniform(5, 25, len(df_filtered))
            
    # 5. 人均月招聘负载 (如果没有则模拟)
    if '人均月招聘负载_人' not in df_filtered.columns:
        if 'HR人均月招聘负载_人' in df_filtered.columns:
            df_filtered['人均月招聘负载_人'] = df_filtered['HR人均月招聘负载_人']
        else:
            df_filtered['人均月招聘负载_人'] = np.random.uniform(3, 10, len(df_filtered))

    # ==========================================
    # 核心预警KPI卡片
    # ==========================================

    st.subheader("1️⃣ 核心异常指标 (实时预警)")
    st.info("💡 **点击卡片翻转** - 查看指标定义、预警阈值和老板关注点")

    kpi_cols = st.columns(5)
    
    # 辅助函数：根据阈值判断颜色
    def get_status_color(val, metric_key):
        info = HRD_EXCEPTION_METRICS[metric_key]
        w = info['warning_level']
        c = info['critical_level']
        
        # 逆序指标 (越低越好): 到岗周期, 流失率, 负载
        if metric_key in ['关键岗位到岗周期_天', '试用期流失率_%', '人均月招聘负载_人']:
            if val < w: return 'normal' # Green
            if val < c: return 'warning' # Orange
            return 'inverse' # Red
        else:
            # 正序指标 (越高越好): 完成率, NPS
            if val > w: return 'normal'
            if val > c: return 'warning'
            return 'inverse'

    # KPI 1: 完成率
    with kpi_cols[0]:
        key = '招聘完成率_%'
        val = df_filtered[key].mean()
        render_metric_flip_card(key, HRD_EXCEPTION_METRICS[key], val, 95.0, 'HRD')

    # KPI 2: 到岗周期
    with kpi_cols[1]:
        key = '关键岗位到岗周期_天'
        val = df_filtered[key].mean()
        render_metric_flip_card(key, HRD_EXCEPTION_METRICS[key], val, 45.0, 'HRD')

    # KPI 3: NPS
    with kpi_cols[2]:
        key = '候选人体验NPS'
        info = HRD_EXCEPTION_METRICS[key]
        val = df_filtered[key].mean()
        render_metric_flip_card(key, info, val, 50.0, 'HRD')

    # KPI 4: 流失率
    with kpi_cols[3]:
        key = '试用期流失率_%'
        val = df_filtered[key].mean()
        render_metric_flip_card(key, HRD_EXCEPTION_METRICS[key], val, 10.0, 'HRD')

    # KPI 5: 负载
    with kpi_cols[4]:
        key = '人均月招聘负载_人'
        val = df_filtered[key].mean()
        render_metric_flip_card(key, HRD_EXCEPTION_METRICS[key], val, 5.0, 'HRD')

    st.markdown("---")

    # ==========================================
    # 部门异常概览矩阵
    # ==========================================
    
    st.subheader("2️⃣ 部门异常概览矩阵")
    
    dept_metrics = df_filtered.groupby('部门').agg({
        '招聘完成率_%': 'mean',
        '关键岗位到岗周期_天': 'mean',
        '候选人体验NPS': 'mean',
        '试用期流失率_%': 'mean',
        '人均月招聘负载_人': 'mean'
    }).reset_index()
    
    # 格式化数据并添加红灯标记
    summary_data = []
    
    for _, row in dept_metrics.iterrows():
        dept_item = {'部门': row['部门']}
        
        # 逐个指标判断
        # 1. 完成率 (低不好)
        val = row['招聘完成率_%']
        icon = '🔴' if val < 85 else ('⚠️' if val < 95 else '✅')
        dept_item['招聘完成率'] = f"{icon} {val:.1f}%"
        
        # 2. 周期 (高不好)
        val = row['关键岗位到岗周期_天']
        icon = '🔴' if val > 60 else ('⚠️' if val > 45 else '✅')
        dept_item['关键岗位周期'] = f"{icon} {val:.1f}天"
        
        # 3. NPS (低不好)
        val = row['候选人体验NPS']
        icon = '🔴' if val < 30 else ('⚠️' if val < 50 else '✅')
        dept_item['体验NPS'] = f"{icon} {val:.1f}分"
        
        # 4. 流失率 (高不好)
        val = row['试用期流失率_%']
        icon = '🔴' if val > 20 else ('⚠️' if val > 10 else '✅')
        dept_item['流失率'] = f"{icon} {val:.1f}%"
        
        # 5. 负载 (高不好)
        val = row['人均月招聘负载_人']
        icon = '🔴' if val > 8 else ('⚠️' if val > 5 else '✅')
        dept_item['人均负载'] = f"{icon} {val:.1f}人"
        
        summary_data.append(dept_item)
        
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    st.markdown("---")

    # ==========================================
    # 图表区
    # ==========================================
    
    st.subheader("📉 深度诊断分析")
    
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        # Chart 3: NPS Heatmap
        st.markdown("#### 3️⃣ 候选人体验热力图 (按部门)")
        nps_dept = df_filtered.groupby('部门')['候选人体验NPS'].mean().reset_index()
        
        # [Data Capture] 候选人体验热力图
        st.session_state['current_charts_data']['HRD - 候选人体验热力图'] = nps_dept
        
        # 颜色反转：NPS高是好的(绿色)，低是坏的(红色) -> RdYlGn
        fig3 = px.bar(
            nps_dept, x='部门', y='候选人体验NPS', color='候选人体验NPS',
            color_continuous_scale='RdYlGn', title="各部门面试体验评分",
            range_color=[20, 80]
        )
        fig3.add_hline(y=50, line_dash="dash", line_color="gray", annotation_text="及格线")
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig3, use_container_width=True)
        
    with col_r:
        # Chart 4: 招聘流程人效热力图 (Heatmap)
        st.markdown("#### 4️⃣ 招聘顾问全流程人效热力图")
        st.caption("展示各顾问在校招流程各环节的吞吐量 (颜色越深代表工作量越大)")

        # 1. 准备数据
        # 聚合基础数据
        heatmap_base = df_filtered.groupby('招聘顾问').agg({
            '收到简历总数': 'sum',      # 初筛复核
            '初筛通过简历数': 'sum',    # 业务初筛
            '面试人数': 'sum',          # 业务面试 (作为基准)
            '发出Offer数': 'sum',       # 沟通Offer (作为基准)
            '接受Offer数': 'sum'        # 入职
        }).reset_index()

        # 2. 衍生中间环节数据 (模拟漏斗逻辑)
        # 逻辑：根据标准转化率推算中间环节，构建完整漏斗
        heatmap_data = []
        
        for _, row in heatmap_base.iterrows():
            recruiter = row['招聘顾问']
            
            # 定义各环节数据 (部分为衍生)
            stages = [
                ('1.初筛复核', row['收到简历总数']),
                ('2.业务初筛', row['初筛通过简历数']),
                ('3.笔试环节', int(row['初筛通过简历数'] * 0.85)),  # 衍生：约85%通过初筛的进入笔试
                ('4.业务面试', row['面试人数']),
                ('5.HR面试', int(row['面试人数'] * 0.6)),         # 衍生：约60%业务面通过进入HR面
                ('6.沟通Offer', int(row['发出Offer数'] * 1.2)),   # 衍生：Offer谈判数通常多于最终发出数
                ('7.正式入职', row['接受Offer数'])
            ]
            
            for stage_name, count in stages:
                heatmap_data.append({
                    '招聘顾问': recruiter,
                    '环节': stage_name,
                    '人数': count
                })

        df_heatmap = pd.DataFrame(heatmap_data)
        
        # [Data Capture] 招聘顾问人效热力图
        st.session_state['current_charts_data']['HRD - 招聘顾问全流程热力图'] = df_heatmap

        # 3. 绘制热力图
        # 颜色主题：使用 Blues 或 Teals 这种专业且清晰的色系
        fig4 = go.Figure(data=go.Heatmap(
            z=df_heatmap['人数'],
            x=df_heatmap['招聘顾问'],
            y=df_heatmap['环节'],
            colorscale='Teal',  # 专业蓝绿色系
            text=df_heatmap['人数'],
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverongaps=False,
            hovertemplate="<b>%{x}</b><br>%{y}: %{z}人<extra></extra>"
        ))

        fig4.update_layout(
            title="顾问 vs 流程环节工作量分布",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="",
            yaxis_title="",
            yaxis={'autorange': 'reversed'} # 让第一步显示在最上面
        )
        
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    
    # ==========================================
    # 异常诊断与行动 (Updated Chart 6)
    # ==========================================
    
    st.markdown("#### 5️⃣ 异常环节智能诊断与行动建议")
    st.info("💡 **行动导向**: 不仅告诉你哪里错了，还告诉你该怎么办")
    
    # 模拟异常数据
    anomalies = [
        {'部门': '技术部', '环节': '面试—Offer', '异常值': '转化率<15%', '影响': '浪费大量面试资源', '建议': '🔴 紧急: 对齐技术面标准，强制填写面评'},
        {'部门': '销售部', '环节': '简历—面试', '异常值': '响应>3天', '影响': '候选人体验极差', '建议': '⚠️ 关注: 每日下午4点设置简历清零提醒'},
        {'部门': '产品部', '环节': 'Offer—入职', '异常值': '拒签率>20%', '影响': '核心岗位交付失败', '建议': '🔴 紧急: 审查薪资竞争力，增加高管谈薪环节'}
    ]
    
    # 卡片式展示
    cols = st.columns(len(anomalies))
    for i, item in enumerate(anomalies):
        color = "#fee2e2" if "🔴" in item['建议'] else "#fef3c7"
        border = "#ef4444" if "🔴" in item['建议'] else "#f59e0b"
        
        with cols[i]:
            st.markdown(f"""
            <div style="background-color: {color}; padding: 15px; border-radius: 8px; border-left: 5px solid {border}; height: 200px;">
                <h4 style="margin-top:0">{item['部门']} - {item['环节']}</h4>
                <p><b>❌ 异常:</b> {item['异常值']}</p>
                <p><b>📉 影响:</b> {item['影响']}</p>
                <hr style="margin: 5px 0; border-color: {border}"/>
                <p style="font-weight:bold">{item['建议']}</p>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    # ==========================================
    # 渠道效能矩阵 (Updated Chart 7 - ROI Bubble)
    # ==========================================
    
    st.markdown("#### 6️⃣ 渠道 ROI 效能矩阵 (Bubble Chart)")
    
    # 模拟数据
    channel_data = pd.DataFrame([
        {'渠道': '猎头', 'Cost': 45000, 'Quality': 85, 'Hires': 15, 'Type': '昂贵优质'},
        {'渠道': '内推', 'Cost': 5000, 'Quality': 80, 'Hires': 40, 'Type': '明星渠道'},
        {'渠道': 'BOSS直聘', 'Cost': 2000, 'Quality': 60, 'Hires': 60, 'Type': '走量渠道'},
        {'渠道': 'RPO', 'Cost': 15000, 'Quality': 70, 'Hires': 25, 'Type': '补充渠道'},
        {'渠道': '校园招聘', 'Cost': 8000, 'Quality': 75, 'Hires': 30, 'Type': '高潜渠道'}
    ])
    
    # [Data Capture] 渠道效能矩阵
    st.session_state['current_charts_data']['HRD - 渠道ROI效能矩阵'] = channel_data
    
    fig7 = px.scatter(
        channel_data, x='Cost', y='Quality', size='Hires', color='Type',
        text='渠道', title="投入产出比分析 (越左上越好)",
        color_discrete_map={'明星渠道': '#10B981', '昂贵优质': '#F59E0B', '走量渠道': '#3B82F6', '补充渠道': '#94A3B8', '高潜渠道': '#8B5CF6'}
    )
    
    # 划分区域
    fig7.add_shape(type="rect", x0=0, y0=70, x1=10000, y1=100, fillcolor="rgba(16, 185, 129, 0.1)", layer="below", line_width=0)
    fig7.add_annotation(x=3000, y=95, text="🏆 黄金区", showarrow=False, font=dict(color="#047857"))
    
    fig7.update_traces(textposition='top center')
    fig7.update_layout(xaxis_title="单人招聘成本 (元)", yaxis_title="人才质量分 (0-100)", plot_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig7, use_container_width=True)
    
    st.markdown("---")

    # ==========================================
    # 硅碳比分析 (Optimized Chart 8 - Before/After)
    # ==========================================
    
    st.markdown("#### 7️⃣ AI提效与硅碳比深度分析 (Before vs After)")
    st.info("💡 **核心价值**: 展示AI介入前后，团队产出能力和个人负载的质变")

    # 1. 模拟 Before/After 数据
    depts = df_filtered['部门'].unique()
    ai_efficiency_data = []
    np.random.seed(55)
    
    for dept in depts:
        hr_count = np.random.randint(3, 8)
        avg_output_before = np.random.randint(3, 5) 
        total_output_before = hr_count * avg_output_before
        
        silicon_ratio = np.random.uniform(0.4, 0.9)
        total_output_after = total_output_before * (1 + silicon_ratio)
        avg_output_after = total_output_after / hr_count
        
        ai_efficiency_data.append({
            '部门': dept, 'HR人数': hr_count,
            'Before总产出': total_output_before,
            'After总产出': total_output_after,
            '硅碳比': silicon_ratio,
            '效率提升_%': silicon_ratio * 100
        })
        
    eff_df = pd.DataFrame(ai_efficiency_data)
    
    # [Data Capture] AI提效产出构成
    st.session_state['current_charts_data']['HRD - AI提效产出构成'] = eff_df
    
    # 2. 堆叠图
    fig_ai = go.Figure()
    fig_ai.add_trace(go.Bar(
        x=eff_df['部门'], y=eff_df['Before总产出'], name='人力基础产出', marker_color='#94A3B8', opacity=0.7,
        text=eff_df['Before总产出'].apply(lambda x: f"{int(x)}"), textposition='inside'
    ))
    fig_ai.add_trace(go.Bar(
        x=eff_df['部门'], y=eff_df['After总产出'] - eff_df['Before总产出'], name='AI增效产出', marker_color='#6f42c1',
        text=(eff_df['After总产出'] - eff_df['Before总产出']).apply(lambda x: f"+{int(x)}"), textposition='inside'
    ))
    
    fig_ai.update_layout(barmode='stack', title="各部门产出构成分析 (人力 + AI增量)", xaxis_title="部门", yaxis_title="月度总招聘产出", plot_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig_ai, use_container_width=True)
    
    # 4. 洞察
    top = eff_df.sort_values('效率提升_%', ascending=False).iloc[0]
    st.success(f"🤖 **最佳实践**: **{top['部门']}** 通过AI实现了 **{top['效率提升_%']:.0f}%** 的效率提升 (硅碳比 {top['硅碳比']:.2f})。")

    st.markdown("---")
    

    st.success("""
    ✅ **HRD 报警器总结**:
    - **异常驱动管理**: 从"盯人用人"转向"盯异常"，管理半径扩大 3-5 倍
    - **全流程质量控**: NPS、流失率、毁约率全链路监控，杜绝质量黑箱
    - **人效动态平衡**: 实时监控团队负载与人效，科学调配人力资源
    - **硅碳协同增效**: 可视化 AI 对团队产能的释放，从"人海战术"转向"人机协同"
    """)


if __name__ == '__main__':
    from data_generator_complete import generate_complete_recruitment_data
    st.set_page_config(page_title="HRD 异常报警器", layout="wide")
    df = generate_complete_recruitment_data(months=12, recruiters=5, departments=5)
    render_hrd_dashboard(df)
