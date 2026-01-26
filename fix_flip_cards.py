"""
强制重新加载翻转卡片系统 - Flip Card Fix Test
用于诊断和修复翻转卡片渲染问题
"""

import streamlit as st
import importlib
import sys

# 清除模块缓存
if 'flip_card_system' in sys.modules:
    importlib.reload(sys.modules['flip_card_system'])

from flip_card_system import inject_flip_card_css, render_metric_flip_card
from data_generator_complete import generate_complete_recruitment_data

st.set_page_config(page_title="Flip Card Fix Test", layout="wide")

# 生成测试数据
df = generate_complete_recruitment_data(months=3, recruiters=2, departments=3)

# 注入CSS
primary_color = '#4A5FE8'
inject_flip_card_css(primary_color)

st.title("🎴 翻转卡片修复测试")
st.markdown("---")

st.info("""
**📝 测试说明:**
- 如果下面显示的是**可以翻转的精美卡片**，说明修复成功 ✅
- 如果下面显示的是**原始HTML代码**，说明还有问题 ❌
- 请悬停在卡片上查看翻转效果
""")

st.markdown("---")

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

# 渲染测试卡片
st.subheader("🎯 测试卡片 - 悬停查看翻转效果")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### HRVP主题 (蓝紫色)")
    render_metric_flip_card(
        metric_key='关键战略岗位按时达成率_%',
        metric_info=test_metric,
        current_value=88.5,
        target_value=85.0,
        role='HRVP',
        raw_data_dict={
            '按时入职P0级人员': 34,
            'P0级招聘计划总数': 40
        }
    )

with col2:
    st.markdown("#### HRD主题 (绿色)")
    render_metric_flip_card(
        metric_key='关键战略岗位按时达成率_%',
        metric_info=test_metric,
        current_value=82.3,
        target_value=85.0,
        role='HRD',
        raw_data_dict={
            '按时入职P0级人员': 31,
            'P0级招聘计划总数': 40
        }
    )

with col3:
    st.markdown("#### HR主题 (橙色)")
    render_metric_flip_card(
        metric_key='关键战略岗位按时达成率_%',
        metric_info=test_metric,
        current_value=78.2,
        target_value=85.0,
        role='HR',
        raw_data_dict={
            '按时入职P0级人员': 28,
            'P0级招聘计划总数': 40
        }
    )

st.markdown("---")

# 诊断信息
st.subheader("🔍 诊断信息")

diag_col1, diag_col2 = st.columns(2)

with diag_col1:
    st.markdown("""
    **✅ 成功的表现:**
    - 看到三个彩色卡片(蓝紫/绿/橙)
    - 卡片有阴影和圆角
    - 悬停时卡片3D翻转
    - 背面显示公式和数据
    """)

with diag_col2:
    st.markdown("""
    **❌ 失败的表现:**
    - 看到 `<div class="flip-container">` 等HTML代码
    - 卡片不能翻转
    - 样式混乱或无样式
    - 浏览器控制台有错误
    """)

st.markdown("---")

# 系统信息
st.subheader("⚙️ 系统信息")

sys_col1, sys_col2, sys_col3 = st.columns(3)

with sys_col1:
    st.metric("Streamlit版本", st.__version__)

with sys_col2:
    import pandas as pd
    st.metric("Pandas版本", pd.__version__)

with sys_col3:
    import numpy as np
    st.metric("NumPy版本", np.__version__)

st.markdown("---")

# 下一步建议
st.subheader("📋 下一步操作")

with st.expander("✅ 如果测试成功", expanded=False):
    st.markdown("""
    恭喜! 翻转卡片系统正常工作。

    **现在可以:**
    1. 返回主程序: `streamlit run recruitment_dashboard_v3_complete.py`
    2. 如果主程序还有问题，请清除缓存: `streamlit cache clear`
    3. 浏览器强制刷新: `Ctrl+Shift+R`
    """)

with st.expander("❌ 如果测试失败", expanded=True):
    st.markdown("""
    请尝试以下步骤:

    **步骤1: 清除缓存**
    ```bash
    streamlit cache clear
    ```

    **步骤2: 删除Python缓存**
    ```bash
    cd "E:\\AI Staff\\AI_Hire_Dashboard"
    rm -rf __pycache__
    rm -rf */__pycache__
    ```

    **步骤3: 检查浏览器控制台**
    - 按F12打开开发者工具
    - 查看Console和Network标签
    - 截图发送给技术支持

    **步骤4: 重装Streamlit**
    ```bash
    pip uninstall streamlit
    pip install streamlit
    ```

    **步骤5: 查看详细诊断指南**
    打开文件: `FLIP_CARD_DEBUG_GUIDE.md`
    """)

st.markdown("---")
st.success("✅ 测试完成! 请根据上面的结果判断是否需要进一步修复。")

# 显示原始HTML用于高级调试
with st.expander("🔧 高级调试 - 查看原始HTML", expanded=False):
    st.code("""
    <!-- 正确的HTML结构应该是这样: -->
    <div class="flip-container theme-vp">
        <div class="flip-inner">
            <div class="flip-front">
                <div class="kpi-title">关键战略岗位按时达成率</div>
                <div class="kpi-value">88.5<span class="unit">%</span></div>
                <div class="kpi-delta delta-positive">▲ 3.5% vs 目标</div>
            </div>
            <div class="flip-back">
                <div class="back-title">📊 关键战略岗位按时达成率</div>
                <div class="back-formula">
                    <strong>📐 计算公式:</strong><br>
                    按时入职P0级人员数 / P0级招聘计划总数 × 100%
                </div>
                <div class="back-data">
                    <strong>📈 数据明细:</strong><br>
                    <strong>按时入职P0级人员:</strong> 34<br>
                    <strong>P0级招聘计划总数:</strong> 40
                </div>
                <div class="back-benchmark">
                    <strong>🎯 基准参考:</strong>
                    <strong>优秀:</strong> >85% | <strong>良好:</strong> 75-85% | <strong>需改进:</strong> <75%
                </div>
            </div>
        </div>
    </div>
    """, language='html')

st.markdown("---")
st.caption("© 2026 翻转卡片修复工具 v1.0 | 如需帮助，请查看 FLIP_CARD_DEBUG_GUIDE.md")

