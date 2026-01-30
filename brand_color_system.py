"""
品牌色系统模块 v3.0 Pro
完整集成 color_settting.py 的所有功能
支持图片上传、颜色提取、色阶生成、全局主题应用
"""

import streamlit as st
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import matplotlib.colors as mcolors
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 颜色提取与处理核心算法
# ==========================================

def extract_colors_from_image(image, num_colors=6):
    """
    使用 K-Means 算法从上传的图片中提取主色调

    Parameters:
    -----------
    image : PIL.Image
        上传的品牌图片 (Logo/PPT截图)
    num_colors : int
        提取的颜色数量，默认6种

    Returns:
    --------
    list of str
        Hex格式的颜色列表，例如 ['#FF5733', '#33FF57', ...]
    """
    # 调整图片大小以加快处理速度 (避免大图片导致计算慢)
    img = image.resize((150, 150))
    img_array = np.array(img)

    # 处理 PNG 透明通道 (RGBA -> RGB)
    if img_array.shape[-1] == 4:
        img_array = img_array[:, :, :3]

    # 将图片数据重塑为像素列表 (每行是一个像素的 R, G, B 值)
    pixels = img_array.reshape(-1, 3)

    # 使用 K-Means 聚类提取主色调
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)

    # 转换为 Hex 格式
    hex_colors = ['#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2]) for c in colors]

    return hex_colors


def generate_palette(base_color, n=10):
    """
    基于单一主色生成色阶（从浅到深的渐变）

    Parameters:
    -----------
    base_color : str
        主色的 Hex 或颜色名称，例如 '#667eea' 或 'blue'
    n : int
        生成的色阶数量，默认10级

    Returns:
    --------
    list of str
        色阶 Hex 列表，例如 ['#f0f2f6', ..., '#667eea', ..., '#000000']
    """
    try:
        # 使用 matplotlib 的线性分段颜色映射
        # 从浅灰 -> 主色 -> 深色
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "custom",
            ["#f0f2f6", base_color, "#1a1a1a"]
        )

        # 生成 n 个均匀分布的颜色
        palette = [mcolors.to_hex(cmap(i/n)) for i in range(n)]

        return palette

    except Exception as e:
        # 如果失败，回退到 Plotly 默认配色
        print(f"色阶生成失败: {e}, 使用默认配色")
        return px.colors.qualitative.Plotly[:n]


def generate_complementary_palette(base_colors, n_per_color=2):
    """
    基于多个提取的颜色生成混合配色方案

    Parameters:
    -----------
    base_colors : list of str
        提取的主色列表
    n_per_color : int
        每个主色生成的渐变数量

    Returns:
    --------
    list of str
        混合配色方案
    """
    palette = []

    for color in base_colors:
        try:
            # 为每个主色生成浅色和深色变体
            rgb = mcolors.to_rgb(color)

            # 浅色变体 (混合白色)
            light_rgb = tuple(x + (1.0 - x) * 0.5 for x in rgb)
            palette.append(mcolors.to_hex(light_rgb))

            # 原色
            palette.append(color)

            # 深色变体 (降低亮度)
            if n_per_color > 2:
                dark_rgb = tuple(x * 0.6 for x in rgb)
                palette.append(mcolors.to_hex(dark_rgb))

        except:
            palette.append(color)

    return palette


