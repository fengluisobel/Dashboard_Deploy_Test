import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json

# 页面配置
st.set_page_config(
    page_title="人力资源招聘指标驾驶舱",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 30px;
        margin-bottom: 15px;
        border-left: 5px solid #3498db;
        padding-left: 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# 生成模拟数据
@st.cache_data
def generate_mock_data():
    """生成模拟招聘数据"""
    np.random.seed(42)

    # 时间维度：最近12个月
    months = pd.date_range(start='2025-01-01', end='2025-12-31', freq='MS')

    # 人员维度
    recruiters = ['张伟', '李娜', '王芳', '刘洋', '陈静']
    departments = ['技术部', '产品部', '市场部', '销售部', '运营部']
    positions = ['初级', '中级', '高级', '专家', '管理层']
    channels = ['招聘网站', '猎头', '内推', '校园招聘', '社交媒体']

    data = {
        '月份': [],
        '招聘顾问': [],
        '部门': [],
        '职级': [],
        '渠道': [],

        # 1. 招聘速度与效率
        '平均招聘周期_天': [],
        '审批耗时_天': [],
        '寻访耗时_天': [],
        '平均录用速度_天': [],
        '流程停滞天数': [],
        '面试反馈速度_小时': [],
        '招聘及时率_%': [],
        '逾期职位数': [],
        '职位老化率_%': [],
        '重启职位数': [],

        # 2. 招聘质量与结果
        '试用期转正率_%': [],
        '试用期延长率_%': [],
        '新员工首年绩效_分': [],
        '绩效校准差异_分': [],
        '新员工早期离职率_%': [],
        '首月流失率_%': [],
        '用人经理满意度_分': [],
        '简历质量满意度_分': [],
        '关键岗位达成率_%': [],
        '核心岗空窗期_天': [],

        # 3. 漏斗与转化
        '录用接受率_%': [],
        '简历初筛通过率_%': [],
        '面试通过率_%': [],
        '渠道简历转化率_%': [],
        '候选人库覆盖率': [],
        '人才地图完备度_%': [],

        # 4. 成本与生产力
        '单次招聘成本_元': [],
        '猎头费用占比_%': [],
        '渠道单价_元': [],
        '招聘顾问人效_人': [],
        '人均负责职位数': [],
        '招聘预算执行率_%': [],
        '平均定薪涨幅_%': [],

        # 5. 体验与品牌
        '候选人NPS': [],
        '面试官专业度评分': [],
        '申请完成率_%': [],
        '移动端申请占比_%': [],
        '幽灵率_%': [],
        '面试爽约率_%': [],
        '雇主品牌触达_PV': [],
        '职位点击申请率_%': [],
        '多元化候选人占比_%': [],
        'Offer多元化率_%': [],

        # 额外维度
        '招聘人数': [],
        '发出Offer数': [],
        '接受Offer数': [],
    }

    for month in months:
        for recruiter in recruiters:
            for dept in departments[:3]:  # 限制数据量
                row_data = {
                    '月份': month,
                    '招聘顾问': recruiter,
                    '部门': dept,
                    '职级': np.random.choice(positions),
                    '渠道': np.random.choice(channels),

                    # 1. 招聘速度与效率
                    '平均招聘周期_天': np.random.randint(20, 60),
                    '审批耗时_天': np.random.randint(3, 10),
                    '寻访耗时_天': np.random.randint(5, 20),
                    '平均录用速度_天': np.random.randint(15, 45),
                    '流程停滞天数': np.random.randint(0, 5),
                    '面试反馈速度_小时': np.random.randint(12, 72),
                    '招聘及时率_%': np.random.uniform(70, 95),
                    '逾期职位数': np.random.randint(0, 5),
                    '职位老化率_%': np.random.uniform(5, 25),
                    '重启职位数': np.random.randint(0, 3),

                    # 2. 招聘质量与结果
                    '试用期转正率_%': np.random.uniform(80, 98),
                    '试用期延长率_%': np.random.uniform(2, 15),
                    '新员工首年绩效_分': np.random.uniform(3.5, 4.8),
                    '绩效校准差异_分': np.random.uniform(0.1, 0.8),
                    '新员工早期离职率_%': np.random.uniform(5, 20),
                    '首月流失率_%': np.random.uniform(1, 8),
                    '用人经理满意度_分': np.random.uniform(3.5, 5.0),
                    '简历质量满意度_分': np.random.uniform(3.0, 5.0),
                    '关键岗位达成率_%': np.random.uniform(70, 100),
                    '核心岗空窗期_天': np.random.randint(10, 60),

                    # 3. 漏斗与转化
                    '录用接受率_%': np.random.uniform(60, 90),
                    '简历初筛通过率_%': np.random.uniform(15, 40),
                    '面试通过率_%': np.random.uniform(25, 60),
                    '渠道简历转化率_%': np.random.uniform(10, 35),
                    '候选人库覆盖率': np.random.uniform(1.5, 4.0),
                    '人才地图完备度_%': np.random.uniform(50, 90),

                    # 4. 成本与生产力
                    '单次招聘成本_元': np.random.randint(3000, 15000),
                    '猎头费用占比_%': np.random.uniform(20, 50),
                    '渠道单价_元': np.random.randint(100, 800),
                    '招聘顾问人效_人': np.random.randint(3, 12),
                    '人均负责职位数': np.random.randint(5, 15),
                    '招聘预算执行率_%': np.random.uniform(70, 105),
                    '平均定薪涨幅_%': np.random.uniform(10, 30),

                    # 5. 体验与品牌
                    '候选人NPS': np.random.randint(-20, 60),
                    '面试官专业度评分': np.random.uniform(3.5, 5.0),
                    '申请完成率_%': np.random.uniform(60, 90),
                    '移动端申请占比_%': np.random.uniform(30, 70),
                    '幽灵率_%': np.random.uniform(5, 25),
                    '面试爽约率_%': np.random.uniform(3, 18),
                    '雇主品牌触达_PV': np.random.randint(5000, 50000),
                    '职位点击申请率_%': np.random.uniform(15, 45),
                    '多元化候选人占比_%': np.random.uniform(25, 55),
                    'Offer多元化率_%': np.random.uniform(20, 50),

                    # 额外维度
                    '招聘人数': np.random.randint(2, 15),
                    '发出Offer数': np.random.randint(3, 20),
                    '接受Offer数': np.random.randint(2, 18),
                }

                for key, value in row_data.items():
                    data[key].append(value)

    df = pd.DataFrame(data)
    return df

# 加载数据
df = generate_mock_data()

# 侧边栏筛选器
st.sidebar.markdown("## 🔍 数据筛选")

# 时间范围筛选
min_date = df['月份'].min().date()
max_date = df['月份'].max().date()
date_range = st.sidebar.date_input(
    "选择时间范围",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# 招聘顾问筛选
selected_recruiters = st.sidebar.multiselect(
    "招聘顾问",
    options=df['招聘顾问'].unique().tolist(),
    default=df['招聘顾问'].unique().tolist()
)

# 部门筛选
selected_departments = st.sidebar.multiselect(
    "部门",
    options=df['部门'].unique().tolist(),
    default=df['部门'].unique().tolist()
)

# 职级筛选
selected_levels = st.sidebar.multiselect(
    "职级",
    options=df['职级'].unique().tolist(),
    default=df['职级'].unique().tolist()
)

# 渠道筛选
selected_channels = st.sidebar.multiselect(
    "招聘渠道",
    options=df['渠道'].unique().tolist(),
    default=df['渠道'].unique().tolist()
)

# 应用筛选
if len(date_range) == 2:
    filtered_df = df[
        (df['月份'].dt.date >= date_range[0]) &
        (df['月份'].dt.date <= date_range[1]) &
        (df['招聘顾问'].isin(selected_recruiters)) &
        (df['部门'].isin(selected_departments)) &
        (df['职级'].isin(selected_levels)) &
        (df['渠道'].isin(selected_channels))
    ]
else:
    filtered_df = df[
        (df['招聘顾问'].isin(selected_recruiters)) &
        (df['部门'].isin(selected_departments)) &
        (df['职级'].isin(selected_levels)) &
        (df['渠道'].isin(selected_channels))
    ]

# 主标题
st.markdown('<h1 class="main-header">🎯 人力资源招聘指标驾驶舱</h1>', unsafe_allow_html=True)

# 总览KPI
st.markdown('<h2 class="sub-header">📈 核心KPI总览</h2>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    avg_time_to_fill = filtered_df['平均招聘周期_天'].mean()
    st.metric("平均招聘周期", f"{avg_time_to_fill:.1f}天", f"{-5:.1f}天")

with col2:
    probation_pass_rate = filtered_df['试用期转正率_%'].mean()
    st.metric("试用期转正率", f"{probation_pass_rate:.1f}%", f"{2.5:.1f}%")

with col3:
    offer_acceptance = filtered_df['录用接受率_%'].mean()
    st.metric("录用接受率", f"{offer_acceptance:.1f}%", f"{3.2:.1f}%")

with col4:
    cost_per_hire = filtered_df['单次招聘成本_元'].mean()
    st.metric("单次招聘成本", f"¥{cost_per_hire:.0f}", f"-¥{500:.0f}")

with col5:
    candidate_nps = filtered_df['候选人NPS'].mean()
    st.metric("候选人NPS", f"{candidate_nps:.1f}", f"{5.3:.1f}")

st.markdown("---")

# Tab布局
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 招聘速度与效率",
    "🎯 招聘质量与结果",
    "🔄 漏斗与转化",
    "💰 成本与生产力",
    "⭐ 体验与品牌",
    "📋 详细数据表"
])

# Tab 1: 招聘速度与效率
with tab1:
    st.markdown('<h2 class="sub-header">1. 招聘速度与效率 (Speed & Efficiency)</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # 平均招聘周期趋势
        monthly_ttf = filtered_df.groupby('月份')['平均招聘周期_天'].mean().reset_index()
        fig1 = px.line(monthly_ttf, x='月份', y='平均招聘周期_天',
                      title='平均招聘周期趋势 (Time to Fill)',
                      markers=True)
        fig1.update_layout(height=350)
        st.plotly_chart(fig1, use_container_width=True)

        # 各阶段耗时分解
        stage_time = pd.DataFrame({
            '阶段': ['审批耗时', '寻访耗时', '面试反馈'],
            '平均天数': [
                filtered_df['审批耗时_天'].mean(),
                filtered_df['寻访耗时_天'].mean(),
                filtered_df['面试反馈速度_小时'].mean() / 24
            ]
        })
        fig2 = px.bar(stage_time, x='阶段', y='平均天数',
                     title='各阶段周转时间分解',
                     color='平均天数',
                     color_continuous_scale='Blues')
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # 平均录用速度 vs 招聘周期
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=filtered_df.groupby('月份')['月份'].first(),
            y=filtered_df.groupby('月份')['平均招聘周期_天'].mean(),
            name='招聘周期',
            mode='lines+markers'
        ))
        fig3.add_trace(go.Scatter(
            x=filtered_df.groupby('月份')['月份'].first(),
            y=filtered_df.groupby('月份')['平均录用速度_天'].mean(),
            name='录用速度',
            mode='lines+markers'
        ))
        fig3.update_layout(title='招聘周期 vs 录用速度对比', height=350)
        st.plotly_chart(fig3, use_container_width=True)

        # 招聘及时率和职位老化率
        fig4 = make_subplots(specs=[[{"secondary_y": True}]])
        fig4.add_trace(
            go.Bar(
                x=filtered_df.groupby('月份')['月份'].first(),
                y=filtered_df.groupby('月份')['招聘及时率_%'].mean(),
                name="招聘及时率"
            ),
            secondary_y=False
        )
        fig4.add_trace(
            go.Scatter(
                x=filtered_df.groupby('月份')['月份'].first(),
                y=filtered_df.groupby('月份')['职位老化率_%'].mean(),
                name="职位老化率",
                mode='lines+markers',
                line=dict(color='red')
            ),
            secondary_y=True
        )
        fig4.update_layout(title='招聘及时率 & 职位老化率', height=350)
        fig4.update_yaxes(title_text="招聘及时率 (%)", secondary_y=False)
        fig4.update_yaxes(title_text="职位老化率 (%)", secondary_y=True)
        st.plotly_chart(fig4, use_container_width=True)

    # 详细指标卡片
    st.markdown("### 📋 详细指标")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("平均审批耗时", f"{filtered_df['审批耗时_天'].mean():.1f}天")
        st.metric("流程停滞天数", f"{filtered_df['流程停滞天数'].mean():.1f}天")

    with metric_col2:
        st.metric("平均寻访耗时", f"{filtered_df['寻访耗时_天'].mean():.1f}天")
        st.metric("逾期职位数", f"{filtered_df['逾期职位数'].sum():.0f}个")

    with metric_col3:
        st.metric("面试反馈速度", f"{filtered_df['面试反馈速度_小时'].mean():.1f}小时")
        st.metric("重启职位数", f"{filtered_df['重启职位数'].sum():.0f}个")

    with metric_col4:
        st.metric("招聘及时率", f"{filtered_df['招聘及时率_%'].mean():.1f}%")
        st.metric("职位老化率", f"{filtered_df['职位老化率_%'].mean():.1f}%")

