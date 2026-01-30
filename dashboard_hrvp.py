"""
HRVP 战略驾驶舱 v3.2 Pro (Strategic Depth & Data Simulation)
核心理念：从"成本中心"转向"利润中心"，用ROI衡量招聘价值
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
# HRVP 核心指标定义 (ROI 导向)
# ==========================================

HRVP_CORE_METRICS = {
    '招聘投资回报率_ROI': {
        'name': '招聘投资回报率 (ROI)',
        'name_en': 'Recruitment ROI',
        'category': '战略价值',
        'unit': 'x',
        'formula': '(新员工创造营收增量 - 招聘总成本) / 招聘总成本',
        'definition': '每投入1元招聘成本，为公司带来了多少倍的业务增值',
        'boss_comment': '这才是赚钱的逻辑！我要看招聘团队是不是在帮我做高杠杆的投资',
        'benchmark': {
            '优秀': '> 5.0x',
            '良好': '3.0x - 5.0x',
            '需改进': '< 3.0x'
        },
        'target': 5.0,
        'review_cadence': 'Quarterly',
        'impact': '直接证明招聘部门是利润中心而非成本中心'
    },

    '关键岗位填补及时率_%': {
        'name': '关键战略岗位填补及时率',
        'name_en': 'Critical Role On-Time Fill Rate',
        'category': '战略交付',
        'unit': '%',
        'formula': '按时到岗的关键岗位数 / 计划招聘关键岗位总数',
        'definition': 'P8及以上/核心技术/新业务负责人的到岗及时性',
        'boss_comment': '那个领军人物不到位，整个业务线都得停摆，这个指标必须盯着',
        'benchmark': {
            '优秀': '>90%',
            '良好': '80-90%',
            '需改进': '<80%'
        },
        'target': 90.0,
        'review_cadence': 'Monthly',
        'impact': '保障公司核心战略如期落地'
    },

    '人均产出贡献比_Ratio': {
        'name': '新员工人均产出贡献比',
        'name_en': 'Revenue per New Hire Ratio',
        'category': '人才效能',
        'unit': 'x',
        'formula': '新员工人均营收 / 人均招聘成本',
        'definition': '衡量人才引进后的产出效能',
        'boss_comment': '招来的人能不能打？用数据说话',
        'benchmark': {
            '优秀': '> 8.0',
            '良好': '5.0-8.0',
            '需改进': '< 5.0'
        },
        'target': 8.0,
        'review_cadence': 'Quarterly',
        'impact': '评估人才质量与业务匹配度'
    },

    '高绩效员工占比_%': {
        'name': '高绩效员工占比 (S/A级)',
        'name_en': 'High Performer Rate',
        'category': '人才质量',
        'unit': '%',
        'formula': '绩效评估为S/A级的新员工 / 总转正人数',
        'definition': '入职一年内绩效表现优异的比例',
        'boss_comment': '我要的是精兵强将，不是人海战术',
        'benchmark': {
            '优秀': '>30%',
            '良好': '20-30%',
            '需改进': '<20%'
        },
        'target': 30.0,
        'review_cadence': 'Quarterly',
        'impact': '决定组织的人才密度'
    },
    
    '招聘成本占营收比_%': {
        'name': '招聘成本占营收比',
        'name_en': 'Recruitment Cost / Revenue',
        'category': '成本效率',
        'unit': '%',
        'formula': '招聘总成本 / 公司总营收',
        'definition': '衡量招聘投入在整体业务盘子中的占比',
        'boss_comment': '花小钱办大事，AI应该帮我们把这个比例降下来',
        'benchmark': {
            '优秀': '< 1.0%',
            '良好': '1.0-2.0%',
            '需改进': '> 2.0%'
        },
        'target': 1.0,
        'review_cadence': 'Annual',
        'impact': '展示AI提效对财务报表的直接贡献'
    }
}


# ==========================================
# HRVP 看板渲染函数
# ==========================================

def render_hrvp_dashboard(df):
    """
    渲染 HRVP 战略驾驶舱 v3.2
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
        <h1 style="color: white; margin: 0; font-size: 2rem;">📊 HRVP 战略驾驶舱 (ROI & Talent Strategy)</h1>
        <p style="color: white; opacity: 0.95; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Strategic Command Center - 关注投资回报、战略交付与核心人才库
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 数据增强与模拟
    # ==========================================
    df_filtered = df.copy()
    np.random.seed(88)
    
    # 1. 模拟 ROI 数据
    if 'ROI' not in df_filtered.columns:
        def get_simulated_roi(row):
            dept = row['部门']
            base_roi = 3.0
            if dept == '销售部': base_roi = 6.5
            elif dept == '技术部': base_roi = 5.0
            elif dept == '产品部': base_roi = 4.5
            elif dept == '运营部': base_roi = 3.5
            return max(1.0, base_roi + np.random.normal(0, 0.8))
        df_filtered['招聘投资回报率_ROI'] = df_filtered.apply(get_simulated_roi, axis=1)

    # 2. 模拟 关键岗位 及其 职级
    if '岗位职级' not in df_filtered.columns:
        levels = ['P9+', 'P8', 'P7', 'P6-', 'VP']
        probs = [0.05, 0.15, 0.3, 0.45, 0.05]
        df_filtered['岗位职级'] = np.random.choice(levels, len(df_filtered), p=probs)
        
    df_filtered['是否关键岗位'] = df_filtered['岗位职级'].isin(['VP', 'P9+', 'P8'])
    
    # 3. 模拟 到岗周期 (确保完全没有空值)
    if '到岗周期_天' not in df_filtered.columns:
         df_filtered['到岗周期_天'] = np.random.randint(20, 100, size=len(df_filtered))
    
    # ==========================================
    # 核心KPI卡片
    # ==========================================

    st.subheader("🎯 核心战略指标")
    kpi_cols = st.columns(5)
    
    # 1. 招聘 ROI
    with kpi_cols[0]:
        metric_key = '招聘投资回报率_ROI'
        info = HRVP_CORE_METRICS[metric_key]
        val = df_filtered[metric_key].mean()
        render_metric_flip_card(metric_key, info, val, info['target'], 'HRVP', 
            raw_data_dict={'平均ROI': f"{val:.1f}x", '对标值': '5.0x'})
            
    # 2. 关键岗位填补及时率
    with kpi_cols[1]:
        metric_key = '关键岗位填补及时率_%'
        info = HRVP_CORE_METRICS[metric_key]
        critical_jobs = df_filtered[df_filtered['是否关键岗位']]
        on_time_count = len(critical_jobs[critical_jobs['到岗周期_天'] < 45])
        total_critical = len(critical_jobs)
        val = (on_time_count / total_critical * 100) if total_critical > 0 else 0
        render_metric_flip_card(metric_key, info, val, info['target'], 'HRVP',
             raw_data_dict={'按时到岗': on_time_count, '关键岗位总数': total_critical})

    # 3. 人均产出贡献比
    with kpi_cols[2]:
        metric_key = '人均产出贡献比_Ratio'
        info = HRVP_CORE_METRICS[metric_key]
        val = 7.2 
        render_metric_flip_card(metric_key, info, val, info['target'], 'HRVP',
            raw_data_dict={'人均营收贡献': '￥85万', '人均招聘成本': '￥1.2万'})

    # 4. 高绩效员工占比
    with kpi_cols[3]:
        metric_key = '高绩效员工占比_%'
        info = HRVP_CORE_METRICS[metric_key]
        val = df_filtered[metric_key].mean()
        render_metric_flip_card(metric_key, info, val, info['target'], 'HRVP',
            raw_data_dict={'S/A级员工': int(len(df_filtered)*val/100), '总人数': len(df_filtered)})

    # 5. 招聘成本占营收比
    with kpi_cols[4]:
        metric_key = '招聘成本占营收比_%'
        info = HRVP_CORE_METRICS[metric_key]
        val = 1.3
        render_metric_flip_card(metric_key, info, val, info['target'], 'HRVP',
             raw_data_dict={'招聘总投入': '￥500万', '公司总营收': '￥3.8亿'})

    st.markdown("---")

    # ==========================================
    # 图表 1: 关键岗位交付风险分析 (Deep Dive)
    # ==========================================
    
    st.subheader("1️⃣ 按职级拆解：关键战略岗位交付趋势")
    
    # 专门构造一个稳健的数据集用于绘图，避免依赖原始数据分布不均
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    levels = ['VP', 'P9+', 'P8']
    
    # 模拟交付率趋势：VP很难，P9+一般，P8较好
    trend_data = []
    
    for m_idx, m in enumerate(months):
        for lvl in levels:
            base_rate = 0.85 # P8
            if lvl == 'P9+': base_rate = 0.75
            if lvl == 'VP': base_rate = 0.55
            
            # 添加随机波动和上升趋势（假设在改进）
            rate = min(1.0, base_rate + (m_idx * 0.01) + np.random.uniform(-0.05, 0.05))
            
            trend_data.append({
                '月份': m,
                '职级': lvl,
                '按时交付率': rate * 100
            })
            
    trend_df = pd.DataFrame(trend_data)
    
    # [Data Capture] 关键岗位交付趋势
    st.session_state['current_charts_data']['HRVP - 关键岗位交付趋势'] = trend_df
    
    fig1 = px.line(
        trend_df,
        x='月份',
        y='按时交付率',
        color='职级',
        markers=True,
        symbol='职级',
        color_discrete_map={
            'VP': '#EF4444',     # Red 
            'P9+': '#F59E0B',    # Orange
            'P8': '#3B82F6'      # Blue
        }
    )
    
    fig1.update_layout(
        title="不同职级关键岗位按时交付率趋势",
        yaxis_title="按时交付率 (%)",
        yaxis_range=[40, 105],
        font=dict(family=font),
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified"
    )
    
    # 添加目标线
    fig1.add_hline(y=90, line_dash="dash", line_color="green", annotation_text="目标 90%")
    fig1.add_hline(y=60, line_dash="dot", line_color="red", annotation_text="危机线 60%")
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 洞察
    vp_current = trend_df[trend_df['职级']=='VP'].iloc[-1]['按时交付率']
    
    st.markdown(f"""
    **📊 风险诊断**:
    - **VP级岗位** 始终在红色危机线附近徘徊 (当前 {vp_current:.1f}%)，说明公司核心高管引进面临系统性困难。
    - **P8级岗位** 表现稳定在85%以上，说明腰部力量供给充足。
    - **行动建议**: 建议 HRVP 亲自介入 VP 级候选人的 **"前期通过率"** 管理，并提高猎头费率上限以获取更优质的定向寻访服务。
    """)

    st.markdown("---")

    # ==========================================
    # 图表 2: ROI 全景分析 (渠道 ROI + 趋势)
    # ==========================================
    
    st.subheader("2️⃣ 招聘投资回报率 (ROI) 深度分析")
    st.markdown(" **公式**: $ROI = \\frac{\\text{新员工首年营收贡献} - \\text{招聘全成本}}{\\text{招聘全成本}} \\times 100\\%$")
    
    col_roi1, col_roi2 = st.columns([1, 1])
    
    with col_roi1:
        st.markdown("#### 🅰️ 分渠道 ROI 效能对比")
        # 构造各渠道 ROI 数据
        # 猎头: 成本高, 质量高 -> ROI 中
        # 内推: 成本低, 质量高 -> ROI 极高
        # AI自招: 成本极低, 质量中 -> ROI 极高 (新星)
        # 招聘网站: 成本低, 质量低 -> ROI 低
        
        channel_roi_data = [
            {'渠道': 'AI智能自招', 'ROI': 12.5, 'Cost': 1500, 'Quality': '中高', 'Type': 'High ROI'},
            {'渠道': '员工内推', 'ROI': 8.2, 'Cost': 5000, 'Quality': '高', 'Type': 'High ROI'},
            {'渠道': '猎头/RPO', 'ROI': 3.1, 'Cost': 45000, 'Quality': '高', 'Type': 'Medium ROI'},
            {'渠道': '传统招聘网站', 'ROI': 1.8, 'Cost': 3000, 'Quality': '低', 'Type': 'Low ROI'},
            {'渠道': '校园招聘', 'ROI': 4.5, 'Cost': 8000, 'Quality': '中', 'Type': 'Medium ROI'}
        ]
        ch_roi_df = pd.DataFrame(channel_roi_data)
        
        # [Data Capture] 分渠道 ROI
        st.session_state['current_charts_data']['HRVP - 分渠道ROI效能'] = ch_roi_df
        
        fig_ch = px.bar(
            ch_roi_df.sort_values('ROI', ascending=True),
            x='ROI',
            y='渠道',
            orientation='h',
            color='Type',
            text='ROI',
            color_discrete_map={
                'High ROI': '#10B981',
                'Medium ROI': '#3B82F6',
                'Low ROI': '#EF4444'
            }
        )
        fig_ch.update_traces(texttemplate='%{text}x', textposition='outside')
        fig_ch.update_layout(title="各渠道 ROI 倍数排名", xaxis_title="ROI (倍数)", plot_bgcolor='rgba(0,0,0,0)', showlegend=True)
        st.plotly_chart(fig_ch, use_container_width=True)
        
    with col_roi2:
         st.markdown("#### 🅱️ ROI 年度增长趋势 (AI驱动)")
         # 趋势数据
         roi_trend_data = [
             {'Month': 'Q1', 'ROI': 3.2, 'Phase': 'Before AI'},
             {'Month': 'Q2', 'ROI': 3.5, 'Phase': 'Before AI'},
             {'Month': 'Q3', 'ROI': 4.8, 'Phase': 'After AI'},
             {'Month': 'Q4', 'ROI': 5.5, 'Phase': 'After AI'}
         ]
         rt_df = pd.DataFrame(roi_trend_data)
         
         # [Data Capture] ROI 年度趋势
         st.session_state['current_charts_data']['HRVP - ROI年度趋势'] = rt_df
         
         fig_rt = px.line(rt_df, x='Month', y='ROI', markers=True, text='ROI')
         fig_rt.add_shape(type="rect", x0=1.5, y0=0, x1=4, y1=6, fillcolor="rgba(16, 185, 129, 0.1)", layer="below", line_width=0)
         fig_rt.add_annotation(x='Q3', y=5, text="AI 战略生效", showarrow=True, arrowhead=1)
         
         fig_rt.update_traces(line_color='#6366F1', line_width=4, marker_size=12, texttemplate='%{text}x', textposition='top center')
         fig_rt.update_layout(title="季度 ROI 跃升趋势", yaxis_title="ROI (倍数)", yaxis_range=[2, 7], plot_bgcolor='rgba(0,0,0,0)')
         st.plotly_chart(fig_rt, use_container_width=True)
         
    # 洞察
    st.success("""
    **💰 投资决策建议**:
    1.  **AI智能自招 (ROI 12.5x)**: 成本边际效应为零，是 ROI 之王。建议明年将 **50% 的社招预算** 转移到 AI 渠道建设。
    2.  **猎头 (ROI 3.1x)**: 虽然绝对质量高，但成本过高拉低了 ROI。建议仅保留 VP 级以上的猎头预算，P8及以下全部通过 AI+内推 解决。
    """)
    
    st.markdown("---")
    
    # ==========================================
    # 图表 3: 成本-质量矩阵 (Better Scatter)
    # ==========================================
    st.subheader("3️⃣ 成本与质量平衡矩阵 (四象限分析)")
    
    # 构造更分散的数据
    matrix_data = pd.DataFrame([
        {'部门': '销售部', 'Cost': 8500, 'HighPerf': 82, 'Size': 50, 'Type': 'Star'},
        {'部门': '技术部', 'Cost': 16000, 'HighPerf': 88, 'Size': 30, 'Type': 'Premium'},
        {'部门': '产品部', 'Cost': 13000, 'HighPerf': 76, 'Size': 20, 'Type': 'Premium'},
        {'部门': '职能部', 'Cost': 4500, 'HighPerf': 55, 'Size': 15, 'Type': 'Basic'},
        {'部门': '运营部', 'Cost': 7500, 'HighPerf': 68, 'Size': 40, 'Type': 'Efficient'}
    ])
            
    # [Data Capture] 成本质量矩阵
    st.session_state['current_charts_data']['HRVP - 成本质量矩阵'] = matrix_data

    fig2 = px.scatter(
        matrix_data,
        x='Cost',
        y='HighPerf',
        size='Size',
        color='部门',
        text='部门',
        title="成本(X) vs 质量(Y) 矩阵 (气泡大小=招聘规模)"
    )
    
    # 绘制象限背景
    mid_cost = 10000; mid_qual = 70
    
    # 四个区域背景
    fig2.add_shape(type="rect", x0=mid_cost, y0=mid_qual, x1=20000, y1=100, fillcolor="rgba(255, 193, 7, 0.1)", layer="below", line_width=0)
    fig2.add_annotation(x=15000, y=95, text="💎 明星区域", showarrow=False, font=dict(color="#B7791F"))
    
    fig2.add_shape(type="rect", x0=0, y0=mid_qual, x1=mid_cost, y1=100, fillcolor="rgba(16, 185, 129, 0.1)", layer="below", line_width=0)
    fig2.add_annotation(x=5000, y=95, text="🌟 卓越区域", showarrow=False, font=dict(color="#047857"))
    
    fig2.add_shape(type="rect", x0=mid_cost, y0=0, x1=20000, y1=mid_qual, fillcolor="rgba(239, 68, 68, 0.1)", layer="below", line_width=0)
    fig2.add_annotation(x=15000, y=40, text="⚠️ 警惕区域", showarrow=False, font=dict(color="#B91C1C"))
    
    fig2.add_shape(type="rect", x0=0, y0=0, x1=mid_cost, y1=mid_qual, fillcolor="rgba(59, 130, 246, 0.1)", layer="below", line_width=0)
    fig2.add_annotation(x=5000, y=40, text="⚖️ 经济区域", showarrow=False, font=dict(color="#1D4ED8"))

    fig2.add_vline(x=mid_cost, line_dash="dash", line_color="gray")
    fig2.add_hline(y=mid_qual, line_dash="dash", line_color="gray")
    
    fig2.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    fig2.update_layout(
        font=dict(family=font), height=500, plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[2000, 18000], title="单次招聘成本 (元)"),
        yaxis=dict(range=[30, 100], title="高绩效员工占比 (%)")
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")


    # ==========================================
    # 图表 4: AI 战略提效 (保留)
    # ==========================================
    st.subheader("4️⃣ AI 战略提效与边际成本分析 (Strategic AI Impact)")
    st.info("💡 **核心价值**: 展示企业如何通过AI实现“规模化增长”与“人力成本”的脱钩")

    # 复用之前好的逻辑，这里简化代码量展示
    # 模拟数据
    months_lb = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    base_head = 10; base_out = 5; hc_cost = 30000
    
    td = []
    for i, m in enumerate(months_lb):
        if i < 6: hc = base_head + int(i*0.5); out = hc * base_out; c = hc * hc_cost
        else: hc = 13; ai_m = 1.0 + (i-5)*0.4; out = hc * base_out * ai_m; c = hc * hc_cost + 2000
        td.append({'Month': m, 'Headcount': hc, 'Output': out, 'Cost': c, 'UnitCost': c/out})
    td_df = pd.DataFrame(td)
    
    # [Data Capture] AI战略提效
    st.session_state['current_charts_data']['HRVP - AI战略提效分析'] = td_df
    
    fig_dec = make_subplots(specs=[[{"secondary_y": True}]])
    fig_dec.add_trace(go.Scatter(x=td_df['Month'], y=td_df['Output'], name='总产出', fill='tozeroy', line=dict(color='#6366F1')), secondary_y=False)
    fig_dec.add_trace(go.Bar(x=td_df['Month'], y=td_df['Headcount'], name='人力', marker_color='rgba(148,163,184,0.5)', width=0.4), secondary_y=True)
    fig_dec.add_vline(x=5.5, line_dash="dash", line_color="green", annotation_text="AI 规模化")
    fig_dec.update_layout(title="产出飙升 vs 人力持平 (解绑效应)", height=400, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_dec, use_container_width=True)
    
    st.markdown("---")

    # ==========================================
    # 图表 5: 校招人才全周期质量 (New! Retention + Promotion)
    # ==========================================
    st.subheader("5️⃣ 校招人才储备: 留存与成长双维评估")
    st.info("💡 **战略视角**: 3年留存率 + 2年晋升率 = 未来核心人才库质量")
    
    # 模拟数据: 不同院校来源的 Cohort Analysis
    # C9: 留存低 (Flight Risk), 晋升快 (Fast Track)
    # 211: 留存高 (Loyal), 晋升稳 (Solid)
    # 海外: 留存低, 晋升快
    # 双非: 留存高, 晋升慢
    
    campus_cohort_data = pd.DataFrame([
        {
            'Source': 'C9联盟院校', 
            'Retention_3yr': 45.0, # 低
            'Promotion_2yr': 60.0, # 高
            'Size': 120,
            'Description': '高潜但不稳 (Flight Risk)'
        },
        {
            'Source': '海外QS50', 
            'Retention_3yr': 40.0, 
            'Promotion_2yr': 65.0, 
            'Size': 80,
            'Description': '精英流动性大'
        },
        {
            'Source': '211核心院校', 
            'Retention_3yr': 75.0, # 高
            'Promotion_2yr': 45.0, # 稳
            'Size': 200,
            'Description': '组织中坚力量 (Backbone)'
        },
        {
            'Source': '普通一本', 
            'Retention_3yr': 85.0, 
            'Promotion_2yr': 25.0, # 慢
            'Size': 150,
            'Description': '基石员工'
        }
    ])
    
    # [Data Capture] 校招人才质量
    st.session_state['current_charts_data']['HRVP - 校招人才质量评估'] = campus_cohort_data
    
    fig_camp = px.scatter(
        campus_cohort_data,
        x='Retention_3yr',
        y='Promotion_2yr',
        size='Size',
        color='Source',
        text='Description',
        title="主要校招来源质量分析 (2022-2023届)",
        color_discrete_sequence=['#F59E0B', '#6366F1', '#10B981', '#3B82F6']
    )
    
    # 划分区域
    # 右上: 核心人才库 (既稳又快)
    fig_camp.add_shape(type="rect", x0=60, y0=40, x1=100, y1=80, fillcolor="rgba(16, 185, 129, 0.1)", layer="below", line_width=0)
    fig_camp.add_annotation(x=70, y=70, text="🏆 核心人才库<br>(既稳又快)", showarrow=False, font=dict(color="#047857"))
    
    # 添加基准线
    fig_camp.update_layout(
        xaxis_title="3年留存率 (%)",
        yaxis_title="2年晋升率 (%)",
        font=dict(family=font),
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[30, 95]),
        yaxis=dict(range=[10, 80])
    )
    fig_camp.update_traces(textposition='top center')
    
    st.plotly_chart(fig_camp, use_container_width=True)
    
    st.success("""
    **🎓 校招战略决策**:
    - **C9/海外精英**: 晋升率极高但留存率低。建议: **实施 "Fast Track" 管培生计划**，用高挑战和快速回报锁定他们。
    - **211院校**: 留存好且晋升尚可，是公司的 **"中坚力量"**。建议: 将校招资源的 **60%** 倾斜向此类院校，作为从选到用的主力池。
    """)

    st.markdown("---")

    

    st.success("""
    ✅ **HRVP 驾驶舱总结**:
    - **ROI 导向决策**: 用数据证明招聘是高回报投资 (ROI > 5x)，而非单纯的成本中心
    - **战略交付透明**: 关键岗位交付风险一目了然，不再被动等待
    - **成本价值对齐**: 清晰展示每一分钱花在了刀刃上 (高绩效人才)
    - **AI 战略落地**: 量化 AI 对人效和边际成本的颠覆性改善
    """)

if __name__ == '__main__':
    from data_generator_complete import generate_complete_recruitment_data
    st.set_page_config(page_title="HRVP 战略驾驶舱", layout="wide")
    df = generate_complete_recruitment_data(months=12, recruiters=5, departments=5)
    render_hrvp_dashboard(df)