def inject_custom_css(font_family, primary_color, background_color="#FFFFFF", text_color="#1a1a1a"):
    """
    向页面注入全局 CSS 以修改字体、配色和布局

    Parameters:
    -----------
    font_family : str
        字体名称，例如 'Inter', 'Roboto'
    primary_color : str
        主色 Hex
    background_color : str
        背景色 Hex
    text_color : str
        文字颜色 Hex
    """
    css = f"""
    <style>
        /* ==========================================
           全局字体设置
           ========================================== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: '{font_family}', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: {text_color};
        }}

        /* ==========================================
           页面背景
           ========================================== */
        .stApp {{
            background: linear-gradient(135deg, {background_color} 0%, #f8f9fa 100%);
        }}

        /* ==========================================
           标题样式 - 科技咨询风格
           ========================================== */
        h1, h2, h3 {{
            font-family: '{font_family}', 'Inter', serif !important;
            color: {text_color} !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
        }}

        h1 {{
            font-size: 2.5rem !important;
            margin-bottom: 1rem !important;
        }}

        h2 {{
            font-size: 1.75rem !important;
            margin-top: 2rem !important;
            margin-bottom: 0.75rem !important;
        }}

        h3 {{
            font-size: 1.25rem !important;
            margin-top: 1.5rem !important;
            color: {primary_color} !important;
        }}

        /* ==========================================
           KPI 卡片样式
           ========================================== */
        .kpi-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            border-left: 4px solid {primary_color};
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }}

        /* ==========================================
           度量指标卡片
           ========================================== */
        .metric-card {{
            background: linear-gradient(135deg, {primary_color}15 0%, {primary_color}05 100%);
            border: 1px solid {primary_color}30;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }}

        /* ==========================================
           侧边栏样式
           ========================================== */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {primary_color}10 0%, #ffffff 100%);
            border-right: 1px solid {primary_color}20;
        }}
        
        /* 侧边栏深色主题对比度修复 */
        section[data-testid="stSidebar"] .stButton > button {{
            background: {primary_color} !important;
            color: white !important;
            border: none !important;
            font-weight: 600 !important;
        }}
        
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background: {primary_color}dd !important;
            color: white !important;
        }}
        
        /* 侧边栏输入框和选择器文字对比度修复 */
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] select,
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stDateInput label,
        section[data-testid="stSidebar"] .stMultiSelect label,
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stTextInput label {{
            color: inherit !important;
        }}
        
        /* 侧边栏内的文本输入框背景和文字 */
        section[data-testid="stSidebar"] .stTextInput input,
        section[data-testid="stSidebar"] .stDateInput input,
        section[data-testid="stSidebar"] .stNumberInput input {{
            background-color: white !important;
            color: #1a1a1a !important;
            border: 1px solid #ddd !important;
        }}
        
        /* 侧边栏下拉选择器 */
        section[data-testid="stSidebar"] .stSelectbox > div > div {{
            background-color: white !important;
            color: #1a1a1a !important;
        }}
        
        /* 侧边栏多选框 */
        section[data-testid="stSidebar"] .stMultiSelect > div > div {{
            background-color: white !important;
            color: #1a1a1a !important;
        }}

        /* ==========================================
           按钮样式
           ========================================== */
        .stButton > button {{
            background: linear-gradient(135deg, {primary_color} 0%, {primary_color}dd 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px {primary_color}40;
        }}

        /* ==========================================
           选择器样式
           ========================================== */
        .stSelectbox, .stMultiSelect {{
            border-radius: 8px;
        }}

        /* ==========================================
           数据表格样式
           ========================================== */
        .dataframe {{
            border: 1px solid {primary_color}20 !important;
            border-radius: 8px !important;
        }}

        /* ==========================================
           分隔线
           ========================================== */
        hr {{
            border: none;
            border-top: 2px solid {primary_color}30;
            margin: 2rem 0;
        }}

        /* ==========================================
           警告框样式
           ========================================== */
        .stAlert {{
            border-radius: 8px;
            border-left: 4px solid {primary_color};
        }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


# ==========================================
# 2. 品牌色系统初始化
# ==========================================

import json
import os

# 品牌配置文件路径
BRAND_CONFIG_FILE = "brand_config.json"

def load_brand_config():
    """
    从JSON文件加载品牌配置
    """
    if os.path.exists(BRAND_CONFIG_FILE):
        try:
            with open(BRAND_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_brand_config():
    """
    保存品牌配置到JSON文件
    """
    config = {
        'brand_colors': st.session_state.get('brand_colors', []),
        'primary_color': st.session_state.get('primary_color', '#667eea'),
        'brand_font': st.session_state.get('brand_font', 'Inter'),
        'is_brand_confirmed': st.session_state.get('is_brand_confirmed', False)
    }
    
    try:
        with open(BRAND_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存品牌配置失败: {e}")

def initialize_brand_system():
    """
    初始化品牌色系统的 session_state
    优先从保存的JSON文件加载配置
    """
    # 尝试从文件加载已保存的配置
    saved_config = load_brand_config()
    
    if 'brand_colors' not in st.session_state:
        if saved_config and 'brand_colors' in saved_config:
            st.session_state['brand_colors'] = saved_config['brand_colors']
        else:
            # 默认配色：科技蓝紫渐变
            st.session_state['brand_colors'] = [
                '#667eea', '#764ba2', '#f093fb', '#4facfe',
                '#00f2fe', '#43e97b', '#38f9d7', '#fa709a',
                '#fee140', '#30cfd0'
            ]

    if 'brand_font' not in st.session_state:
        if saved_config and 'brand_font' in saved_config:
            st.session_state['brand_font'] = saved_config['brand_font']
        else:
            st.session_state['brand_font'] = "Inter"

    if 'primary_color' not in st.session_state:
        if saved_config and 'primary_color' in saved_config:
            st.session_state['primary_color'] = saved_config['primary_color']
        else:
            st.session_state['primary_color'] = "#667eea"

    if 'is_brand_confirmed' not in st.session_state:
        if saved_config and 'is_brand_confirmed' in saved_config:
            st.session_state['is_brand_confirmed'] = saved_config['is_brand_confirmed']
        else:
            st.session_state['is_brand_confirmed'] = False

    if 'extracted_colors' not in st.session_state:
        st.session_state['extracted_colors'] = []


# ==========================================
# 3. 品牌色配置界面
# ==========================================

def render_brand_color_configurator():
    """
    渲染品牌色配置界面 (在侧边栏)
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 品牌风格定制")

    # 上传图片
    st.sidebar.info("上传您的品牌 Logo 或 PPT 截图，系统将自动提取配色")

    uploaded_file = st.sidebar.file_uploader(
        "上传品牌图片 (JPG/PNG)",
        type=['jpg', 'png', 'jpeg'],
        key="brand_image_uploader"
    )

    # 如果上传了图片
    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        # 显示预览
        st.sidebar.image(image, caption="品牌素材预览", use_container_width=True)

        # 提取颜色按钮
        if st.sidebar.button("🔍 提取品牌基因", type="primary"):
            with st.spinner("正在分析像素并提取主色调..."):
                extracted = extract_colors_from_image(image, num_colors=6)
                st.session_state['extracted_colors'] = extracted
                st.session_state['is_brand_confirmed'] = False
                st.sidebar.success("✅ 提取成功！请在下方配置")

    # 如果已经提取了颜色但还没确认
    if st.session_state['extracted_colors'] and not st.session_state['is_brand_confirmed']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ 配色方案确认")

        # 显示提取的颜色
        st.sidebar.write("**提取到的主色调：**")

        # 使用 columns 显示颜色选择器
        cols = st.sidebar.columns(3)
        for idx, color in enumerate(st.session_state['extracted_colors']):
            col_idx = idx % 3
            with cols[col_idx]:
                new_color = st.color_picker(
                    f"色{idx+1}",
                    color,
                    key=f"brand_color_picker_{idx}"
                )
                # 更新颜色
                st.session_state['extracted_colors'][idx] = new_color

        # 主色选择
        st.sidebar.write("**选择主色：**")
        primary_idx = st.sidebar.selectbox(
            "哪个颜色作为主色？",
            range(len(st.session_state['extracted_colors'])),
            format_func=lambda x: f"颜色 {x+1}",
            key="primary_color_selector"
        )

        st.session_state['primary_color'] = st.session_state['extracted_colors'][primary_idx]

        # 配色方案类型
        st.sidebar.write("**配色方案：**")
        scheme_type = st.sidebar.radio(
            "选择图表配色逻辑",
            ["单色渐变 (专业/极简)", "提取色混合 (多彩/活力)", "互补色方案 (对比/高端)"],
            key="scheme_type_selector"
        )

        # 生成最终配色
        final_palette = []

        if scheme_type == "单色渐变 (专业/极简)":
            final_palette = generate_palette(st.session_state['primary_color'], n=10)

        elif scheme_type == "提取色混合 (多彩/活力)":
            final_palette = st.session_state['extracted_colors']

        else:  # 互补色方案
            final_palette = generate_complementary_palette(
                st.session_state['extracted_colors'][:3],
                n_per_color=3
            )

        # 预览色条
        st.sidebar.write("**生成的图表色阶预览：**")

        # 创建预览图
        fig_preview = go.Figure()

        for idx, color in enumerate(final_palette):
            fig_preview.add_trace(go.Bar(
                x=[idx],
                y=[1],
                marker_color=color,
                showlegend=False,
                hovertemplate=f'颜色: {color}<extra></extra>'
            ))

        fig_preview.update_layout(
            height=80,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_visible=False,
            yaxis_visible=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            bargap=0.1
        )

        st.sidebar.plotly_chart(fig_preview, use_container_width=True)

        # 字体选择
        st.sidebar.write("**字体风格：**")
        font_choice = st.sidebar.selectbox(
            "选择应用字体",
            ["Inter", "Roboto", "Open Sans", "Lato", "Montserrat"],
            key="font_selector"
        )

        # 确认按钮
        if st.sidebar.button("✅ 确认并应用该品牌风格", type="primary", key="confirm_brand"):
            st.session_state['brand_colors'] = final_palette
            st.session_state['brand_font'] = font_choice
            st.session_state['is_brand_confirmed'] = True
            st.rerun()

    # 如果已经确认，显示重置按钮
    if st.session_state['is_brand_confirmed']:
        st.sidebar.success("✅ 品牌风格已应用")

        # 显示当前配色
        st.sidebar.write("**当前品牌色：**")
        preview_cols = st.sidebar.columns(5)
        for idx, color in enumerate(st.session_state['brand_colors'][:5]):
            with preview_cols[idx]:
                st.markdown(
                    f'<div style="background-color:{color};height:30px;border-radius:4px;"></div>',
                    unsafe_allow_html=True
                )

        if st.sidebar.button("🔄 重置品牌风格", key="reset_brand"):
            st.session_state['is_brand_confirmed'] = False
            st.session_state['extracted_colors'] = []
            st.session_state['brand_colors'] = [
                '#667eea', '#764ba2', '#f093fb', '#4facfe',
                '#00f2fe', '#43e97b', '#38f9d7', '#fa709a',
                '#fee140', '#30cfd0'
            ]
            st.session_state['primary_color'] = "#667eea"
            st.session_state['brand_font'] = "Inter"
            st.rerun()