# Tab 2: 招聘质量与结果
with tab2:
    st.markdown('<h2 class="sub-header">2. 招聘质量与结果 (Quality of Hire)</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # 试用期转正率趋势
        monthly_probation = filtered_df.groupby('月份')['试用期转正率_%'].mean().reset_index()
        fig5 = px.line(monthly_probation, x='月份', y='试用期转正率_%',
                      title='试用期转正率趋势 (Probation Pass Rate)',
                      markers=True)
        fig5.add_hline(y=90, line_dash="dash", line_color="green",
                      annotation_text="目标线: 90%")
        fig5.update_layout(height=350)
        st.plotly_chart(fig5, use_container_width=True)

        # 新员工绩效分布
        fig6 = px.histogram(filtered_df, x='新员工首年绩效_分',
                           title='新员工首年绩效分布',
                           nbins=20,
                           color_discrete_sequence=['#636EFA'])
        fig6.update_layout(height=350)
        st.plotly_chart(fig6, use_container_width=True)

    with col2:
        # 早期离职率分析
        turnover_data = pd.DataFrame({
            '类型': ['首月流失率', '早期离职率 (<6月)'],
            '比率 (%)': [
                filtered_df['首月流失率_%'].mean(),
                filtered_df['新员工早期离职率_%'].mean()
            ]
        })
        fig7 = px.bar(turnover_data, x='类型', y='比率 (%)',
                     title='新员工离职率分析',
                     color='比率 (%)',
                     color_continuous_scale='Reds')
        fig7.update_layout(height=350)
        st.plotly_chart(fig7, use_container_width=True)

        # 用人经理满意度 vs 简历质量满意度
        satisfaction_monthly = filtered_df.groupby('月份').agg({
            '用人经理满意度_分': 'mean',
            '简历质量满意度_分': 'mean'
        }).reset_index()

        fig8 = go.Figure()
        fig8.add_trace(go.Scatter(
            x=satisfaction_monthly['月份'],
            y=satisfaction_monthly['用人经理满意度_分'],
            name='用人经理满意度',
            mode='lines+markers',
            fill='tonexty'
        ))
        fig8.add_trace(go.Scatter(
            x=satisfaction_monthly['月份'],
            y=satisfaction_monthly['简历质量满意度_分'],
            name='简历质量满意度',
            mode='lines+markers',
            fill='tonexty'
        ))
        fig8.update_layout(title='满意度趋势对比', height=350)
        st.plotly_chart(fig8, use_container_width=True)

    # 入职职级分布
    st.markdown("### 👥 入职职级分布 (New Hire by Level)")
    level_dist = filtered_df.groupby('职级')['招聘人数'].sum().reset_index()
    fig9 = px.pie(level_dist, values='招聘人数', names='职级',
                 title='各职级招聘人数分布',
                 hole=0.4)
    st.plotly_chart(fig9, use_container_width=True)

    # 详细指标
    st.markdown("### 📋 详细指标")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("试用期转正率", f"{filtered_df['试用期转正率_%'].mean():.1f}%")
        st.metric("试用期延长率", f"{filtered_df['试用期延长率_%'].mean():.1f}%")

    with metric_col2:
        st.metric("新员工首年绩效", f"{filtered_df['新员工首年绩效_分'].mean():.2f}分")
        st.metric("绩效校准差异", f"{filtered_df['绩效校准差异_分'].mean():.2f}分")

    with metric_col3:
        st.metric("早期离职率", f"{filtered_df['新员工早期离职率_%'].mean():.1f}%")
        st.metric("首月流失率", f"{filtered_df['首月流失率_%'].mean():.1f}%")

    with metric_col4:
        st.metric("用人经理满意度", f"{filtered_df['用人经理满意度_分'].mean():.2f}分")
        st.metric("关键岗位达成率", f"{filtered_df['关键岗位达成率_%'].mean():.1f}%")

# Tab 3: 漏斗与转化
with tab3:
    st.markdown('<h2 class="sub-header">3. 漏斗与转化 (Funnel & Conversion)</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # 录用接受率趋势
        monthly_offer = filtered_df.groupby('月份')['录用接受率_%'].mean().reset_index()
        fig10 = px.area(monthly_offer, x='月份', y='录用接受率_%',
                       title='录用接受率趋势 (Offer Acceptance Rate)',
                       color_discrete_sequence=['#00CC96'])
        fig10.add_hline(y=75, line_dash="dash", line_color="red",
                       annotation_text="目标线: 75%")
        fig10.update_layout(height=350)
        st.plotly_chart(fig10, use_container_width=True)

        # 招聘漏斗
        funnel_data = pd.DataFrame({
            '阶段': ['简历初筛', '面试', '录用接受'],
            '通过率 (%)': [
                filtered_df['简历初筛通过率_%'].mean(),
                filtered_df['面试通过率_%'].mean(),
                filtered_df['录用接受率_%'].mean()
            ]
        })
        fig11 = go.Figure(go.Funnel(
            y=funnel_data['阶段'],
            x=funnel_data['通过率 (%)'],
            textinfo="value+percent initial"
        ))
        fig11.update_layout(title='招聘漏斗转化率', height=350)
        st.plotly_chart(fig11, use_container_width=True)

    with col2:
        # 渠道有效性分析
        channel_effectiveness = filtered_df.groupby('渠道').agg({
            '渠道简历转化率_%': 'mean',
            '招聘人数': 'sum'
        }).reset_index()

        fig12 = px.scatter(channel_effectiveness,
                          x='渠道简历转化率_%',
                          y='招聘人数',
                          size='招聘人数',
                          color='渠道',
                          title='渠道有效性矩阵 (转化率 vs 招聘量)',
                          hover_data=['渠道'])
        fig12.update_layout(height=350)
        st.plotly_chart(fig12, use_container_width=True)

        # 候选人库覆盖率
        monthly_coverage = filtered_df.groupby('月份')['候选人库覆盖率'].mean().reset_index()
        fig13 = px.bar(monthly_coverage, x='月份', y='候选人库覆盖率',
                      title='候选人库覆盖率趋势 (Pipeline Coverage)',
                      color='候选人库覆盖率',
                      color_continuous_scale='Viridis')
        fig13.add_hline(y=2.0, line_dash="dash", line_color="green",
                       annotation_text="理想覆盖率: 2.0")
        fig13.update_layout(height=350)
        st.plotly_chart(fig13, use_container_width=True)

    # 全流程转化率详情
    st.markdown("### 🔄 全流程转化率详情")
    conversion_col1, conversion_col2, conversion_col3 = st.columns(3)

    with conversion_col1:
        st.metric("简历初筛通过率", f"{filtered_df['简历初筛通过率_%'].mean():.1f}%")
        st.metric("人才地图完备度", f"{filtered_df['人才地图完备度_%'].mean():.1f}%")

    with conversion_col2:
        st.metric("面试通过率", f"{filtered_df['面试通过率_%'].mean():.1f}%")
        st.metric("渠道简历转化率", f"{filtered_df['渠道简历转化率_%'].mean():.1f}%")

    with conversion_col3:
        st.metric("录用接受率", f"{filtered_df['录用接受率_%'].mean():.1f}%")
        st.metric("候选人库覆盖率", f"{filtered_df['候选人库覆盖率'].mean():.2f}x")

# Tab 4: 成本与生产力
with tab4:
    st.markdown('<h2 class="sub-header">4. 成本与生产力 (Cost & Productivity)</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # 单次招聘成本趋势
        monthly_cost = filtered_df.groupby('月份')['单次招聘成本_元'].mean().reset_index()
        fig14 = px.line(monthly_cost, x='月份', y='单次招聘成本_元',
                       title='单次招聘成本趋势 (Cost per Hire)',
                       markers=True,
                       color_discrete_sequence=['#EF553B'])
        fig14.update_layout(height=350)
        st.plotly_chart(fig14, use_container_width=True)

        # 招聘成本构成
        cost_breakdown = pd.DataFrame({
            '类型': ['猎头费用', '渠道费用', '其他费用'],
            '占比 (%)': [
                filtered_df['猎头费用占比_%'].mean(),
                30,  # 渠道费用占比（模拟）
                100 - filtered_df['猎头费用占比_%'].mean() - 30
            ]
        })
        fig15 = px.pie(cost_breakdown, values='占比 (%)', names='类型',
                      title='招聘成本构成',
                      hole=0.4,
                      color_discrete_sequence=px.colors.sequential.RdBu)
        fig15.update_layout(height=350)
        st.plotly_chart(fig15, use_container_width=True)

    with col2:
        # 招聘顾问人效
        recruiter_productivity = filtered_df.groupby('招聘顾问')['招聘顾问人效_人'].mean().reset_index()
        fig16 = px.bar(recruiter_productivity, x='招聘顾问', y='招聘顾问人效_人',
                      title='招聘顾问人效对比 (Recruiter Productivity)',
                      color='招聘顾问人效_人',
                      color_continuous_scale='Greens')
        fig16.update_layout(height=350)
        st.plotly_chart(fig16, use_container_width=True)

        # 预算执行率
        monthly_budget = filtered_df.groupby('月份')['招聘预算执行率_%'].mean().reset_index()
        fig17 = go.Figure()
        fig17.add_trace(go.Bar(
            x=monthly_budget['月份'],
            y=monthly_budget['招聘预算执行率_%'],
            marker_color=monthly_budget['招聘预算执行率_%'].apply(
                lambda x: 'green' if x <= 100 else 'red'
            )
        ))
        fig17.add_hline(y=100, line_dash="dash", line_color="blue",
                       annotation_text="预算基准: 100%")
        fig17.update_layout(title='招聘预算执行率', height=350)
        st.plotly_chart(fig17, use_container_width=True)

    # 部门成本对比
    st.markdown("### 💼 部门招聘成本对比")
    dept_cost = filtered_df.groupby('部门').agg({
        '单次招聘成本_元': 'mean',
        '招聘人数': 'sum'
    }).reset_index()
    dept_cost['总成本'] = dept_cost['单次招聘成本_元'] * dept_cost['招聘人数']

    fig18 = px.bar(dept_cost, x='部门', y='总成本',
                  title='各部门总招聘成本',
                  color='单次招聘成本_元',
                  color_continuous_scale='Reds',
                  hover_data=['招聘人数', '单次招聘成本_元'])
    st.plotly_chart(fig18, use_container_width=True)

    # 详细指标
    st.markdown("### 📋 详细指标")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("单次招聘成本", f"¥{filtered_df['单次招聘成本_元'].mean():.0f}")
        st.metric("猎头费用占比", f"{filtered_df['猎头费用占比_%'].mean():.1f}%")

    with metric_col2:
        st.metric("渠道单价", f"¥{filtered_df['渠道单价_元'].mean():.0f}")
        st.metric("招聘顾问人效", f"{filtered_df['招聘顾问人效_人'].mean():.1f}人")

    with metric_col3:
        st.metric("人均负责职位数", f"{filtered_df['人均负责职位数'].mean():.1f}个")
        st.metric("预算执行率", f"{filtered_df['招聘预算执行率_%'].mean():.1f}%")

    with metric_col4:
        st.metric("平均定薪涨幅", f"{filtered_df['平均定薪涨幅_%'].mean():.1f}%")
        total_cost = (filtered_df['单次招聘成本_元'] * filtered_df['招聘人数']).sum()
        st.metric("总招聘成本", f"¥{total_cost:,.0f}")

# Tab 5: 体验与品牌
with tab5:
    st.markdown('<h2 class="sub-header">5. 体验与品牌 (Experience & Brand)</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # 候选人NPS趋势
        monthly_nps = filtered_df.groupby('月份')['候选人NPS'].mean().reset_index()
        fig19 = px.line(monthly_nps, x='月份', y='候选人NPS',
                       title='候选人净推荐值趋势 (Candidate NPS)',
                       markers=True,
                       color_discrete_sequence=['#AB63FA'])
        fig19.add_hline(y=0, line_dash="dash", line_color="gray")
        fig19.add_hline(y=30, line_dash="dash", line_color="green",
                       annotation_text="优秀线: 30")
        fig19.update_layout(height=350)
        st.plotly_chart(fig19, use_container_width=True)

        # 面试官专业度评分
        monthly_interviewer = filtered_df.groupby('月份')['面试官专业度评分'].mean().reset_index()
        fig20 = px.bar(monthly_interviewer, x='月份', y='面试官专业度评分',
                      title='面试官专业度评分趋势',
                      color='面试官专业度评分',
                      color_continuous_scale='Blues')
        fig20.add_hline(y=4.0, line_dash="dash", line_color="green",
                       annotation_text="合格线: 4.0")
        fig20.update_layout(height=350)
        st.plotly_chart(fig20, use_container_width=True)

    with col2:
        # 申请完成率 vs 移动端占比
        fig21 = make_subplots(specs=[[{"secondary_y": True}]])

        monthly_app = filtered_df.groupby('月份').agg({
            '申请完成率_%': 'mean',
            '移动端申请占比_%': 'mean'
        }).reset_index()

        fig21.add_trace(
            go.Bar(
                x=monthly_app['月份'],
                y=monthly_app['申请完成率_%'],
                name="申请完成率",
                marker_color='lightblue'
            ),
            secondary_y=False
        )
        fig21.add_trace(
            go.Scatter(
                x=monthly_app['月份'],
                y=monthly_app['移动端申请占比_%'],
                name="移动端占比",
                mode='lines+markers',
                line=dict(color='orange', width=3)
            ),
            secondary_y=True
        )
        fig21.update_layout(title='申请完成率 & 移动端占比', height=350)
        fig21.update_yaxes(title_text="申请完成率 (%)", secondary_y=False)
        fig21.update_yaxes(title_text="移动端占比 (%)", secondary_y=True)
        st.plotly_chart(fig21, use_container_width=True)

        # 雇主品牌触达
        monthly_reach = filtered_df.groupby('月份')['雇主品牌触达_PV'].sum().reset_index()
        fig22 = px.area(monthly_reach, x='月份', y='雇主品牌触达_PV',
                       title='雇主品牌触达量趋势 (Brand Reach)',
                       color_discrete_sequence=['#FFA15A'])
        fig22.update_layout(height=350)
        st.plotly_chart(fig22, use_container_width=True)

    # 候选人体验指标雷达图
    st.markdown("### 🎯 候选人体验综合评估")

    experience_metrics = {
        '候选人NPS': (filtered_df['候选人NPS'].mean() + 100) / 2,  # 归一化到0-100
        '面试官专业度': filtered_df['面试官专业度评分'].mean() * 20,  # 归一化到0-100
        '申请完成率': filtered_df['申请完成率_%'].mean(),
        '职位点击率': filtered_df['职位点击申请率_%'].mean(),
        '低幽灵率': 100 - filtered_df['幽灵率_%'].mean(),  # 反向指标
        '低爽约率': 100 - filtered_df['面试爽约率_%'].mean()  # 反向指标
    }

    fig23 = go.Figure()
    fig23.add_trace(go.Scatterpolar(
        r=list(experience_metrics.values()),
        theta=list(experience_metrics.keys()),
        fill='toself',
        name='候选人体验指标'
    ))
    fig23.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title='候选人体验六维雷达图',
        height=500
    )
    st.plotly_chart(fig23, use_container_width=True)

    # 多元化指标
    st.markdown("### 🌈 多元化与包容性")
    col1, col2 = st.columns(2)

    with col1:
        monthly_diversity = filtered_df.groupby('月份')['多元化候选人占比_%'].mean().reset_index()
        fig24 = px.line(monthly_diversity, x='月份', y='多元化候选人占比_%',
                       title='多元化候选人占比趋势',
                       markers=True,
                       color_discrete_sequence=['#19D3F3'])
        st.plotly_chart(fig24, use_container_width=True)

    with col2:
        monthly_offer_diversity = filtered_df.groupby('月份')['Offer多元化率_%'].mean().reset_index()
        fig25 = px.line(monthly_offer_diversity, x='月份', y='Offer多元化率_%',
                       title='Offer多元化率趋势',
                       markers=True,
                       color_discrete_sequence=['#FF6692'])
        st.plotly_chart(fig25, use_container_width=True)

    # 详细指标
    st.markdown("### 📋 详细指标")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("候选人NPS", f"{filtered_df['候选人NPS'].mean():.1f}")
        st.metric("幽灵率", f"{filtered_df['幽灵率_%'].mean():.1f}%")

    with metric_col2:
        st.metric("面试官专业度", f"{filtered_df['面试官专业度评分'].mean():.2f}分")
        st.metric("面试爽约率", f"{filtered_df['面试爽约率_%'].mean():.1f}%")

    with metric_col3:
        st.metric("申请完成率", f"{filtered_df['申请完成率_%'].mean():.1f}%")
        st.metric("职位点击申请率", f"{filtered_df['职位点击申请率_%'].mean():.1f}%")

    with metric_col4:
        st.metric("移动端申请占比", f"{filtered_df['移动端申请占比_%'].mean():.1f}%")
        st.metric("多元化候选人占比", f"{filtered_df['多元化候选人占比_%'].mean():.1f}%")

# Tab 6: 详细数据表
with tab6:
    st.markdown('<h2 class="sub-header">📋 详细数据表</h2>', unsafe_allow_html=True)

    # 数据导出功能
    st.markdown("### 📥 数据导出")

    # 选择要导出的维度
    export_dimension = st.radio(
        "选择分析维度",
        ["按月汇总", "按招聘顾问汇总", "按部门汇总", "按渠道汇总", "原始明细数据"]
    )

    if export_dimension == "按月汇总":
        summary_df = filtered_df.groupby('月份').agg({
            '平均招聘周期_天': 'mean',
            '试用期转正率_%': 'mean',
            '录用接受率_%': 'mean',
            '单次招聘成本_元': 'mean',
            '候选人NPS': 'mean',
            '招聘人数': 'sum',
            '新员工早期离职率_%': 'mean',
            '用人经理满意度_分': 'mean'
        }).round(2).reset_index()
        display_df = summary_df

    elif export_dimension == "按招聘顾问汇总":
        summary_df = filtered_df.groupby('招聘顾问').agg({
            '平均招聘周期_天': 'mean',
            '招聘顾问人效_人': 'mean',
            '单次招聘成本_元': 'mean',
            '录用接受率_%': 'mean',
            '招聘人数': 'sum',
            '用人经理满意度_分': 'mean',
            '候选人NPS': 'mean'
        }).round(2).reset_index()
        display_df = summary_df

    elif export_dimension == "按部门汇总":
        summary_df = filtered_df.groupby('部门').agg({
            '平均招聘周期_天': 'mean',
            '单次招聘成本_元': 'mean',
            '招聘人数': 'sum',
            '试用期转正率_%': 'mean',
            '新员工早期离职率_%': 'mean',
            '关键岗位达成率_%': 'mean'
        }).round(2).reset_index()
        display_df = summary_df

    elif export_dimension == "按渠道汇总":
        summary_df = filtered_df.groupby('渠道').agg({
            '渠道简历转化率_%': 'mean',
            '招聘人数': 'sum',
            '渠道单价_元': 'mean',
            '单次招聘成本_元': 'mean',
            '录用接受率_%': 'mean'
        }).round(2).reset_index()
        display_df = summary_df

    else:  # 原始明细数据
        display_df = filtered_df.copy()
        display_df['月份'] = display_df['月份'].dt.strftime('%Y-%m')

    # 显示数据表
    st.dataframe(display_df, use_container_width=True, height=400)

    # 下载按钮
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 下载CSV文件",
        data=csv,
        file_name=f"recruitment_data_{export_dimension}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    # 数据统计摘要
    st.markdown("### 📊 数据统计摘要")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"**数据记录数:** {len(filtered_df)}")
        st.info(f"**时间跨度:** {filtered_df['月份'].min().strftime('%Y-%m')} 至 {filtered_df['月份'].max().strftime('%Y-%m')}")

    with col2:
        st.info(f"**招聘顾问数:** {filtered_df['招聘顾问'].nunique()}")
        st.info(f"**涉及部门数:** {filtered_df['部门'].nunique()}")

    with col3:
        st.info(f"**总招聘人数:** {filtered_df['招聘人数'].sum():.0f}")
        st.info(f"**平均招聘周期:** {filtered_df['平均招聘周期_天'].mean():.1f}天")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 20px;'>
    <p>🎯 人力资源招聘指标驾驶舱 v1.0</p>
    <p>数据更新时间: {}</p>
    <p>基于《驾驶舱-人力资源招聘指标体系》构建</p>
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

