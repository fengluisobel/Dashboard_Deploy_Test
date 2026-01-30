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
from data_generator_complete import seed_db_with_generated_data, METRICS_METADATA
from db_manager import DBManager
from brand_color_system import (
    initialize_brand_system,
    render_brand_color_configurator_inline,
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
# Session State 初始化 for Chart Export
# ==========================================
if 'current_charts_data' not in st.session_state:
    st.session_state['current_charts_data'] = {}


# ==========================================
# 数据加载与缓存
# ==========================================

@st.cache_data
def load_recruitment_data(months=12, recruiters=5, departments=5):
    """
    加载招聘数据（从DuckDB）
    """
    # 无论参数如何，都统一调用 DB Seed 逻辑
    # 如果 DB 已有数据，会直接返回；没有则根据参数生成
    return seed_db_with_generated_data(months, recruiters, departments)


# ==========================================
# 侧边栏：全局控制
# ==========================================

import os

# Logo显示 - 优先使用用户自定义Logo文件，否则使用默认Logo
# 使用绝对路径以避免部署时的路径问题
current_dir = os.path.dirname(os.path.abspath(__file__))
default_logo = os.path.join(current_dir, "logo", "default_logo.png")
custom_logo_path = os.path.join(current_dir, "logo", "custom_logo.png")

# 检查自定义Logo文件是否存在
if os.path.exists(custom_logo_path):
    st.sidebar.image(custom_logo_path, width=150)
elif os.path.exists(default_logo):
    st.sidebar.image(default_logo, width=150)
else:
    # 兜底显示：如果找不到图片，显示文字
    st.sidebar.markdown("### 招聘驾驶舱")

 
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

# ==========================================
# 数据生成配置
# ==========================================

st.sidebar.subheader("⚙️ 数据配置")

with st.sidebar.expander("数据生成参数", expanded=False):
    months = st.number_input("月份数", min_value=3, max_value=24, value=12, key="data_months")
    recruiters = st.number_input("招聘顾问数", min_value=1, max_value=20, value=5, key="data_recruiters")
    departments = st.number_input("部门数", min_value=1, max_value=10, value=5, key="data_depts")

    if st.button("🔄 重置并重新生成", key="regenerate_data"):
        st.cache_data.clear()
        # 强制删除表并重新初始化 (通过简单地删除 db 文件或 drop table，这里选择简单 Drop)
        DBManager().conn.execute("DROP TABLE IF EXISTS recruitment_data")
        st.success("已重置数据库")
        st.rerun()

# ------------------------------------------
# [NEW] 数据管理中心
# ------------------------------------------
st.sidebar.subheader("💾 数据管理 Center")
with st.sidebar.expander("导入/导出/更新", expanded=False):
    db_mgr = DBManager()
    
    # 1. 导出
    if st.button("📥 导出当前数据 (Excel)", use_container_width=True):
        df_export = db_mgr.load_data_to_df()
        st.download_button(
            label="点击下载 .csv",
            data=df_export.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"recruitment_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    # 2. 导入
    uploaded_file = st.file_uploader("📤 上传数据 (覆写)", type=['csv', 'xlsx'])
    if uploaded_file:
        if st.button("确认导入", use_container_width=True):
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_new = pd.read_csv(uploaded_file)
                else:
                    df_new = pd.read_excel(uploaded_file)
                
                success, msg = db_mgr.import_data(df_new, mode='replace')
                if success:
                    st.success("导入成功! 请刷新页面")
                    st.cache_data.clear()
                else:
                    st.error(f"导入失败: {msg}")
            except Exception as e:
                st.error(f"文件解析错误: {e}")

    # 3. SQL 更新
    st.markdown("---")
    st.markdown("**🛠️ 高级: SQL 更新**")
    sql_query = st.text_area("输入SQL (支持 DuckDB 语法)", height=100, placeholder="UPDATE recruitment_data SET 部门='AI Lab' WHERE ...")
    if st.button("执行 SQL", key="run_sql_btn"):
        if sql_query.strip():
            success, res = db_mgr.execute_query(sql_query)
            if success:
                st.success("执行成功")
                if isinstance(res, pd.DataFrame) and not res.empty:
                    st.dataframe(res)
                st.cache_data.clear() # 清除缓存以显示更新
            else:
                st.error(f"执行失败: {res}")

# ------------------------------------------
# [NEW] 图表数据导出 (Report Generator)
# ------------------------------------------
st.sidebar.subheader("📊 导出图表数据")
with st.sidebar.expander("导出可视化的图表数据", expanded=True):
    # 获取当前已捕获的图表数据
    available_charts = st.session_state.get('current_charts_data', {})
    
    if not available_charts:
        st.info("暂无可用图表数据，请等待页面加载完成...")
    else:
        # 全选控制
        select_all_charts = st.checkbox("全选所有图表", value=False, key="select_all_charts_toggle")
        
        # 多选框 (默认全选或空)
        chart_options = list(available_charts.keys())
        default_selections = chart_options if select_all_charts else []
        
        selected_charts = st.multiselect(
            "选择要导出的图表:",
            options=chart_options,
            default=default_selections,
            key="chart_export_selector"
        )
        
        if st.button("📥 导出选中图表 (Excel)", use_container_width=True, key="export_charts_btn"):
            if not selected_charts:
                st.warning("请至少选择一个图表")
            else:
                try:
                    import io
                    # 创建内存中的 Excel 文件
                    output = io.BytesIO()
                    
                    # 使用 xlsxwriter 引擎 (Streamlit 默认支持)
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        for chart_name in selected_charts:
                            df_chart = available_charts[chart_name]
                            # Excel sheet name limit is 31 chars
                            sheet_name = chart_name.replace("HRVP - ", "").replace("HRD - ", "").replace("HR - ", "")[:30]
                            df_chart.to_excel(writer, sheet_name=sheet_name, index=False)
                            
                    output.seek(0)
                    
                    st.download_button(
                        label="点击下载 .xlsx",
                        data=output,
                        file_name=f"Chart_Data_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success(f"已生成 {len(selected_charts)} 个图表的数据文件")
                    
                except Exception as e:
                    st.error(f"导出失败: {str(e)}")

# 加载数据
with st.spinner("正在加载招聘数据..."):
    df = load_recruitment_data(months=months, recruiters=recruiters, departments=departments)

st.sidebar.markdown("---")

# ==========================================
# 侧边栏：数据筛选器（根据角色动态切换）
# ==========================================

st.sidebar.subheader("🔍 数据筛选")

# 初始化筛选后的数据
df_filtered = df.copy()

if role == "HRVP (战略驾驶舱)":
    # HRVP: 时间粒度 + 时间范围 + 快捷筛选
    
    # 快捷筛选按钮
    st.sidebar.markdown("**⚡ 快捷筛选:**")
    quick_col1, quick_col2 = st.sidebar.columns(2)
    
    with quick_col1:
        if st.button("近3个月", key="hrvp_quick_3m_sidebar", use_container_width=True):
            st.session_state.hrvp_quick_filter = "3m"
    
    with quick_col2:
        if st.button("近半年", key="hrvp_quick_6m_sidebar", use_container_width=True):
            st.session_state.hrvp_quick_filter = "6m"
    
    if st.sidebar.button("全部时间", key="hrvp_quick_all_sidebar", use_container_width=True):
        st.session_state.hrvp_quick_filter = "all"
    
    st.sidebar.markdown("")
    
    # 时间粒度
    time_granularity = st.sidebar.selectbox(
        "时间粒度",
        ["月度", "季度", "年度"],
        key="hrvp_time_granularity_sidebar"
    )
    
    # 处理快捷筛选
    if 'hrvp_quick_filter' in st.session_state and st.session_state.hrvp_quick_filter != "all":
        end_date = df['月份'].max()
        
        if st.session_state.hrvp_quick_filter == "3m":
            start_date = end_date - pd.DateOffset(months=3)
            st.sidebar.info(f"🔍 近3个月")
        elif st.session_state.hrvp_quick_filter == "6m":
            start_date = end_date - pd.DateOffset(months=6)
            st.sidebar.info(f"🔍 近半年")
        
        df_filtered = df[df['月份'] >= start_date].copy()
    else:
        # 常规时间筛选
        if time_granularity == "月度":
            start_month = st.sidebar.date_input("开始月份", df['月份'].min(), key="hrvp_start_sidebar")
            end_month = st.sidebar.date_input("结束月份", df['月份'].max(), key="hrvp_end_sidebar")
            df_filtered = df[
                (df['月份'] >= pd.to_datetime(start_month)) &
                (df['月份'] <= pd.to_datetime(end_month))
            ].copy()
        elif time_granularity == "季度":
            quarters = df['季度'].unique()
            start_quarter = st.sidebar.selectbox("开始季度", quarters, key="hrvp_start_q_sidebar")
            end_quarter = st.sidebar.selectbox("结束季度", quarters, index=len(quarters)-1, key="hrvp_end_q_sidebar")
            start_idx = list(quarters).index(start_quarter)
            end_idx = list(quarters).index(end_quarter)
            selected_quarters = quarters[start_idx:end_idx+1]
            df_filtered = df[df['季度'].isin(selected_quarters)].copy()
        else:
            years = df['年份'].unique()
            start_year = st.sidebar.selectbox("开始年份", years, key="hrvp_start_y_sidebar")
            end_year = st.sidebar.selectbox("结束年份", years, index=len(years)-1, key="hrvp_end_y_sidebar")
            df_filtered = df[
                (df['年份'] >= start_year) &
                (df['年份'] <= end_year)
            ].copy()
    
    # 存储时间粒度供dashboard使用
    st.session_state['current_time_granularity'] = time_granularity

elif role == "HRD (异常报警器)":
    # HRD: 时间粒度 + 时间范围 + 部门多选
    
    time_granularity = st.sidebar.selectbox(
        "时间粒度",
        ["周度", "月度"],
        key="hrd_time_granularity_sidebar"
    )
    
    start_month = st.sidebar.date_input("开始时间", df['月份'].min(), key="hrd_start_sidebar")
    end_month = st.sidebar.date_input("结束时间", df['月份'].max(), key="hrd_end_sidebar")
    
    selected_depts = st.sidebar.multiselect(
        "部门筛选 (可多选)",
        options=df['部门'].unique().tolist(),
        default=df['部门'].unique().tolist(),
        key="hrd_dept_filter_sidebar"
    )
    
    # 数据筛选
    df_filtered = df[
        (df['月份'] >= pd.to_datetime(start_month)) &
        (df['月份'] <= pd.to_datetime(end_month)) &
        (df['部门'].isin(selected_depts))
    ].copy()
    
    st.session_state['current_time_granularity'] = time_granularity

elif role == "HR (任务管理器)":
    # HR: 当前用户 + 时间范围
    
    recruiter_list = df['招聘顾问'].unique().tolist()
    
    selected_recruiter = st.sidebar.selectbox(
        "👤 当前用户",
        recruiter_list,
        key="hr_user_selector_sidebar"
    )
    
    st.sidebar.info(f"仅显示 **{selected_recruiter}** 的数据")
    
    time_range = st.sidebar.selectbox(
        "时间范围",
        ["今日", "本周", "本月", "自定义"],
        key="hr_time_range_sidebar"
    )
    
    custom_days = 7
    if time_range == "自定义":
        custom_days = st.sidebar.number_input("过去N天", min_value=1, max_value=90, value=7, key="hr_custom_days_sidebar")
    
    # 数据筛选 - 只看自己的数据
    df_my_data = df[df['招聘顾问'] == selected_recruiter].copy()
    
    if time_range == "今日":
        today = df_my_data['月份'].max()
        df_filtered = df_my_data[df_my_data['月份'] == today].copy()
    elif time_range == "本周":
        last_week = df_my_data['月份'].max() - pd.Timedelta(days=7)
        df_filtered = df_my_data[df_my_data['月份'] >= last_week].copy()
    elif time_range == "本月":
        current_month = df_my_data['月份'].max().replace(day=1)
        df_filtered = df_my_data[df_my_data['月份'] >= current_month].copy()
    else:
        cutoff_date = df_my_data['月份'].max() - pd.Timedelta(days=custom_days)
        df_filtered = df_my_data[df_my_data['月份'] >= cutoff_date].copy()
    
    st.session_state['selected_recruiter'] = selected_recruiter
    st.session_state['hr_time_range'] = time_range

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
# 主内容区：品牌风格定制（右侧可折叠面板）
# ==========================================

# 使用 columns 布局，将品牌设置放在右上角
brand_col1, brand_col2 = st.columns([3, 1])

with brand_col2:
    render_brand_color_configurator_inline()


# ==========================================
# 主内容区：根据角色渲染不同看板
# ==========================================

# 渲染对应角色的看板
if role == "HRVP (战略驾驶舱)":
    render_hrvp_dashboard(df_filtered)

elif role == "HRD (异常报警器)":
    render_hrd_dashboard(df_filtered)

elif role == "HR (任务管理器)":
    selected_recruiter = st.session_state.get('selected_recruiter', df['招聘顾问'].unique()[0])
    render_hr_dashboard(df_filtered, selected_recruiter=selected_recruiter)


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

