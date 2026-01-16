import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from PIL import Image
from sklearn.cluster import KMeans
import matplotlib.colors as mcolors

# ==========================================
# 页面配置 - 科技咨询风格
# ==========================================
st.set_page_config(
    page_title="招聘数据驾驶舱 | Recruitment Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 品牌颜色提取工具
# ==========================================
def extract_colors_from_image(image, num_colors=6):
    """使用K-Means从图片提取主色调"""
    img = image.resize((150, 150))
    img_array = np.array(img)
    if img_array.shape[-1] == 4:
        img_array = img_array[:, :, :3]
    pixels = img_array.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    hex_colors = ['#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2]) for c in colors]
    return hex_colors

def generate_palette(base_color, n=10):
    """基于主色生成渐变色阶"""
    try:
        cmap = mcolors.LinearSegmentedColormap.from_list("custom", ["#f8f9fa", base_color, "#212529"])
        palette = [mcolors.to_hex(cmap(i/n)) for i in range(n)]
        return palette
    except:
        return px.colors.sequential.Blues

# ==========================================
# 专业严谨的CSS样式
# ==========================================
def inject_professional_css(primary_color="#1a73e8", font_family="Inter"):
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* 全局专业字体 */
        html, body, [class*="css"] {{
            font-family: '{font_family}', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            color: #1e293b;
            background: #f8fafc;
        }}

        /* 主容器 */
        .stApp {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-attachment: fixed;
        }}

        .main .block-container {{
            background: rgba(255,255,255,0.98);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.12);
            backdrop-filter: blur(10px);
        }}

        /* 标题样式 */
        .main-title {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, {primary_color} 0%, #5b21b6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }}

        .role-badge {{
            display: inline-block;
            padding: 0.5rem 1.2rem;
            border-radius: 24px;
            font-size: 0.875rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 1.5rem;
        }}

        .role-hrvp {{ background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; }}
        .role-hrd {{ background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%); color: white; }}
        .role-hr {{ background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%); color: white; }}

        /* KPI卡片 */
        .kpi-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 4px solid {primary_color};
            transition: all 0.3s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}

        .kpi-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: {primary_color};
            line-height: 1;
            margin: 0.5rem 0;
        }}

        .kpi-label {{
            font-size: 0.875rem;
            font-weight: 500;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .kpi-change {{
            font-size: 0.875rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }}

        .kpi-up {{ color: #16a34a; }}
        .kpi-down {{ color: #dc2626; }}

        /* 警报卡片 */
        .alert-card {{
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin: 0.75rem 0;
            border-left: 4px solid;
        }}

        .alert-critical {{
            background: #fef2f2;
            border-color: #dc2626;
            color: #991b1b;
        }}

        .alert-warning {{
            background: #fffbeb;
            border-color: #f59e0b;
            color: #92400e;
        }}

        .alert-success {{
            background: #f0fdf4;
            border-color: #16a34a;
            color: #166534;
        }}

        /* 任务卡片 */
        .task-card {{
            background: white;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}

        .task-urgent {{
            border-left-color: #dc2626;
            background: #fef2f2;
        }}

        .task-title {{
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 0.25rem;
        }}

        .task-meta {{
            font-size: 0.875rem;
            color: #64748b;
        }}

        /* 指标卡片组 */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }}

        .metric-item {{
            background: #f8fafc;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}

        .metric-item-label {{
            font-size: 0.8rem;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 0.25rem;
        }}

        .metric-item-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e293b;
        }}

        /* 标签 */
        .tag {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 0.25rem;
        }}

        .tag-red {{ background: #fee2e2; color: #991b1b; }}
        .tag-yellow {{ background: #fef3c7; color: #92400e; }}
        .tag-green {{ background: #d1fae5; color: #166534; }}
        .tag-blue {{ background: #dbeafe; color: #1e40af; }}

        /* 分割线 */
        hr {{
            margin: 2rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        }}

        /* 侧边栏样式 */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
        }}

        [data-testid="stSidebar"] * {{
            color: white !important;
        }}

        /* Plotly图表优化 */
        .js-plotly-plot {{
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ==========================================
# 会话状态初始化
# ==========================================
if 'brand_colors' not in st.session_state:
    st.session_state['brand_colors'] = px.colors.sequential.Blues
if 'primary_color' not in st.session_state:
    st.session_state['primary_color'] = "#1a73e8"
if 'brand_font' not in st.session_state:
    st.session_state['brand_font'] = "Inter"

# ==========================================
# 模拟数据生成
# ==========================================
@st.cache_data
def generate_enterprise_data():
    """生成企业级招聘数据"""
    np.random.seed(42)
    months = pd.date_range(start='2025-01-01', end='2025-12-31', freq='MS')
    recruiters = ['张伟', '李娜', '王芳', '刘洋', '陈静']
    departments = ['技术部', '产品部', '市场部', '销售部', '运营部']

    data = {
        '月份': [], '招聘顾问': [], '部门': [],

        # HRVP关注的战略指标
        '关键岗位按时达成率_%': [], '空缺岗位收入损失_万': [],
        '高绩效员工占比_%': [], '人才市场占有率_%': [],
        '单次招聘成本_元': [], '猎头费用占比_%': [],

        # HRD关注的异常指标
        'TTF超标率_%': [], '面试通过率_%': [], '投诉量': [],
        '招聘顾问人效_人': [], '漏斗转化率异常': [],
        'Offer毁约率_%': [], '预算执行率_%': [],

        # HR关注的执行指标
        '待处理候选人数': [], '流程停滞天数': [],
        '今日面试数': [], '个人转化率_%': [],
        '月度SLA达成进度_%': [], '招聘人数': [],
    }

    for month in months:
        for recruiter in recruiters:
            for dept in departments[:3]:
                data['月份'].append(month)
                data['招聘顾问'].append(recruiter)
                data['部门'].append(dept)

                # HRVP指标
                data['关键岗位按时达成率_%'].append(np.random.uniform(75, 95))
                data['空缺岗位收入损失_万'].append(np.random.randint(50, 500))
                data['高绩效员工占比_%'].append(np.random.uniform(60, 85))
                data['人才市场占有率_%'].append(np.random.uniform(15, 35))
                data['单次招聘成本_元'].append(np.random.randint(5000, 20000))
                data['猎头费用占比_%'].append(np.random.uniform(25, 45))

                # HRD指标
                data['TTF超标率_%'].append(np.random.uniform(10, 35))
                data['面试通过率_%'].append(np.random.uniform(20, 50))
                data['投诉量'].append(np.random.randint(0, 5))
                data['招聘顾问人效_人'].append(np.random.randint(3, 12))
                data['漏斗转化率异常'].append(np.random.choice([0, 0, 0, 1], p=[0.7, 0.1, 0.1, 0.1]))
                data['Offer毁约率_%'].append(np.random.uniform(3, 15))
                data['预算执行率_%'].append(np.random.uniform(85, 105))

                # HR指标
                data['待处理候选人数'].append(np.random.randint(5, 30))
                data['流程停滞天数'].append(np.random.randint(0, 8))
                data['今日面试数'].append(np.random.randint(1, 8))
                data['个人转化率_%'].append(np.random.uniform(15, 40))
                data['月度SLA达成进度_%'].append(np.random.uniform(60, 105))
                data['招聘人数'].append(np.random.randint(2, 15))

    return pd.DataFrame(data)

df = generate_enterprise_data()

# ==========================================
# 侧边栏 - 品牌设置
# ==========================================
with st.sidebar:
    st.markdown("### 🎨 品牌视觉定制")

    uploaded_file = st.file_uploader("上传品牌Logo/PPT截图", type=['jpg', 'png', 'jpeg'])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="品牌素材", use_container_width=True)

        if st.button("🔍 提取品牌基因", type="primary"):
            with st.spinner("AI分析中..."):
                colors = extract_colors_from_image(image)
                st.session_state['brand_colors'] = generate_palette(colors[0])
                st.session_state['primary_color'] = colors[0]
                st.success("✅ 品牌色已应用!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 👤 角色权限")

    role = st.selectbox(
        "切换角色视角",
        ["HRVP (战略层)", "HRD (管理层)", "HR (执行层)"],
        help="不同角色看到不同的指标和粒度"
    )

    st.markdown("---")
    st.markdown("### 📅 时间筛选")

    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_month = st.selectbox("起始月份", df['月份'].dt.strftime('%Y-%m').unique())
    with date_col2:
        end_month = st.selectbox("结束月份", df['月份'].dt.strftime('%Y-%m').unique(), index=11)

    filtered_df = df[
        (df['月份'].dt.strftime('%Y-%m') >= start_month) &
        (df['月份'].dt.strftime('%Y-%m') <= end_month)
    ]

    if role == "HRD (管理层)" or role == "HR (执行层)":
        st.markdown("---")
        st.markdown("### 🏢 部门筛选")
        selected_dept = st.multiselect("选择部门", df['部门'].unique(), default=df['部门'].unique())
        filtered_df = filtered_df[filtered_df['部门'].isin(selected_dept)]

    if role == "HR (执行层)":
        st.markdown("---")
        st.markdown("### 👤 个人筛选")
        selected_recruiter = st.selectbox("招聘顾问", df['招聘顾问'].unique())
        filtered_df = filtered_df[filtered_df['招聘顾问'] == selected_recruiter]

# 应用CSS
inject_professional_css(st.session_state['primary_color'], st.session_state['brand_font'])

# ==========================================
# 主界面
# ==========================================

# 角色标识
role_class = {
    "HRVP (战略层)": "role-hrvp",
    "HRD (管理层)": "role-hrd",
    "HR (执行层)": "role-hr"
}[role]

role_name_cn = {
    "HRVP (战略层)": "人力资源副总裁",
    "HRD (管理层)": "招聘总监",
    "HR (执行层)": "招聘专员"
}[role]

st.markdown(f'<div class="main-title">招聘数据驾驶舱</div>', unsafe_allow_html=True)
st.markdown(f'<div class="role-badge {role_class}">{role_name_cn} Dashboard</div>', unsafe_allow_html=True)

# ==========================================
# HRVP 视角: 战略驾驶舱(钱/战略/风险)
# ==========================================
if role == "HRVP (战略层)":
    st.markdown("## 💼 战略级KPI - 聚焦钱、战略、风险")

    # 核心KPI卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_val = filtered_df['关键岗位按时达成率_%'].mean()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">关键岗位按时达成率</div>
            <div class="kpi-value">{kpi_val:.1f}%</div>
            <div class="kpi-change kpi-{'up' if kpi_val > 80 else 'down'}">
                {'▲' if kpi_val > 80 else '▼'} vs 目标80%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        kpi_val = filtered_df['空缺岗位收入损失_万'].sum()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">空缺岗位收入损失</div>
            <div class="kpi-value">¥{kpi_val:.0f}万</div>
            <div class="kpi-change kpi-down">⚠ 需加速招聘</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        kpi_val = filtered_df['高绩效员工占比_%'].mean()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">高绩效员工占比</div>
            <div class="kpi-value">{kpi_val:.1f}%</div>
            <div class="kpi-change kpi-{'up' if kpi_val > 70 else 'down'}">
                质量{'优秀' if kpi_val > 70 else '需改进'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        kpi_val = filtered_df['单次招聘成本_元'].mean()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">平均招聘成本</div>
            <div class="kpi-value">¥{kpi_val/1000:.1f}K</div>
            <div class="kpi-change kpi-{'down' if kpi_val < 12000 else 'up'}">
                {'成本可控' if kpi_val < 12000 else '⚠ 成本偏高'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 详细指标(置顶)
    st.markdown("### 📊 详细指标矩阵")

    metrics_html = f"""
    <div class="metrics-grid">
        <div class="metric-item">
            <div class="metric-item-label">人才市场占有率</div>
            <div class="metric-item-value">{filtered_df['人才市场占有率_%'].mean():.1f}%</div>
        </div>
        <div class="metric-item">
            <div class="metric-item-label">猎头费用占比</div>
            <div class="metric-item-value">{filtered_df['猎头费用占比_%'].mean():.1f}%</div>
        </div>
        <div class="metric-item">
            <div class="metric-item-label">战略岗位数</div>
            <div class="metric-item-value">{np.random.randint(15,25)}</div>
        </div>
        <div class="metric-item">
            <div class="metric-item-label">总招聘人数</div>
            <div class="metric-item-value">{filtered_df['招聘人数'].sum()}</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)

    st.markdown("---")

    # 图表区(图表在下)
    st.markdown("### 📈 战略分析看板")

    col1, col2 = st.columns(2)

    with col1:
        # 关键岗位达成趋势
        monthly = filtered_df.groupby('月份')['关键岗位按时达成率_%'].mean().reset_index()
        fig = px.line(monthly, x='月份', y='关键岗位按时达成率_%',
                     title='关键岗位按时达成率趋势',
                     markers=True,
                     color_discrete_sequence=[st.session_state['primary_color']])
        fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="目标线80%")
        fig.update_layout(
            font=dict(family=st.session_state['brand_font']),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 成本vs质量矩阵
        dept_data = filtered_df.groupby('部门').agg({
            '单次招聘成本_元': 'mean',
            '高绩效员工占比_%': 'mean',
            '招聘人数': 'sum'
        }).reset_index()

        fig = px.scatter(dept_data, x='单次招聘成本_元', y='高绩效员工占比_%',
                        size='招聘人数', color='部门',
                        title='招聘成本 vs 人才质量矩阵',
                        color_discrete_sequence=st.session_state['brand_colors'])
        fig.update_layout(
            font=dict(family=st.session_state['brand_font']),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    # 收入损失趋势
    monthly_loss = filtered_df.groupby('月份')['空缺岗位收入损失_万'].sum().reset_index()
    fig = px.area(monthly_loss, x='月份', y='空缺岗位收入损失_万',
                 title='空缺岗位造成的收入损失趋势',
                 color_discrete_sequence=['#dc2626'])
    fig.update_layout(
        font=dict(family=st.session_state['brand_font']),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# HRD 视角: 异常报警器
# ==========================================
elif role == "HRD (管理层)":
    st.markdown("## 🚨 异常管理驾驶舱 - 红黄绿预警")

    # 核心KPI
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_val = filtered_df['TTF超标率_%'].mean()
        status = "critical" if kpi_val > 25 else ("warning" if kpi_val > 15 else "success")
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">TTF超标率</div>
            <div class="kpi-value">{kpi_val:.1f}%</div>
            <span class="tag tag-{'red' if status=='critical' else ('yellow' if status=='warning' else 'green')}">
                {'🔴 严重' if status=='critical' else ('🟡 警告' if status=='warning' else '🟢 正常')}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        kpi_val = filtered_df['Offer毁约率_%'].mean()
        status = "critical" if kpi_val > 10 else ("warning" if kpi_val > 6 else "success")
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Offer毁约率</div>
            <div class="kpi-value">{kpi_val:.1f}%</div>
            <span class="tag tag-{'red' if status=='critical' else ('yellow' if status=='warning' else 'green')}">
                {'🔴 严重' if status=='critical' else ('🟡 警告' if status=='warning' else '🟢 正常')}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        kpi_val = filtered_df['招聘顾问人效_人'].mean()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">团队人均产能</div>
            <div class="kpi-value">{kpi_val:.1f}人/月</div>
            <div class="kpi-change kpi-{'up' if kpi_val > 7 else 'down'}">
                {'▲ 效率优秀' if kpi_val > 7 else '▼ 需提升'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        kpi_val = filtered_df['投诉量'].sum()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">总投诉量</div>
            <div class="kpi-value">{kpi_val:.0f}件</div>
            <span class="tag tag-{'red' if kpi_val > 15 else ('yellow' if kpi_val > 8 else 'green')}">
                {'⚠ 需关注' if kpi_val > 8 else '✓ 可控'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 异常预警区(置顶)
    st.markdown("### ⚠️ 异常预警列表")

    # 模拟异常数据
    alerts = []
    if filtered_df['TTF超标率_%'].mean() > 20:
        alerts.append(("critical", "TTF严重超标", f"当前超标率{filtered_df['TTF超标率_%'].mean():.1f}%,需立即介入优化流程"))
    if filtered_df['Offer毁约率_%'].mean() > 8:
        alerts.append(("warning", "Offer毁约率偏高", f"当前毁约率{filtered_df['Offer毁约率_%'].mean():.1f}%,建议review薪酬策略"))
    if filtered_df['投诉量'].sum() > 10:
        alerts.append(("warning", "候选人投诉增多", f"本期投诉{filtered_df['投诉量'].sum():.0f}件,需加强服务质量"))
    if filtered_df['预算执行率_%'].mean() > 95:
        alerts.append(("success", "预算控制良好", f"执行率{filtered_df['预算执行率_%'].mean():.1f}%,在合理范围内"))

    for alert_type, title, desc in alerts:
        st.markdown(f"""
        <div class="alert-card alert-{alert_type}">
            <strong>{'🔴' if alert_type=='critical' else ('🟡' if alert_type=='warning' else '🟢')} {title}</strong><br/>
            {desc}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 详细指标
    st.markdown("### 📊 详细运营指标")

    metrics_html = f"""
    <div class="metrics-grid">
        <div class="metric-item">
            <div class="metric-item-label">面试通过率</div>
            <div class="metric-item-value">{filtered_df['面试通过率_%'].mean():.1f}%</div>
        </div>
        <div class="metric-item">
            <div class="metric-item-label">预算执行率</div>
            <div class="metric-item-value">{filtered_df['预算执行率_%'].mean():.1f}%</div>
        </div>
        <div class="metric-item">
            <div class="metric-item-label">漏斗异常次数</div>
            <div class="metric-item-value">{filtered_df['漏斗转化率异常'].sum():.0f}</div>
        </div>
        <div class="metric-item">
            <div class="metric-item-label">团队总人效</div>
            <div class="metric-item-value">{filtered_df['招聘人数'].sum()}</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)

    st.markdown("---")

    # 图表区
    st.markdown("### 📈 管理分析看板")

    col1, col2 = st.columns(2)

    with col1:
        # 部门健康度热力图
        dept_health = filtered_df.groupby('部门').agg({
            'TTF超标率_%': 'mean',
            '面试通过率_%': 'mean',
            '投诉量': 'sum'
        }).reset_index()

        fig = go.Figure(data=go.Heatmap(
            z=[dept_health['TTF超标率_%'].values,
               100-dept_health['面试通过率_%'].values,
               dept_health['投诉量'].values],
            x=dept_health['部门'].values,
            y=['TTF超标率', '面试低通过率', '投诉量'],
            colorscale='RdYlGn_r',
            text=[dept_health['TTF超标率_%'].values,
                  100-dept_health['面试通过率_%'].values,
                  dept_health['投诉量'].values],
            texttemplate='%{text:.1f}',
            textfont={"size": 12}
        ))
        fig.update_layout(
            title='部门招聘健康度热力图',
            font=dict(family=st.session_state['brand_font']),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 招聘顾问人效对比
        recruiter_perf = filtered_df.groupby('招聘顾问')['招聘顾问人效_人'].mean().reset_index()
        fig = px.bar(recruiter_perf, x='招聘顾问', y='招聘顾问人效_人',
                    title='招聘顾问人效对比',
                    color='招聘顾问人效_人',
                    color_continuous_scale=st.session_state['brand_colors'])
        fig.update_layout(
            font=dict(family=st.session_state['brand_font']),
            plot_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    # Offer毁约率趋势
    monthly_renege = filtered_df.groupby('月份')['Offer毁约率_%'].mean().reset_index()
    fig = px.line(monthly_renege, x='月份', y='Offer毁约率_%',
                 title='Offer毁约率趋势监控',
                 markers=True,
                 color_discrete_sequence=['#dc2626'])
    fig.add_hline(y=8, line_dash="dash", line_color="orange", annotation_text="警戒线8%")
    fig.update_layout(
        font=dict(family=st.session_state['brand_font']),
        plot_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# HR 视角: 任务管理器
# ==========================================
else:  # HR (执行层)
    st.markdown("## ✅ 今日任务清单 - 行动导向")

    # 今日关键数据
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_val = filtered_df['待处理候选人数'].iloc[-1] if len(filtered_df) > 0 else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">⏰ 今日待处理</div>
            <div class="kpi-value">{kpi_val:.0f}人</div>
            <span class="tag tag-{'red' if kpi_val > 20 else 'yellow'}">
                {'紧急' if kpi_val > 20 else '正常'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        kpi_val = filtered_df['今日面试数'].iloc[-1] if len(filtered_df) > 0 else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📅 今日面试</div>
            <div class="kpi-value">{kpi_val:.0f}场</div>
            <div class="kpi-change">需确认状态</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        kpi_val = filtered_df['个人转化率_%'].iloc[-1] if len(filtered_df) > 0 else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📊 个人转化率</div>
            <div class="kpi-value">{kpi_val:.1f}%</div>
            <div class="kpi-change kpi-{'up' if kpi_val > 25 else 'down'}">
                {'▲ 推人精准' if kpi_val > 25 else '▼ 需对焦JD'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        kpi_val = filtered_df['月度SLA达成进度_%'].iloc[-1] if len(filtered_df) > 0 else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🎯 本月进度</div>
            <div class="kpi-value">{kpi_val:.0f}%</div>
            <div class="kpi-change kpi-{'up' if kpi_val > 80 else 'down'}">
                {'💪 冲刺目标' if kpi_val < 90 else '✅ 达标'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 今日待办任务(置顶)
    st.markdown("### 📋 今日待办任务 (优先级排序)")

    # 模拟任务列表
    tasks = [
        ("urgent", "紧急", "王候选人 - 已停滞3天", "技术部架构师", "立即联系用人经理催反馈"),
        ("urgent", "紧急", "李候选人 - Offer待确认", "产品部经理", "今日16:00前必须完成谈薪"),
        ("normal", "常规", "张候选人 - 待安排二面", "市场部", "需在明日前安排面试"),
        ("normal", "常规", "刘候选人 - 初筛通过", "销售部", "推荐给用人经理review"),
        ("normal", "常规", "陈候选人 - 背调进行中", "技术部", "跟进背调公司进度"),
    ]

    for task_type, priority, candidate, dept, action in tasks:
        st.markdown(f"""
        <div class="task-card {'task-urgent' if task_type=='urgent' else ''}">
            <div class="task-title">
                <span class="tag tag-{'red' if task_type=='urgent' else 'blue'}">{priority}</span>
                {candidate}
            </div>
            <div class="task-meta">
                📁 {dept} | 🎯 {action}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 详细指标
    st.markdown("### 📊 个人绩效指标")

    metrics_html = f"""
    <div class="metrics-grid">
        <div class="metric-item">
            <div class="metric-item-label">本月已入职</div>
            <div class="metric-item-value">{filtered_df['招聘人数'].sum()}</div>
        </div>
        <div class="metric-item">
            <div class="metric-item-label">流程停滞天数</div>
            <div class="metric-item-value">{filtered_df['流程停滞天数'].mean():.1f}天</div>
        </div>
        <div class="metric-item">
            <div class="metric-item-label">个人转化率</div>
            <div class="metric-item-value">{filtered_df['个人转化率_%'].mean():.1f}%</div>
        </div>
        <div class="metric-item">
            <div class="metric-item-label">SLA达成进度</div>
            <div class="metric-item-value">{filtered_df['月度SLA达成进度_%'].mean():.0f}%</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)

    st.markdown("---")

    # 图表区
    st.markdown("### 📈 个人绩效看板")

    col1, col2 = st.columns(2)

    with col1:
        # SLA达成进度
        monthly_progress = filtered_df.groupby('月份')['月度SLA达成进度_%'].mean().reset_index()
        fig = px.line(monthly_progress, x='月份', y='月度SLA达成进度_%',
                     title='月度SLA达成进度趋势',
                     markers=True,
                     color_discrete_sequence=[st.session_state['primary_color']])
        fig.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="目标100%")
        fig.update_layout(
            font=dict(family=st.session_state['brand_font']),
            plot_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 个人转化率趋势
        monthly_conv = filtered_df.groupby('月份')['个人转化率_%'].mean().reset_index()
        fig = px.area(monthly_conv, x='月份', y='个人转化率_%',
                     title='个人简历转化率趋势',
                     color_discrete_sequence=['#0891b2'])
        fig.update_layout(
            font=dict(family=st.session_state['brand_font']),
            plot_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    # 待处理候选人趋势
    monthly_pending = filtered_df.groupby('月份')['待处理候选人数'].mean().reset_index()
    fig = px.bar(monthly_pending, x='月份', y='待处理候选人数',
                title='待处理候选人数趋势',
                color='待处理候选人数',
                color_continuous_scale='Reds')
    fig.update_layout(
        font=dict(family=st.session_state['brand_font']),
        plot_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 页脚
# ==========================================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #64748b; padding: 1rem; font-size: 0.875rem;'>
    <strong>招聘数据驾驶舱 v3.0 Pro</strong> | Powered by Advanced Analytics<br/>
    最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 当前角色: {role_name_cn}
</div>
""", unsafe_allow_html=True)
