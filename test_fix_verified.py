"""
翻转卡片快速验证 - 修复后测试
"""

import streamlit as st
from flip_card_system import inject_flip_card_css, render_metric_flip_card

st.set_page_config(page_title="翻转卡片修复验证", layout="wide")

st.title("✅ 翻转卡片修复验证")

st.success("""
**已修复的问题**:
- 原代码使用了 `st.components.v1.html(html, unsafe_allow_html=True)` (错误)
- 已改回 `st.markdown(html, unsafe_allow_html=True)` (正确)

**st.components.v1.html() vs st.markdown()**:
- `st.components.v1.html()`: 用于完整的HTML文档,需要包含 `<html>`, `<head>`, `<body>` 标签
- `st.markdown()`: 用于HTML片段,更适合嵌入到Streamlit页面中
- `st.components.v1.html()` 不接受 `unsafe_allow_html` 参数!
""")

st.markdown("---")

# 注入CSS
inject_flip_card_css(primary_color='#4A5FE8')

# 测试指标
test_metric = {
    'name': '关键战略岗位按时达成率',
    'unit': '%',
    'formula': '按时入职P0级人员数 / P0级招聘计划总数 × 100%',
    'benchmark': {
        '优秀': '>85%',
        '良好': '75-85%',
        '需改进': '<75%'
    },
    'target': 85.0
}

st.subheader("🎴 测试翻转卡片 (悬停查看翻转效果)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### HRVP主题")
    render_metric_flip_card(
        metric_key='关键战略岗位按时达成率_%',
        metric_info=test_metric,
        current_value=88.5,
        target_value=85.0,
        role='HRVP',
        raw_data_dict={'按时入职': 34, '总计划': 40}
    )

with col2:
    st.markdown("#### HRD主题")
    render_metric_flip_card(
        metric_key='关键战略岗位按时达成率_%',
        metric_info=test_metric,
        current_value=82.3,
        target_value=85.0,
        role='HRD',
        raw_data_dict={'按时入职': 31, '总计划': 40}
    )

with col3:
    st.markdown("#### HR主题")
    render_metric_flip_card(
        metric_key='关键战略岗位按时达成率_%',
        metric_info=test_metric,
        current_value=78.2,
        target_value=85.0,
        role='HR',
        raw_data_dict={'按时入职': 28, '总计划': 40}
    )

st.markdown("---")

st.info("""
**验证清单**:
- ✅ 卡片显示为彩色卡片(不是HTML代码)
- ✅ 卡片有阴影和圆角
- ✅ 鼠标悬停时卡片3D翻转
- ✅ 背面显示公式、数据、基准
""")

st.markdown("---")
st.caption("如果上面的卡片正常显示并能翻转,说明问题已完全修复! 🎉")
