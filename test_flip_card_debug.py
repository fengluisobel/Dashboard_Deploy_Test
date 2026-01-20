"""
测试翻转卡片渲染 - Debug Version
"""

import streamlit as st
from flip_card_system import inject_flip_card_css, render_metric_flip_card

st.set_page_config(page_title="Flip Card Debug Test", layout="wide")

st.title("🔍 翻转卡片渲染测试 Debug")

# 注入 CSS
st.write("Step 1: 注入CSS...")
inject_flip_card_css(primary_color='#4A5FE8')
st.success("✅ CSS已注入")

# 测试指标数据
test_metric_info = {
    'name': '关键战略岗位按时达成率',
    'unit': '%',
    'formula': '按时入职的P0级人员数 / P0级招聘计划总数 × 100%',
    'definition': '仅统计对公司战略有重大影响的岗位',
    'benchmark': {
        '优秀': '>85%',
        '良好': '75-85%',
        '需改进': '<75%'
    },
    'target': 85.0
}

st.write("Step 2: 准备测试数据...")
st.json(test_metric_info)

st.write("Step 3: 渲染翻转卡片...")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 测试卡片 1")
    render_metric_flip_card(
        metric_key='关键战略岗位按时达成率_%',
        metric_info=test_metric_info,
        current_value=88.5,
        target_value=85.0,
        role='HRVP',
        raw_data_dict={'按时入职': 34, '总计划': 40}
    )

with col2:
    st.markdown("#### 测试卡片 2")
    render_metric_flip_card(
        metric_key='关键战略岗位按时达成率_%',
        metric_info=test_metric_info,
        current_value=82.3,
        target_value=85.0,
        role='HRD',
        raw_data_dict={'按时入职': 31, '总计划': 40}
    )

with col3:
    st.markdown("#### 测试卡片 3")
    render_metric_flip_card(
        metric_key='关键战略岗位按时达成率_%',
        metric_info=test_metric_info,
        current_value=78.2,
        target_value=85.0,
        role='HR',
        raw_data_dict={'按时入职': 28, '总计划': 40}
    )

st.markdown("---")
st.info("💡 请悬停在卡片上查看翻转效果")

# 显示原始HTML用于调试
with st.expander("🔍 查看原始HTML (Debug)"):
    st.code("""
    <div class="flip-container theme-vp">
        <div class="flip-inner">
            <div class="flip-front">...</div>
            <div class="flip-back">...</div>
        </div>
    </div>
    """, language='html')