# ==========================================
# 4. 获取当前品牌色
# ==========================================

def get_brand_colors():
    """
    获取当前的品牌配色方案

    Returns:
    --------
    list of str
        当前的品牌色列表
    """
    initialize_brand_system()
    return st.session_state['brand_colors']


def get_primary_color():
    """
    获取当前的主色

    Returns:
    --------
    str
        主色 Hex
    """
    initialize_brand_system()
    return st.session_state['primary_color']


def get_brand_font():
    """
    获取当前的品牌字体

    Returns:
    --------
    str
        字体名称
    """
    initialize_brand_system()
    return st.session_state['brand_font']


def apply_brand_theme():
    """
    应用品牌主题 (CSS + 字体)
    在主程序开始时调用
    """
    initialize_brand_system()

    inject_custom_css(
        font_family=st.session_state['brand_font'],
        primary_color=st.session_state['primary_color'],
        background_color="#FFFFFF",
        text_color="#1a1a1a"
    )


# ==========================================
# 5. 品牌色配置界面 (内联版本 - 用于右侧面板)
# ==========================================

def render_brand_color_configurator_inline():
    """
    渲染品牌色配置界面 (内联版本，用于主内容区右侧)
    使用 st.expander 实现可折叠面板
    """
    import os
    
    # 自定义Logo保存路径
    custom_logo_path = "logo/custom_logo.png"
    
    with st.expander("🎨 品牌风格定制 (全局设置)", expanded=False):
        
        # ==========================================
        # Logo 上传区域
        # ==========================================
        st.subheader("🖼️ Logo 设置")
        
        logo_file = st.file_uploader(
            "上传自定义 Logo (JPG/PNG)",
            type=['jpg', 'png', 'jpeg'],
            key="logo_uploader_inline"
        )
        
        if logo_file is not None:
            # 保存到本地文件
            try:
                # 确保logo目录存在
                os.makedirs("logo", exist_ok=True)
                
                # 保存上传的文件
                with open(custom_logo_path, "wb") as f:
                    f.write(logo_file.getbuffer())
                
                st.session_state['custom_logo_path'] = custom_logo_path
                st.success("✅ Logo 已保存并更新！")
                st.image(custom_logo_path, caption="新 Logo 预览", width=150)
            except Exception as e:
                st.error(f"保存Logo失败: {e}")
        
        # 检查是否存在自定义Logo文件
        if os.path.exists(custom_logo_path):
            st.info("📌 当前使用自定义 Logo")
            st.image(custom_logo_path, width=100)
            
            if st.button("🔄 恢复默认 Logo", key="reset_logo"):
                try:
                    os.remove(custom_logo_path)
                    if 'custom_logo_path' in st.session_state:
                        del st.session_state['custom_logo_path']
                    st.success("✅ 已恢复默认 Logo")
                    st.rerun()
                except Exception as e:
                    st.error(f"删除失败: {e}")
        
        st.markdown("---")
        
        # ==========================================
        # 品牌色提取区域
        # ==========================================
        st.subheader("🎨 品牌配色")
        st.info("上传您的品牌 Logo 或 PPT 截图，系统将自动提取配色")

        uploaded_file = st.file_uploader(
            "上传品牌图片提取配色 (JPG/PNG)",
            type=['jpg', 'png', 'jpeg'],
            key="brand_image_uploader_inline"
        )

        # 如果上传了图片
        if uploaded_file is not None:
            image = Image.open(uploaded_file)

            # 显示预览
            st.image(image, caption="品牌素材预览", use_container_width=True)

            # 提取颜色按钮
            if st.button("🔍 提取品牌基因", type="primary", key="extract_brand_inline"):
                with st.spinner("正在分析像素并提取主色调..."):
                    extracted = extract_colors_from_image(image, num_colors=6)
                    st.session_state['extracted_colors'] = extracted
                    st.session_state['is_brand_confirmed'] = False
                    st.success("✅ 提取成功！请在下方配置")

        # 如果已经提取了颜色但还没确认
        if st.session_state['extracted_colors'] and not st.session_state['is_brand_confirmed']:
            st.markdown("---")
            st.subheader("🛠️ 配色方案确认")

            # 显示提取的颜色
            st.write("**提取到的主色调：**")

            # 使用 columns 显示颜色选择器
            cols = st.columns(3)
            for idx, color in enumerate(st.session_state['extracted_colors']):
                col_idx = idx % 3
                with cols[col_idx]:
                    new_color = st.color_picker(
                        f"色{idx+1}",
                        color,
                        key=f"brand_color_picker_inline_{idx}"
                    )
                    # 更新颜色
                    st.session_state['extracted_colors'][idx] = new_color

            # 主色选择
            st.write("**选择主色：**")
            primary_idx = st.selectbox(
                "哪个颜色作为主色？",
                range(len(st.session_state['extracted_colors'])),
                format_func=lambda x: f"颜色 {x+1}",
                key="primary_color_selector_inline"
            )

            st.session_state['primary_color'] = st.session_state['extracted_colors'][primary_idx]

            # 配色方案类型
            st.write("**配色方案：**")
            scheme_type = st.radio(
                "选择图表配色逻辑",
                ["单色渐变 (专业/极简)", "提取色混合 (多彩/活力)", "互补色方案 (对比/高端)"],
                key="scheme_type_selector_inline"
            )

            # 生成最终配色
            final_palette = []

            if scheme_type == "单色渐变 (专业/极简)":
                final_palette = generate_palette(st.session_state['primary_color'], n=10)

            elif scheme_type == "提取色混合 (多彩/活力)":
                final_palette = st.session_state['extracted_colors']

            else:  # 互补色方案
                final_palette = generate_complementary_palette(
                    st.session_state['extracted_colors'][:3],
                    n_per_color=3
                )

            # 预览色条
            st.write("**生成的图表色阶预览：**")

            # 创建预览图
            fig_preview = go.Figure()

            for idx, color in enumerate(final_palette):
                fig_preview.add_trace(go.Bar(
                    x=[idx],
                    y=[1],
                    marker_color=color,
                    showlegend=False,
                    hovertemplate=f'颜色: {color}<extra></extra>'
                ))

            fig_preview.update_layout(
                height=80,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis_visible=False,
                yaxis_visible=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                bargap=0.1
            )

            st.plotly_chart(fig_preview, use_container_width=True)

            # 字体选择
            st.write("**字体风格：**")
            font_choice = st.selectbox(
                "选择应用字体",
                ["Inter", "Roboto", "Open Sans", "Lato", "Montserrat"],
                key="font_selector_inline"
            )

            # 确认按钮
            if st.button("✅ 确认并应用该品牌风格", type="primary", key="confirm_brand_inline"):
                st.session_state['brand_colors'] = final_palette
                st.session_state['brand_font'] = font_choice
                st.session_state['is_brand_confirmed'] = True
                # 保存到文件实现持久化
                save_brand_config()
                st.rerun()

        # 如果已经确认，显示重置按钮
        if st.session_state['is_brand_confirmed']:
            st.success("✅ 品牌风格已应用")

            # 显示当前配色
            st.write("**当前品牌色：**")
            preview_cols = st.columns(5)
            for idx, color in enumerate(st.session_state['brand_colors'][:5]):
                with preview_cols[idx]:
                    st.markdown(
                        f'<div style="background-color:{color};height:30px;border-radius:4px;"></div>',
                        unsafe_allow_html=True
                    )

            if st.button("🔄 重置品牌风格", key="reset_brand_inline"):
                st.session_state['is_brand_confirmed'] = False
                st.session_state['extracted_colors'] = []
                st.session_state['brand_colors'] = [
                    '#667eea', '#764ba2', '#f093fb', '#4facfe',
                    '#00f2fe', '#43e97b', '#38f9d7', '#fa709a',
                    '#fee140', '#30cfd0'
                ]
                st.session_state['primary_color'] = "#667eea"
                st.session_state['brand_font'] = "Inter"
                # 保存到文件实现持久化
                save_brand_config()
                st.rerun()


