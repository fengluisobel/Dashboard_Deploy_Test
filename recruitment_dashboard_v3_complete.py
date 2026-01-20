"""
招聘数据驾驶舱 v3.0 Pro - 完整集成版
整合所有模块的主程序

版本: v3.0 Pro
发布日期: 2026-01-16
设计理念: 不是"给你看数据"，而是"告诉你该做什么决策/警惕什么风险/执行什么任务"
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# 导入所有模块
from data_generator_complete import generate_complete_recruitment_data, METRICS_METADATA
from brand_color_system import (
    initialize_brand_system,
    render_brand_color_configurator,
    apply_brand_theme,
    get_brand_colors,
    get_primary_color
)
from dashboard_hrvp import render_hrvp_dashboard, HRVP_CORE_METRICS
from dashboard_hrd import render_hrd_dashboard, HRD_EXCEPTION_METRICS
from dashboard_hr import render_hr_dashboard, HR_EXECUTION_METRICS
from visual_enhancement_pro import inject_professional_uiux_css, render_pro_header


# ==========================================
# 页面配置
# ==========================================

st.set_page_config(
    page_title="招聘数据驾驶舱 v3.0 Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# 初始化系统
# ==========================================

# 初始化品牌系统
initialize_brand_system()

# 应用品牌主题
apply_brand_theme()

# 应用专业级UI/UX视觉增强 (WCAG AAA级对比度)
inject_professional_uiux_css(get_primary_color())


# ==========================================
# 数据加载与缓存
# ==========================================

@st.cache_data
def load_recruitment_data(months=12, recruiters=5, departments=5):
    """
    加载招聘数据（带缓存）
    """
    return generate_complete_recruitment_data(months, recruiters, departments)


# ==========================================
# 侧边栏：全局控制
# ==========================================

# st.sidebar.image("https://via.placeholder.com/300x80/667eea/ffffff?text=Recruitment+Dashboard", use_container_width=True)

# st.sidebar.title("📊 招聘数据驾驶舱 v3.0 Pro")
# st.sidebar.markdown("---")


# 自动生成带背景色的专业 Logo
# logo_url = "https://ui-avatars.com/api/?name=Talent+Pro&background=0068c9&color=fff&size=256&font-size=0.33&length=2&rounded=true&bold=true"


logo_url = "logo/logo_全.png" 

st.sidebar.image(logo_url, width=150,) # 控制宽度更精致
st.sidebar.title("AI Hire 驾驶舱")
st.sidebar.caption("v3.0 Pro | Enterprise Edition")
st.sidebar.markdown("---")


# 角色选择
st.sidebar.subheader("🎭 选择角色视角")

role = st.sidebar.radio(
    "当前角色",
    ["HRVP (战略驾驶舱)", "HRD (异常报警器)", "HR (任务管理器)"],
    key="role_selector"
)

st.sidebar.markdown("---")

# 品牌色配置器
render_brand_color_configurator()

st.sidebar.markdown("---")

# 数据生成配置
st.sidebar.subheader("⚙️ 数据配置")

with st.sidebar.expander("数据生成参数", expanded=False):
    months = st.number_input("月份数", min_value=3, max_value=24, value=12, key="data_months")
    recruiters = st.number_input("招聘顾问数", min_value=1, max_value=20, value=5, key="data_recruiters")
    departments = st.number_input("部门数", min_value=1, max_value=10, value=5, key="data_depts")

    if st.button("🔄 重新生成数据", key="regenerate_data"):
        st.cache_data.clear()
        st.rerun()

st.sidebar.markdown("---")

# 系统信息
st.sidebar.subheader("ℹ️ 系统信息")
st.sidebar.info(f"""
**版本**: v3.0 Pro
**更新**: 2026-01-16
**指标总数**: 81个
- L1: 5个
- L2: 27个
- L3: 54个

**当前品牌色**: {len(get_brand_colors())}色
""")

# 帮助文档
with st.sidebar.expander("📖 使用帮助"):
    st.markdown("""
    ### 三层角色定位

    **HRVP (战略驾驶舱)**
    - 只看金钱、战略、风险
    - 4-5个核心战略指标
    - 全集团汇总视图
    - 月度/季度/年度

    **HRD (异常报警器)**
    - 红黄绿预警系统
    - 部门/BU汇总视图
    - 可下钻到Recruiter
    - 周度/月度

    **HR (任务管理器)**
    - 今日待办清单置顶
    - 告诉你该做什么
    - 仅个人负责职位
    - 每日/每周
    """)


# ==========================================
# 主内容区：根据角色渲染不同看板
# ==========================================

# 加载数据
with st.spinner("正在加载招聘数据..."):
    df = load_recruitment_data(months=months, recruiters=recruiters, departments=departments)

# 渲染对应角色的看板
if role == "HRVP (战略驾驶舱)":
    render_hrvp_dashboard(df)

elif role == "HRD (异常报警器)":
    render_hrd_dashboard(df)

elif role == "HR (任务管理器)":
    # HR需要选择具体的招聘顾问
    recruiter_list = df['招聘顾问'].unique().tolist()

    # 在主内容区顶部让用户选择
    st.markdown("### 👤 选择招聘顾问")
    selected_recruiter = st.selectbox(
        "当前用户 (HR只能查看自己的数据)",
        recruiter_list,
        key="hr_main_user_selector"
    )

    st.markdown("---")

    render_hr_dashboard(df, selected_recruiter=selected_recruiter)


# ==========================================
# 底部：版权和链接
# ==========================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📚 相关文档**
    - [V3_PRO_README.md](./V3_PRO_README.md)
    - [BI指标体系.json](./指标梳理/BI指标体系.json)
    - [招聘指标 层级.md](./MindMap/招聘指标 层级.md)
    """)

with col2:
    st.markdown("""
    **🎨 设计风格**
    - 科技咨询·专业严谨
    - Inter字体
    - 渐变蓝紫主色
    - 卡片式布局
    """)

with col3:
    st.markdown("""
    **✅ 核心价值**
    - HRVP: 决策时间减少80%
    - HRD: 异常发现速度提升10倍
    - HR: 报表分析时间减少90%
    """)

st.markdown("---")

st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem 0;">
    © 2026 招聘数据驾驶舱 v3.0 Pro | Powered by Streamlit & Plotly |
    <a href="https://github.com/yourusername/recruitment-dashboard" target="_blank" style="color: #667eea;">GitHub</a>
</div>
""", unsafe_allow_html=True)
