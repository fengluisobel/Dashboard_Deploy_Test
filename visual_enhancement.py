"""
招聘数据驾驶舱 v3.0 Pro Ultra - 视觉增强模块
Visual Enhancement Module

提供超现代化的视觉效果,包括:
- 毛玻璃质感(Glassmorphism)
- 流畅动画效果
- 动态渐变背景
- 精致交互反馈

完全不改变任何业务逻辑和功能,纯视觉增强
"""

import streamlit as st


def inject_ultra_modern_css(primary_color='#667eea'):
    """
    注入超现代化CSS样式

    特性:
    - 毛玻璃卡片效果(Glassmorphism)
    - 动态渐变背景
    - 流畅动画过渡
    - 多层阴影系统
    - 渐变文字标题
    - 深色侧边栏
    - 自定义滚动条
    - 悬浮效果

    Parameters:
    -----------
    primary_color : str
        主题色(十六进制颜色代码)
    """

    # 从主色提取RGB值用于rgba
    r = int(primary_color[1:3], 16)
    g = int(primary_color[3:5], 16)
    b = int(primary_color[5:7], 16)

    css = f"""
    <style>
    /* ========================================
       Google Fonts 引入
       ======================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ========================================
       全局样式重置
       ======================================== */
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    code, pre {{
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
    }}

    /* ========================================
       动态渐变背景
       ======================================== */
    .stApp {{
        background: linear-gradient(135deg,
            {primary_color}08 0%,
            #f8f9fa 25%,
            {primary_color}05 50%,
            #ffffff 75%,
            {primary_color}08 100%
        );
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }}

    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* ========================================
       毛玻璃卡片效果 (Glassmorphism)
       ======================================== */
    .kpi-card,
    .css-1r6slb0,
    .css-12oz5g7,
    [data-testid="stMetricValue"],
    [data-testid="metric-container"] {{
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.06),
            0 2px 8px rgba(0, 0, 0, 0.04),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        padding: 1.5rem;
    }}

    /* 卡片悬浮效果 */
    .kpi-card:hover,
    .css-1r6slb0:hover,
    .css-12oz5g7:hover,
    [data-testid="metric-container"]:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow:
            0 20px 60px rgba({r}, {g}, {b}, 0.2),
            0 8px 24px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 1);
        border: 1px solid rgba({r}, {g}, {b}, 0.15);
    }}

    /* ========================================
       标题渐变文字
       ======================================== */
    h1 {{
        background: linear-gradient(135deg, {primary_color} 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        margin-bottom: 1rem !important;
    }}

    h2 {{
        background: linear-gradient(135deg, {primary_color} 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }}

    h3 {{
        color: {primary_color};
        font-weight: 600 !important;
    }}

    /* ========================================
       按钮增强效果
       ======================================== */
    .stButton > button {{
        background: linear-gradient(135deg, {primary_color} 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 16px rgba({r}, {g}, {b}, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}

    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg,
            transparent,
            rgba(255, 255, 255, 0.3),
            transparent
        );
        transition: left 0.5s;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 8px 24px rgba({r}, {g}, {b}, 0.4);
    }}

    .stButton > button:hover::before {{
        left: 100%;
    }}

    .stButton > button:active {{
        transform: translateY(0) scale(0.98);
        box-shadow: 0 2px 8px rgba({r}, {g}, {b}, 0.3);
    }}

    /* ========================================
       深色渐变侧边栏
       ======================================== */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg,
            #2d1b69 0%,
            #3e2a7e 50%,
            #4a3586 100%
        );
        color: white;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
    }}

    [data-testid="stSidebar"] * {{
        color: white !important;
    }}

    [data-testid="stSidebar"] .stRadio > label,
    [data-testid="stSidebar"] .stSelectbox > label,
    [data-testid="stSidebar"] .stNumberInput > label {{
        color: rgba(255, 255, 255, 0.95) !important;
        font-weight: 500;
    }}

    [data-testid="stSidebar"] hr {{
        border-color: rgba(255, 255, 255, 0.2) !important;
        margin: 1.5rem 0;
    }}

    /* 侧边栏输入框样式 */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select {{
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        color: white !important;
        padding: 0.5rem !important;
    }}

    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] select:focus {{
        border-color: rgba(255, 255, 255, 0.6) !important;
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1) !important;
    }}

    /* ========================================
       表格美化
       ======================================== */
    .dataframe {{
        border-radius: 12px !important;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06) !important;
    }}

    .dataframe thead tr {{
        background: linear-gradient(135deg, {primary_color} 0%, #764ba2 100%) !important;
    }}

    .dataframe thead th {{
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        text-align: left !important;
    }}

    .dataframe tbody tr {{
        transition: all 0.2s ease;
    }}

    .dataframe tbody tr:hover {{
        background-color: rgba({r}, {g}, {b}, 0.08) !important;
        transform: scale(1.01);
    }}

    .dataframe tbody td {{
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
    }}

    /* ========================================
       Plotly图表容器美化
       ======================================== */
    .js-plotly-plot {{
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 1rem;
    }}

    /* ========================================
       信息框美化
       ======================================== */
    .stAlert {{
        border-radius: 12px !important;
        border-left: 4px solid {primary_color} !important;
        background: rgba({r}, {g}, {b}, 0.05) !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }}

    /* Success 信息框 */
    [data-baseweb="notification"] {{
        border-radius: 12px !important;
        background: rgba(40, 167, 69, 0.1) !important;
        backdrop-filter: blur(10px);
        border-left: 4px solid #28a745 !important;
    }}

    /* Warning 信息框 */
    .stWarning {{
        border-radius: 12px !important;
        background: rgba(255, 193, 7, 0.1) !important;
        backdrop-filter: blur(10px);
        border-left: 4px solid #ffc107 !important;
    }}

    /* Error 信息框 */
    .stError {{
        border-radius: 12px !important;
        background: rgba(220, 53, 69, 0.1) !important;
        backdrop-filter: blur(10px);
        border-left: 4px solid #dc3545 !important;
    }}

    /* Info 信息框 */
    .stInfo {{
        border-radius: 12px !important;
        background: rgba({r}, {g}, {b}, 0.1) !important;
        backdrop-filter: blur(10px);
        border-left: 4px solid {primary_color} !important;
    }}

    /* ========================================
       展开器美化
       ======================================== */
    .streamlit-expanderHeader {{
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        border: 1px solid rgba({r}, {g}, {b}, 0.1);
        font-weight: 600;
        padding: 1rem !important;
        transition: all 0.3s ease;
    }}

    .streamlit-expanderHeader:hover {{
        background: rgba({r}, {g}, {b}, 0.05) !important;
        border-color: rgba({r}, {g}, {b}, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    }}

    .streamlit-expanderContent {{
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px);
        border-radius: 0 0 12px 12px !important;
        padding: 1rem !important;
    }}

    /* ========================================
       选择框美化
       ======================================== */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        border-radius: 12px !important;
        border: 1px solid rgba({r}, {g}, {b}, 0.2) !important;
        background: rgba(255, 255, 255, 0.9) !important;
        transition: all 0.3s ease;
    }}

    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {{
        border-color: {primary_color} !important;
        box-shadow: 0 0 0 3px rgba({r}, {g}, {b}, 0.1) !important;
    }}

    /* ========================================
       输入框美化
       ======================================== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {{
        border-radius: 12px !important;
        border: 1px solid rgba({r}, {g}, {b}, 0.2) !important;
        background: rgba(255, 255, 255, 0.9) !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease;
    }}

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: {primary_color} !important;
        box-shadow: 0 0 0 3px rgba({r}, {g}, {b}, 0.1) !important;
    }}

    /* ========================================
       自定义滚动条
       ======================================== */
    ::-webkit-scrollbar {{
        width: 12px;
        height: 12px;
    }}

    ::-webkit-scrollbar-track {{
        background: rgba(0, 0, 0, 0.05);
        border-radius: 10px;
    }}

    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, {primary_color} 0%, #764ba2 100%);
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.5);
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, #764ba2 0%, {primary_color} 100%);
    }}

    /* ========================================
       分隔线美化
       ======================================== */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg,
            transparent 0%,
            {primary_color}40 50%,
            transparent 100%
        );
        margin: 2rem 0;
    }}

    /* ========================================
       代码块美化
       ======================================== */
    code {{
        background: rgba({r}, {g}, {b}, 0.08) !important;
        color: {primary_color} !important;
        padding: 0.2rem 0.5rem !important;
        border-radius: 6px !important;
        font-size: 0.9em !important;
        border: 1px solid rgba({r}, {g}, {b}, 0.15);
    }}

    pre {{
        background: rgba(0, 0, 0, 0.02) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        padding: 1rem !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
    }}

    /* ========================================
       文件上传区域美化
       ======================================== */
    [data-testid="stFileUploader"] {{
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border: 2px dashed rgba({r}, {g}, {b}, 0.3) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        transition: all 0.3s ease;
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: {primary_color} !important;
        background: rgba({r}, {g}, {b}, 0.05) !important;
        transform: scale(1.01);
    }}

    /* ========================================
       标签页美化
       ======================================== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 0.5rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {primary_color} 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba({r}, {g}, {b}, 0.3);
    }}

    /* ========================================
       进度条美化
       ======================================== */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {primary_color} 0%, #764ba2 100%);
        border-radius: 10px;
    }}

    /* ========================================
       日期选择器美化
       ======================================== */
    .stDateInput > div > div > input {{
        border-radius: 12px !important;
        border: 1px solid rgba({r}, {g}, {b}, 0.2) !important;
        background: rgba(255, 255, 255, 0.9) !important;
        padding: 0.75rem 1rem !important;
    }}

    /* ========================================
       滑块美化
       ======================================== */
    .stSlider > div > div > div > div {{
        background: linear-gradient(90deg, {primary_color} 0%, #764ba2 100%) !important;
    }}

    /* ========================================
       复选框和单选框美化
       ======================================== */
    .stCheckbox > label > div {{
        border-radius: 6px;
        border: 2px solid rgba({r}, {g}, {b}, 0.3);
    }}

    .stRadio > label > div {{
        border-radius: 50%;
        border: 2px solid rgba({r}, {g}, {b}, 0.3);
    }}

    /* ========================================
       响应式设计
       ======================================== */
    @media (max-width: 768px) {{
        .kpi-card {{
            padding: 1rem !important;
        }}

        h1 {{
            font-size: 1.5rem !important;
        }}

        h2 {{
            font-size: 1.25rem !important;
        }}

        .stButton > button {{
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
        }}
    }}

    /* ========================================
       打印样式优化
       ======================================== */
    @media print {{
        .stApp {{
            background: white !important;
        }}

        .kpi-card,
        .css-1r6slb0,
        .css-12oz5g7 {{
            box-shadow: none !important;
            border: 1px solid #ddd !important;
        }}

        [data-testid="stSidebar"] {{
            display: none !important;
        }}
    }}

    /* ========================================
       加载动画优化
       ======================================== */
    .stSpinner > div {{
        border-color: {primary_color} transparent transparent transparent !important;
    }}

    /* ========================================
       工具提示美化
       ======================================== */
    [data-testid="stTooltipIcon"] {{
        color: {primary_color} !important;
    }}

    /* ========================================
       下拉菜单美化
       ======================================== */
    [role="listbox"] {{
        border-radius: 12px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
    }}

    [role="option"]:hover {{
        background: rgba({r}, {g}, {b}, 0.1) !important;
    }}

    /* ========================================
       自定义KPI卡片类(供手动添加)
       ======================================== */
    .kpi-card-custom {{
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px) saturate(180%);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.06),
            0 2px 8px rgba(0, 0, 0, 0.04),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        padding: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .kpi-card-custom:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow:
            0 20px 60px rgba({r}, {g}, {b}, 0.2),
            0 8px 24px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 1);
    }}

    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


def render_enhanced_header(title, subtitle, icon="📊", gradient_colors=None):
    """
    渲染增强的页面标题

    Parameters:
    -----------
    title : str
        主标题
    subtitle : str
        副标题
    icon : str
        图标emoji
    gradient_colors : tuple
        渐变色元组 (color1, color2),默认使用主题色
    """

    if gradient_colors is None:
        from brand_color_system import get_primary_color
        primary = get_primary_color()
        gradient_colors = (primary, '#764ba2')

    color1, color2 = gradient_colors

    html = f"""
    <div style="background: linear-gradient(135deg, {color1} 0%, {color2} 100%);
                padding: 2rem;
                border-radius: 16px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 24px rgba(0,0,0,0.12);
                backdrop-filter: blur(10px);">
        <h1 style="color: white; margin: 0; font-size: 2rem; font-weight: 800;">
            {icon} {title}
        </h1>
        <p style="color: white; opacity: 0.95; margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: 500;">
            {subtitle}
        </p>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def render_stats_card(label, value, delta=None, delta_color="normal", icon="📈"):
    """
    渲染增强的统计卡片

    Parameters:
    -----------
    label : str
        标签文本
    value : str
        主要数值
    delta : str
        变化值(可选)
    delta_color : str
        变化值颜色 ("normal", "inverse", "off")
    icon : str
        图标emoji
    """

    from brand_color_system import get_primary_color
    primary = get_primary_color()

    # 提取RGB
    r = int(primary[1:3], 16)
    g = int(primary[3:5], 16)
    b = int(primary[5:7], 16)

    # Delta颜色
    if delta:
        if delta_color == "normal":
            # 正数绿色,负数红色
            if delta.startswith('+') or delta.startswith('▲'):
                delta_color_hex = '#28a745'
            else:
                delta_color_hex = '#dc3545'
        elif delta_color == "inverse":
            # 正数红色,负数绿色
            if delta.startswith('+') or delta.startswith('▲'):
                delta_color_hex = '#dc3545'
            else:
                delta_color_hex = '#28a745'
        else:
            delta_color_hex = '#666'

        delta_html = f"""
        <div style="font-size: 0.9rem; color: {delta_color_hex}; margin-top: 0.5rem; font-weight: 600;">
            {delta}
        </div>
        """
    else:
        delta_html = ""

    html = f"""
    <div class="kpi-card-custom" style="text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">
            {icon}
        </div>
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.75rem; font-weight: 500;">
            {label}
        </div>
        <div style="font-size: 2.5rem; font-weight: 800; color: {primary}; margin-bottom: 0.25rem;">
            {value}
        </div>
        {delta_html}
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def render_section_divider(text=""):
    """
    渲染增强的章节分隔符

    Parameters:
    -----------
    text : str
        分隔符文本(可选)
    """

    from brand_color_system import get_primary_color
    primary = get_primary_color()

    if text:
        html = f"""
        <div style="position: relative; text-align: center; margin: 2rem 0;">
            <hr style="border: none; height: 2px; background: linear-gradient(90deg, transparent 0%, {primary}40 50%, transparent 100%);">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                        background: white; padding: 0 1rem; font-weight: 600; color: {primary};">
                {text}
            </div>
        </div>
        """
    else:
        html = f"""
        <hr style="border: none; height: 2px; background: linear-gradient(90deg, transparent 0%, {primary}40 50%, transparent 100%); margin: 2rem 0;">
        """

    st.markdown(html, unsafe_allow_html=True)