# ==========================================
# 6. 测试示例
# ==========================================

if __name__ == '__main__':
    st.set_page_config(page_title="品牌色系统测试", layout="wide")

    # 初始化系统
    initialize_brand_system()

    # 应用主题
    apply_brand_theme()

    # 渲染配置界面
    render_brand_color_configurator()

    # 主内容区
    st.title("🎨 品牌色系统测试")
    st.markdown("这是一个测试页面，用于验证品牌色系统的所有功能")

    st.divider()

    # 显示当前配色
    st.subheader("当前品牌配色方案")

    colors = get_brand_colors()

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.metric("主色", get_primary_color())
        st.markdown(
            f'<div style="background-color:{get_primary_color()};height:100px;border-radius:8px;"></div>',
            unsafe_allow_html=True
        )

    with col2:
        st.metric("字体", get_brand_font())
        st.markdown(f"**示例文字**: The quick brown fox jumps over the lazy dog")

    with col3:
        st.metric("配色数量", len(colors))
        st.write("完整色板：")
        for color in colors:
            st.markdown(
                f'<div style="background-color:{color};height:20px;margin:2px 0;border-radius:4px;"></div>',
                unsafe_allow_html=True
            )

    st.divider()

    # 测试图表
    st.subheader("图表应用测试")

    import pandas as pd

    # 测试数据
    test_df = pd.DataFrame({
        '类别': ['A', 'B', 'C', 'D', 'E'],
        '数值': [23, 45, 56, 78, 90]
    })

    fig = px.bar(
        test_df,
        x='类别',
        y='数值',
        color='类别',
        color_discrete_sequence=colors
    )

    fig.update_layout(
        font=dict(family=get_brand_font()),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.success("✅ 品牌色系统测试完成")

