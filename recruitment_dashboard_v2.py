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
    page_title="人力资源招聘指标驾驶舱 v2.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 包含卡片翻转效果
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

    /* 翻转卡片样式 */
    .flip-card {
        background-color: transparent;
        width: 100%;
        height: 200px;
        perspective: 1000px;
        margin-bottom: 20px;
    }
    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.6s;
        transform-style: preserve-3d;
    }
    .flip-card:hover .flip-card-inner {
        transform: rotateY(180deg);
    }
    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .flip-card-front {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .flip-card-back {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        transform: rotateY(180deg);
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow-y: auto;
        font-size: 12px;
        text-align: left;
    }
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 16px;
        opacity: 0.9;
    }

    /* 洞察卡片样式 */
    .insight-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
        margin: 10px 0;
    }
    .insight-title {
        font-weight: bold;
        color: #c92a2a;
        font-size: 16px;
        margin-bottom: 5px;
    }
    .action-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #20c997;
        margin: 10px 0;
    }
    .action-title {
        font-weight: bold;
        color: #087f5b;
        font-size: 16px;
        margin-bottom: 5px;
    }

    /* 角色标签 */
    .role-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        margin: 2px;
    }
    .role-hrvp {
        background-color: #e7f5ff;
        color: #1971c2;
    }
    .role-hrd {
        background-color: #f3f0ff;
        color: #5f3dc4;
    }
    .role-hr {
        background-color: #e3fafc;
        color: #0c8599;
    }
    .role-business {
        background-color: #fff4e6;
        color: #e8590c;
    }

    /* 说明框 */
    .info-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 10px 0;
    }

    /* 提示框 */
    .tip-box {
        background-color: #fff3bf;
        padding: 10px 15px;
        border-radius: 5px;
        border-left: 3px solid #ffa94d;
        margin: 5px 0;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# 指标定义数据库
METRICS_DEFINITIONS = {
    "平均招聘周期_天": {
        "name": "平均招聘周期 (Time to Fill)",
        "definition": "从HC审批通过到新员工入职的天数",
        "formula": "Σ(入职日 - 需求审批日) / 招聘总人数",
        "components": ["审批耗时", "寻访耗时", "面试耗时", "Offer沟通", "入职准备"],
        "benchmark": "优秀<30天, 良好30-45天, 需改进>45天",
        "roles": ["HRVP", "HRD", "HR"]
    },
    "试用期转正率_%": {
        "name": "试用期转正率 (Probation Pass Rate)",
        "definition": "顺利通过试用期考核的员工比例",
        "formula": "(期间转正人数 / 期间应转正总人数) × 100%",
        "components": ["转正人数", "应转正人数", "延长试用", "试用期失败"],
        "benchmark": "优秀>90%, 良好80-90%, 需改进<80%",
        "roles": ["HRVP", "HRD", "业务部门"]
    },
    "录用接受率_%": {
        "name": "录用接受率 (Offer Acceptance Rate)",
        "definition": "候选人接受Offer的比例",
        "formula": "(接受Offer数 / 发出Offer总数) × 100%",
        "components": ["发出Offer数", "接受数", "拒绝数", "拒绝原因分析"],
        "benchmark": "优秀>80%, 良好70-80%, 需改进<70%",
        "roles": ["HRVP", "HRD", "HR"]
    },
    "单次招聘成本_元": {
        "name": "单次招聘成本 (Cost per Hire)",
        "definition": "招募一名新员工的平均费用",
        "formula": "(外部渠道费+猎头费+内部团队成本) / 入职人数",
        "components": ["渠道费用", "猎头费用", "内推奖励", "团队成本"],
        "benchmark": "因岗位而异,初级<5000, 中级5000-10000, 高级>10000",
        "roles": ["HRVP", "HRD"]
    },
    "候选人NPS": {
        "name": "候选人净推荐值 (Candidate NPS)",
        "definition": "候选人推荐面试体验的意愿",
        "formula": "推荐者% - 贬损者% (含未录用人员)",
        "components": ["推荐者(9-10分)", "中立者(7-8分)", "贬损者(0-6分)"],
        "benchmark": "优秀>30, 良好10-30, 需改进<10",
        "roles": ["HRVP", "HRD", "HR"]
    },
}

# 角色配置
ROLE_CONFIG = {
    "HRVP": {
        "name": "人力资源副总裁",
        "description": "关注战略指标、成本控制、整体效能",
        "key_metrics": ["平均招聘周期_天", "单次招聘成本_元", "招聘顾问人效_人", "试用期转正率_%", "候选人NPS"],
        "color": "#1971c2"
    },
    "HRD": {
        "name": "人力资源总监",
        "description": "关注流程优化、质量管理、团队管理",
        "key_metrics": ["招聘及时率_%", "录用接受率_%", "用人经理满意度_分", "新员工早期离职率_%", "招聘预算执行率_%"],
        "color": "#5f3dc4"
    },
    "HR": {
        "name": "招聘专员/顾问",
        "description": "关注执行指标、日常运营、候选人体验",
        "key_metrics": ["简历初筛通过率_%", "面试通过率_%", "面试反馈速度_小时", "候选人库覆盖率", "幽灵率_%"],
        "color": "#0c8599"
    },
    "业务部门": {
        "name": "用人部门经理",
        "description": "关注招聘速度、候选人质量、团队稳定性",
        "key_metrics": ["平均招聘周期_天", "试用期转正率_%", "新员工首年绩效_分", "关键岗位达成率_%", "核心岗空窗期_天"],
        "color": "#e8590c"
    }
}

# AI洞察生成函数
def generate_ai_insights(metric_name, metric_value, df, metric_type="general"):
    """根据指标生成AI洞察和建议"""
    insights = []
    actions = []

    if metric_name == "平均招聘周期_天":
        if metric_value > 45:
            insights.append("🔴 招聘周期过长,已超过行业平均水平(30-40天),可能影响关键岗位的及时补充")
            insights.append(f"📊 当前平均{metric_value:.0f}天,比目标慢{metric_value-35:.0f}天")
            actions.append("⚡ 立即行动: 分析审批和寻访环节,识别最大瓶颈")
            actions.append("🎯 优化建议: 建立快速通道机制,关键岗位审批时间压缩至3天内")
            actions.append("📋 后续跟进: 每周review卡住的职位,主动push进度")
        elif metric_value > 35:
            insights.append("🟡 招聘周期略长,有优化空间")
            actions.append("💡 建议: 分析各环节耗时占比,重点优化最慢环节")
        else:
            insights.append("🟢 招聘周期控制良好,保持当前效率")
            actions.append("✅ 持续: 分享最佳实践,在团队内推广")

    elif metric_name == "试用期转正率_%":
        if metric_value < 80:
            insights.append("🔴 转正率偏低,可能存在招聘标准不清晰或候选人质量问题")
            insights.append(f"📊 当前{metric_value:.1f}%,低于目标90%")
            actions.append("🔍 深入分析: 统计未转正原因(能力/文化/其他)")
            actions.append("📝 改进措施: 优化面试评估标准,增加试用期中期反馈")
            actions.append("👥 培训计划: 强化面试官校准培训")
        elif metric_value < 90:
            insights.append("🟡 转正率有提升空间")
            actions.append("💡 建议: 关注试用期延长的案例,提前干预")
        else:
            insights.append("🟢 转正率表现优秀")
            actions.append("✅ 保持: 继续严格把控招聘质量")

    elif metric_name == "录用接受率_%":
        if metric_value < 70:
            insights.append("🔴 Offer接受率低,可能存在薪酬竞争力不足或候选人期望管理不到位")
            insights.append(f"📊 有{100-metric_value:.1f}%的Offer被拒绝")
            actions.append("💰 薪酬分析: 对比被拒Offer的薪资与市场水平")
            actions.append("🗣️ 沟通优化: Offer前充分了解候选人顾虑,提前解决")
            actions.append("⏰ 时效管理: 缩短Offer发放时间,避免候选人被竞对截胡")
        elif metric_value < 80:
            insights.append("🟡 Offer接受率可以提升")
            actions.append("💡 建议: 分析拒绝原因TOP3,针对性改进")
        else:
            insights.append("🟢 Offer接受率健康")
            actions.append("✅ 继续: 保持良好的候选人体验和薪酬竞争力")

    elif metric_name == "候选人NPS":
        if metric_value < 10:
            insights.append("🔴 候选人体验亟需改善,低NPS会影响雇主品牌")
            actions.append("📞 紧急调研: 电话回访近期候选人,了解痛点")
            actions.append("👨‍💼 面试官培训: 强化面试礼仪和专业度")
            actions.append("⏱️ 流程优化: 缩短反馈周期,提升沟通响应速度")
        elif metric_value < 30:
            insights.append("🟡 候选人体验有改进空间")
            actions.append("💡 建议: 重点关注未录用候选人的反馈")
        else:
            insights.append("🟢 候选人体验优秀,良好的口碑会带来更多推荐")
            actions.append("✅ 放大优势: 将优秀案例制作成雇主品牌素材")

    elif metric_name == "单次招聘成本_元":
        avg_cost = metric_value
        if avg_cost > 15000:
            insights.append("🔴 招聘成本过高,需要优化渠道组合")
            actions.append("📊 成本分析: 拆解猎头费用、渠道费用占比")
            actions.append("🔄 渠道优化: 提升内推和低成本渠道占比")
            actions.append("💡 长期策略: 建立人才库,减少对外部渠道依赖")
        elif avg_cost > 10000:
            insights.append("🟡 招聘成本偏高,有优化空间")
            actions.append("💡 建议: 分析高成本岗位,寻找替代渠道")
        else:
            insights.append("🟢 招聘成本控制良好")
            actions.append("✅ 保持: 继续优化渠道mix,控制成本")

    # 通用洞察
    if len(insights) == 0:
        insights.append("📊 指标数据已记录,持续关注趋势变化")
        actions.append("📈 建议: 定期对比历史数据,发现异常及时处理")

    return insights, actions

# 生成模拟数据
@st.cache_data
def generate_mock_data():
    """生成模拟招聘数据"""
    np.random.seed(42)

    months = pd.date_range(start='2025-01-01', end='2025-12-31', freq='MS')
    recruiters = ['张伟', '李娜', '王芳', '刘洋', '陈静']
    departments = ['技术部', '产品部', '市场部', '销售部', '运营部']
    positions = ['初级', '中级', '高级', '专家', '管理层']
    channels = ['招聘网站', '猎头', '内推', '校园招聘', '社交媒体']

    data = {
        '月份': [], '招聘顾问': [], '部门': [], '职级': [], '渠道': [],
        '平均招聘周期_天': [], '审批耗时_天': [], '寻访耗时_天': [],
        '平均录用速度_天': [], '流程停滞天数': [], '面试反馈速度_小时': [],
        '招聘及时率_%': [], '逾期职位数': [], '职位老化率_%': [], '重启职位数': [],
        '试用期转正率_%': [], '试用期延长率_%': [], '新员工首年绩效_分': [],
        '绩效校准差异_分': [], '新员工早期离职率_%': [], '首月流失率_%': [],
        '用人经理满意度_分': [], '简历质量满意度_分': [], '关键岗位达成率_%': [],
        '核心岗空窗期_天': [], '录用接受率_%': [], '简历初筛通过率_%': [],
        '面试通过率_%': [], '渠道简历转化率_%': [], '候选人库覆盖率': [],
        '人才地图完备度_%': [], '单次招聘成本_元': [], '猎头费用占比_%': [],
        '渠道单价_元': [], '招聘顾问人效_人': [], '人均负责职位数': [],
        '招聘预算执行率_%': [], '平均定薪涨幅_%': [], '候选人NPS': [],
        '面试官专业度评分': [], '申请完成率_%': [], '移动端申请占比_%': [],
        '幽灵率_%': [], '面试爽约率_%': [], '雇主品牌触达_PV': [],
        '职位点击申请率_%': [], '多元化候选人占比_%': [], 'Offer多元化率_%': [],
        '招聘人数': [], '发出Offer数': [], '接受Offer数': [],
    }

    for month in months:
        for recruiter in recruiters:
            for dept in departments[:3]:
                row_data = {
                    '月份': month, '招聘顾问': recruiter, '部门': dept,
                    '职级': np.random.choice(positions), '渠道': np.random.choice(channels),
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
                    '录用接受率_%': np.random.uniform(60, 90),
                    '简历初筛通过率_%': np.random.uniform(15, 40),
                    '面试通过率_%': np.random.uniform(25, 60),
                    '渠道简历转化率_%': np.random.uniform(10, 35),
                    '候选人库覆盖率': np.random.uniform(1.5, 4.0),
                    '人才地图完备度_%': np.random.uniform(50, 90),
                    '单次招聘成本_元': np.random.randint(3000, 15000),
                    '猎头费用占比_%': np.random.uniform(20, 50),
                    '渠道单价_元': np.random.randint(100, 800),
                    '招聘顾问人效_人': np.random.randint(3, 12),
                    '人均负责职位数': np.random.randint(5, 15),
                    '招聘预算执行率_%': np.random.uniform(70, 105),
                    '平均定薪涨幅_%': np.random.uniform(10, 30),
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
                    '招聘人数': np.random.randint(2, 15),
                    '发出Offer数': np.random.randint(3, 20),
                    '接受Offer数': np.random.randint(2, 18),
                }
                for key, value in row_data.items():
                    data[key].append(value)

    return pd.DataFrame(data)

# 创建翻转卡片组件
def create_flip_card(metric_name, metric_value, metric_def):
    """创建可翻转的指标卡片"""
    # 角色标签
    role_badges = ""
    for role in metric_def.get("roles", []):
        role_class = f"role-{role.lower().replace('部门', 'business')}"
        role_badges += f'<span class="role-badge {role_class}">{role}</span>'

    html_code = f"""
    <div class="flip-card">
        <div class="flip-card-inner">
            <div class="flip-card-front">
                <div class="metric-label">{metric_def['name']}</div>
                <div class="metric-value">{metric_value}</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 10px;">
                    {role_badges}
                </div>
                <div style="font-size: 11px; opacity: 0.7; margin-top: 5px;">
                    鼠标悬停查看详情 →
                </div>
            </div>
            <div class="flip-card-back">
                <div style="font-weight: bold; margin-bottom: 10px; font-size: 14px;">
                    {metric_def['name']}
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>📖 定义:</strong><br/>{metric_def['definition']}
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>🧮 公式:</strong><br/>{metric_def['formula']}
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>📊 构成:</strong><br/>• {' • '.join(metric_def['components'])}
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>🎯 基准:</strong><br/>{metric_def['benchmark']}
                </div>
                <div>
                    <strong>👥 关注角色:</strong><br/>{', '.join(metric_def['roles'])}
                </div>
            </div>
        </div>
    </div>
    """
    return html_code

# 加载数据
df = generate_mock_data()

# 侧边栏 - 角色选择
st.sidebar.markdown("## 👤 选择角色视角")
selected_role = st.sidebar.selectbox(
    "选择你的角色",
    options=list(ROLE_CONFIG.keys()),
    format_func=lambda x: f"{ROLE_CONFIG[x]['name']} - {x}"
)

role_info = ROLE_CONFIG[selected_role]
st.sidebar.markdown(f"""
<div class="info-box">
    <strong>{role_info['name']}</strong><br/>
    {role_info['description']}
</div>
""", unsafe_allow_html=True)

# 侧边栏 - 数据筛选器
st.sidebar.markdown("## 🔍 数据筛选")

min_date = df['月份'].min().date()
max_date = df['月份'].max().date()
date_range = st.sidebar.date_input(
    "选择时间范围",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

selected_recruiters = st.sidebar.multiselect(
    "招聘顾问",
    options=df['招聘顾问'].unique().tolist(),
    default=df['招聘顾问'].unique().tolist()
)

selected_departments = st.sidebar.multiselect(
    "部门",
    options=df['部门'].unique().tolist(),
    default=df['部门'].unique().tolist()
)

selected_levels = st.sidebar.multiselect(
    "职级",
    options=df['职级'].unique().tolist(),
    default=df['职级'].unique().tolist()
)

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
st.markdown(f'<h1 class="main-header">🎯 人力资源招聘指标驾驶舱 v2.0</h1>', unsafe_allow_html=True)
st.markdown(f"<div style='text-align: center; color: {role_info['color']}; font-size: 20px; margin-bottom: 20px;'>当前视角: <strong>{role_info['name']}</strong></div>", unsafe_allow_html=True)

# 核心KPI - 使用翻转卡片
st.markdown('<h2 class="sub-header">📈 核心KPI总览 (鼠标悬停查看详情)</h2>', unsafe_allow_html=True)

# 根据角色显示关键指标
key_metrics_for_role = role_info['key_metrics']
cols = st.columns(min(5, len(key_metrics_for_role)))

for idx, metric_key in enumerate(key_metrics_for_role[:5]):
    with cols[idx]:
        if metric_key in filtered_df.columns:
            metric_value = filtered_df[metric_key].mean()

            # 格式化显示
            if '_%' in metric_key:
                display_value = f"{metric_value:.1f}%"
            elif '_元' in metric_key:
                display_value = f"¥{metric_value:.0f}"
            elif '_天' in metric_key:
                display_value = f"{metric_value:.1f}天"
            elif '_小时' in metric_key:
                display_value = f"{metric_value:.1f}小时"
            elif '_分' in metric_key:
                display_value = f"{metric_value:.2f}分"
            elif 'NPS' in metric_key:
                display_value = f"{metric_value:.0f}"
            else:
                display_value = f"{metric_value:.2f}"

            # 如果有定义就显示翻转卡片
            if metric_key in METRICS_DEFINITIONS:
                st.markdown(
                    create_flip_card(metric_key, display_value, METRICS_DEFINITIONS[metric_key]),
                    unsafe_allow_html=True
                )
            else:
                # 简单指标卡片
                st.metric(metric_key.replace('_', ' '), display_value)

st.markdown("---")

# Tab布局
if selected_role == "业务部门":
    # 业务部门专属视图
    tab1, tab2, tab3 = st.tabs([
        "🎯 我的招聘进度",
        "👥 候选人质量评估",
        "📊 团队稳定性分析"
    ])

    with tab1:
        st.markdown('<h2 class="sub-header">🎯 我的招聘进度</h2>', unsafe_allow_html=True)

        # 说明框
        st.markdown("""
        <div class="info-box">
            <strong>📖 这个页面告诉你什么?</strong><br/>
            展示你部门当前的招聘进度,包括招聘周期、职位填补情况和及时率。帮助你了解HR团队的交付速度。
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # 招聘周期趋势
            monthly_ttf = filtered_df.groupby('月份')['平均招聘周期_天'].mean().reset_index()
            fig1 = px.line(monthly_ttf, x='月份', y='平均招聘周期_天',
                          title='平均招聘周期趋势',
                          markers=True)
            fig1.add_hline(y=35, line_dash="dash", line_color="green",
                          annotation_text="目标: 35天")
            st.plotly_chart(fig1, use_container_width=True)

            # AI洞察
            avg_ttf = filtered_df['平均招聘周期_天'].mean()
            insights, actions = generate_ai_insights("平均招聘周期_天", avg_ttf, filtered_df)

            for insight in insights:
                st.markdown(f'<div class="insight-card"><div class="insight-title">💡 数据洞察</div>{insight}</div>', unsafe_allow_html=True)
            for action in actions:
                st.markdown(f'<div class="action-card"><div class="action-title">🎯 推荐动作</div>{action}</div>', unsafe_allow_html=True)

        with col2:
            # 关键岗位达成率
            monthly_critical = filtered_df.groupby('月份')['关键岗位达成率_%'].mean().reset_index()
            fig2 = px.bar(monthly_critical, x='月份', y='关键岗位达成率_%',
                         title='关键岗位达成率',
                         color='关键岗位达成率_%',
                         color_continuous_scale='RdYlGn')
            fig2.add_hline(y=90, line_dash="dash", line_color="red",
                          annotation_text="合格线: 90%")
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("""
            <div class="tip-box">
                💡 <strong>如何看这个图?</strong><br/>
                柱子越高越好,绿色表示完成情况良好。如果低于90%红线,说明关键岗位招聘遇到困难,建议与HR沟通。
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown('<h2 class="sub-header">👥 候选人质量评估</h2>', unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
            <strong>📖 这个页面告诉你什么?</strong><br/>
            评估推荐候选人的质量,包括试用期表现、转正率和绩效水平,帮助你判断招聘质量。
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # 试用期转正率
            monthly_probation = filtered_df.groupby('月份')['试用期转正率_%'].mean().reset_index()
            fig3 = px.line(monthly_probation, x='月份', y='试用期转正率_%',
                          title='试用期转正率趋势',
                          markers=True)
            fig3.add_hline(y=90, line_dash="dash", line_color="green",
                          annotation_text="目标: 90%")
            st.plotly_chart(fig3, use_container_width=True)

            # AI洞察
            avg_probation = filtered_df['试用期转正率_%'].mean()
            insights, actions = generate_ai_insights("试用期转正率_%", avg_probation, filtered_df)

            for insight in insights:
                st.markdown(f'<div class="insight-card"><div class="insight-title">💡 数据洞察</div>{insight}</div>', unsafe_allow_html=True)
            for action in actions:
                st.markdown(f'<div class="action-card"><div class="action-title">🎯 推荐动作</div>{action}</div>', unsafe_allow_html=True)

        with col2:
            # 新员工绩效
            fig4 = px.histogram(filtered_df, x='新员工首年绩效_分',
                               title='新员工首年绩效分布',
                               nbins=20)
            fig4.add_vline(x=4.0, line_dash="dash", line_color="green",
                          annotation_text="合格线: 4.0")
            st.plotly_chart(fig4, use_container_width=True)

            st.markdown("""
            <div class="tip-box">
                💡 <strong>如何看这个图?</strong><br/>
                分布越靠右(高分)越好。如果大部分新员工绩效在4.0以上,说明招聘质量高。
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown('<h2 class="sub-header">📊 团队稳定性分析</h2>', unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
            <strong>📖 这个页面告诉你什么?</strong><br/>
            分析新员工的留存情况,早期离职率高可能意味着岗位匹配问题或入职体验不佳。
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # 早期离职率
            monthly_turnover = filtered_df.groupby('月份')['新员工早期离职率_%'].mean().reset_index()
            fig5 = px.area(monthly_turnover, x='月份', y='新员工早期离职率_%',
                          title='新员工早期离职率趋势(<6个月)',
                          color_discrete_sequence=['#ff6b6b'])
            fig5.add_hline(y=15, line_dash="dash", line_color="red",
                          annotation_text="警戒线: 15%")
            st.plotly_chart(fig5, use_container_width=True)

            st.markdown("""
            <div class="tip-box">
                💡 <strong>如何看这个图?</strong><br/>
                趋势线越低越好。如果超过15%警戒线,建议review招聘标准和入职培训流程。
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # 核心岗空窗期
            monthly_vacancy = filtered_df.groupby('月份')['核心岗空窗期_天'].mean().reset_index()
            fig6 = px.bar(monthly_vacancy, x='月份', y='核心岗空窗期_天',
                         title='核心岗位空窗期',
                         color='核心岗空窗期_天',
                         color_continuous_scale='Reds')
            st.plotly_chart(fig6, use_container_width=True)

            st.markdown("""
            <div class="tip-box">
                💡 <strong>如何看这个图?</strong><br/>
                空窗期越短越好。长时间空窗会影响业务运转,建议提前3个月启动关键岗位招聘。
            </div>
            """, unsafe_allow_html=True)

else:
    # HR角色视图(原有的Tab结构)
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

        st.markdown("""
        <div class="info-box">
            <strong>📖 这个维度衡量什么?</strong><br/>
            衡量招聘团队响应业务需求的速度和流程流畅度。关键指标包括招聘周期、各阶段耗时和及时率。
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            monthly_ttf = filtered_df.groupby('月份')['平均招聘周期_天'].mean().reset_index()
            fig1 = px.line(monthly_ttf, x='月份', y='平均招聘周期_天',
                          title='平均招聘周期趋势 (Time to Fill)',
                          markers=True)
            fig1.add_hline(y=35, line_dash="dash", line_color="green",
                          annotation_text="目标: 35天")
            st.plotly_chart(fig1, use_container_width=True)

            # AI洞察
            avg_ttf = filtered_df['平均招聘周期_天'].mean()
            insights, actions = generate_ai_insights("平均招聘周期_天", avg_ttf, filtered_df)

            for insight in insights:
                st.markdown(f'<div class="insight-card"><div class="insight-title">💡 数据洞察</div>{insight}</div>', unsafe_allow_html=True)
            for action in actions:
                st.markdown(f'<div class="action-card"><div class="action-title">🎯 推荐动作</div>{action}</div>', unsafe_allow_html=True)

            # 阶段耗时分解
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
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("""
            <div class="tip-box">
                💡 <strong>如何优化?</strong> 找出最长的阶段,优先优化该环节。例如审批耗时长就优化审批流程,寻访耗时长就优化人才库或渠道。
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # 招聘周期 vs 录用速度
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
            fig3.update_layout(title='招聘周期 vs 录用速度对比')
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
            fig4.update_layout(title='招聘及时率 & 职位老化率')
            fig4.update_yaxes(title_text="招聘及时率 (%)", secondary_y=False)
            fig4.update_yaxes(title_text="职位老化率 (%)", secondary_y=True)
            st.plotly_chart(fig4, use_container_width=True)

            st.markdown("""
            <div class="tip-box">
                💡 <strong>关注红线!</strong> 职位老化率(红线)越高,说明有很多职位长期招不到人,需要重点关注这些"老大难"职位。
            </div>
            """, unsafe_allow_html=True)

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

        st.markdown("""
        <div class="info-box">
            <strong>📖 这个维度衡量什么?</strong><br/>
            衡量招募人才的匹配度、绩效表现及稳定性。关键指标包括转正率、绩效、离职率和满意度。
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            monthly_probation = filtered_df.groupby('月份')['试用期转正率_%'].mean().reset_index()
            fig5 = px.line(monthly_probation, x='月份', y='试用期转正率_%',
                          title='试用期转正率趋势 (Probation Pass Rate)',
                          markers=True)
            fig5.add_hline(y=90, line_dash="dash", line_color="green",
                          annotation_text="目标线: 90%")
            st.plotly_chart(fig5, use_container_width=True)

            # AI洞察
            avg_probation = filtered_df['试用期转正率_%'].mean()
            insights, actions = generate_ai_insights("试用期转正率_%", avg_probation, filtered_df)

            for insight in insights:
                st.markdown(f'<div class="insight-card"><div class="insight-title">💡 数据洞察</div>{insight}</div>', unsafe_allow_html=True)
            for action in actions:
                st.markdown(f'<div class="action-card"><div class="action-title">🎯 推荐动作</div>{action}</div>', unsafe_allow_html=True)

            fig6 = px.histogram(filtered_df, x='新员工首年绩效_分',
                               title='新员工首年绩效分布',
                               nbins=20,
                               color_discrete_sequence=['#636EFA'])
            st.plotly_chart(fig6, use_container_width=True)

        with col2:
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
            st.plotly_chart(fig7, use_container_width=True)

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
            fig8.update_layout(title='满意度趋势对比')
            st.plotly_chart(fig8, use_container_width=True)

        level_dist = filtered_df.groupby('职级')['招聘人数'].sum().reset_index()
        fig9 = px.pie(level_dist, values='招聘人数', names='职级',
                     title='各职级招聘人数分布',
                     hole=0.4)
        st.plotly_chart(fig9, use_container_width=True)

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

        st.markdown("""
        <div class="info-box">
            <strong>📖 这个维度衡量什么?</strong><br/>
            衡量招聘全流程的转化效率及渠道有效性。关键指标包括Offer接受率、各阶段通过率和渠道转化率。
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            monthly_offer = filtered_df.groupby('月份')['录用接受率_%'].mean().reset_index()
            fig10 = px.area(monthly_offer, x='月份', y='录用接受率_%',
                           title='录用接受率趋势 (Offer Acceptance Rate)',
                           color_discrete_sequence=['#00CC96'])
            fig10.add_hline(y=75, line_dash="dash", line_color="red",
                           annotation_text="目标线: 75%")
            st.plotly_chart(fig10, use_container_width=True)

            # AI洞察
            avg_offer = filtered_df['录用接受率_%'].mean()
            insights, actions = generate_ai_insights("录用接受率_%", avg_offer, filtered_df)

            for insight in insights:
                st.markdown(f'<div class="insight-card"><div class="insight-title">💡 数据洞察</div>{insight}</div>', unsafe_allow_html=True)
            for action in actions:
                st.markdown(f'<div class="action-card"><div class="action-title">🎯 推荐动作</div>{action}</div>', unsafe_allow_html=True)

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
            fig11.update_layout(title='招聘漏斗转化率')
            st.plotly_chart(fig11, use_container_width=True)

            st.markdown("""
            <div class="tip-box">
                💡 <strong>漏斗分析技巧:</strong> 找出转化率最低的环节,集中资源优化。例如初筛通过率过低说明简历质量差或标准过严。
            </div>
            """, unsafe_allow_html=True)

        with col2:
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
            st.plotly_chart(fig12, use_container_width=True)

            st.markdown("""
            <div class="tip-box">
                💡 <strong>渠道优化策略:</strong> 右上角的渠道(高转化率+高招聘量)是优质渠道,应加大投入。左下角渠道考虑淘汰或优化。
            </div>
            """, unsafe_allow_html=True)

            monthly_coverage = filtered_df.groupby('月份')['候选人库覆盖率'].mean().reset_index()
            fig13 = px.bar(monthly_coverage, x='月份', y='候选人库覆盖率',
                          title='候选人库覆盖率趋势 (Pipeline Coverage)',
                          color='候选人库覆盖率',
                          color_continuous_scale='Viridis')
            fig13.add_hline(y=2.0, line_dash="dash", line_color="green",
                           annotation_text="理想覆盖率: 2.0")
            st.plotly_chart(fig13, use_container_width=True)

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

        st.markdown("""
        <div class="info-box">
            <strong>📖 这个维度衡量什么?</strong><br/>
            衡量招聘活动的财务成本投入与团队人效。关键指标包括单次招聘成本、人效和预算执行率。
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            monthly_cost = filtered_df.groupby('月份')['单次招聘成本_元'].mean().reset_index()
            fig14 = px.line(monthly_cost, x='月份', y='单次招聘成本_元',
                           title='单次招聘成本趋势 (Cost per Hire)',
                           markers=True,
                           color_discrete_sequence=['#EF553B'])
            st.plotly_chart(fig14, use_container_width=True)

            # AI洞察
            avg_cost = filtered_df['单次招聘成本_元'].mean()
            insights, actions = generate_ai_insights("单次招聘成本_元", avg_cost, filtered_df)

            for insight in insights:
                st.markdown(f'<div class="insight-card"><div class="insight-title">💡 数据洞察</div>{insight}</div>', unsafe_allow_html=True)
            for action in actions:
                st.markdown(f'<div class="action-card"><div class="action-title">🎯 推荐动作</div>{action}</div>', unsafe_allow_html=True)

            cost_breakdown = pd.DataFrame({
                '类型': ['猎头费用', '渠道费用', '其他费用'],
                '占比 (%)': [
                    filtered_df['猎头费用占比_%'].mean(),
                    30,
                    100 - filtered_df['猎头费用占比_%'].mean() - 30
                ]
            })
            fig15 = px.pie(cost_breakdown, values='占比 (%)', names='类型',
                          title='招聘成本构成',
                          hole=0.4,
                          color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig15, use_container_width=True)

        with col2:
            recruiter_productivity = filtered_df.groupby('招聘顾问')['招聘顾问人效_人'].mean().reset_index()
            fig16 = px.bar(recruiter_productivity, x='招聘顾问', y='招聘顾问人效_人',
                          title='招聘顾问人效对比 (Recruiter Productivity)',
                          color='招聘顾问人效_人',
                          color_continuous_scale='Greens')
            st.plotly_chart(fig16, use_container_width=True)

            st.markdown("""
            <div class="tip-box">
                💡 <strong>人效分析:</strong> 人效最高的招聘顾问有哪些最佳实践?可以在团队内分享学习。
            </div>
            """, unsafe_allow_html=True)

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
            fig17.update_layout(title='招聘预算执行率')
            st.plotly_chart(fig17, use_container_width=True)

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

        st.markdown("""
        <div class="info-box">
            <strong>📖 这个维度衡量什么?</strong><br/>
            衡量雇主品牌在候选人侧的感知与反馈。关键指标包括候选人NPS、面试官专业度和申请体验。
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            monthly_nps = filtered_df.groupby('月份')['候选人NPS'].mean().reset_index()
            fig19 = px.line(monthly_nps, x='月份', y='候选人NPS',
                           title='候选人净推荐值趋势 (Candidate NPS)',
                           markers=True,
                           color_discrete_sequence=['#AB63FA'])
            fig19.add_hline(y=0, line_dash="dash", line_color="gray")
            fig19.add_hline(y=30, line_dash="dash", line_color="green",
                           annotation_text="优秀线: 30")
            st.plotly_chart(fig19, use_container_width=True)

            # AI洞察
            avg_nps = filtered_df['候选人NPS'].mean()
            insights, actions = generate_ai_insights("候选人NPS", avg_nps, filtered_df)

            for insight in insights:
                st.markdown(f'<div class="insight-card"><div class="insight-title">💡 数据洞察</div>{insight}</div>', unsafe_allow_html=True)
            for action in actions:
                st.markdown(f'<div class="action-card"><div class="action-title">🎯 推荐动作</div>{action}</div>', unsafe_allow_html=True)

            monthly_interviewer = filtered_df.groupby('月份')['面试官专业度评分'].mean().reset_index()
            fig20 = px.bar(monthly_interviewer, x='月份', y='面试官专业度评分',
                          title='面试官专业度评分趋势',
                          color='面试官专业度评分',
                          color_continuous_scale='Blues')
            fig20.add_hline(y=4.0, line_dash="dash", line_color="green",
                           annotation_text="合格线: 4.0")
            st.plotly_chart(fig20, use_container_width=True)

        with col2:
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
            fig21.update_layout(title='申请完成率 & 移动端占比')
            fig21.update_yaxes(title_text="申请完成率 (%)", secondary_y=False)
            fig21.update_yaxes(title_text="移动端占比 (%)", secondary_y=True)
            st.plotly_chart(fig21, use_container_width=True)

            monthly_reach = filtered_df.groupby('月份')['雇主品牌触达_PV'].sum().reset_index()
            fig22 = px.area(monthly_reach, x='月份', y='雇主品牌触达_PV',
                           title='雇主品牌触达量趋势 (Brand Reach)',
                           color_discrete_sequence=['#FFA15A'])
            st.plotly_chart(fig22, use_container_width=True)

        st.markdown("### 🎯 候选人体验综合评估")

        experience_metrics = {
            '候选人NPS': (filtered_df['候选人NPS'].mean() + 100) / 2,
            '面试官专业度': filtered_df['面试官专业度评分'].mean() * 20,
            '申请完成率': filtered_df['申请完成率_%'].mean(),
            '职位点击率': filtered_df['职位点击申请率_%'].mean(),
            '低幽灵率': 100 - filtered_df['幽灵率_%'].mean(),
            '低爽约率': 100 - filtered_df['面试爽约率_%'].mean()
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

        st.markdown("""
        <div class="tip-box">
            💡 <strong>雷达图解读:</strong> 图形越饱满说明体验越好。短板指标需要重点改进。
        </div>
        """, unsafe_allow_html=True)

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

        st.markdown("### 📥 数据导出")

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

        else:
            display_df = filtered_df.copy()
            display_df['月份'] = display_df['月份'].dt.strftime('%Y-%m')

        st.dataframe(display_df, use_container_width=True, height=400)

        csv = display_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下载CSV文件",
            data=csv,
            file_name=f"recruitment_data_{export_dimension}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

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
st.markdown(f"""
<div style='text-align: center; color: #7f8c8d; padding: 20px;'>
    <p>🎯 人力资源招聘指标驾驶舱 v2.0 - 支持角色视角 & AI洞察</p>
    <p>数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>基于《驾驶舱-人力资源招聘指标体系》构建</p>
</div>
""", unsafe_allow_html=True)
