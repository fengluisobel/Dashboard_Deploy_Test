"""
最小化翻转卡片测试 - 直接HTML渲染
"""

import streamlit as st

st.set_page_config(page_title="Minimal Flip Test", layout="wide")

st.title("🔬 最小化翻转卡片测试")

# 直接注入CSS
css = """
<style>
.flip-container {
    perspective: 1000px;
    height: 160px;
    cursor: pointer;
    margin-bottom: 1rem;
}

.flip-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.6s;
    transform-style: preserve-3d;
}

.flip-container:hover .flip-inner {
    transform: rotateY(180deg);
}

.flip-front,
.flip-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.flip-front {
    background: #FFFFFF;
    border: 1.5px solid #E8E8E8;
}

.flip-back {
    background: #FAFBFC;
    border: 1.5px solid #D1D1D1;
    transform: rotateY(180deg);
}

.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #4A5FE8;
}
</style>
"""

st.markdown(css, unsafe_allow_html=True)

st.write("### 测试 1: 直接HTML")

# 直接渲染HTML
html_test = """
<div class="flip-container">
    <div class="flip-inner">
        <div class="flip-front">
            <div class="kpi-value">88.5%</div>
            <div>正面内容</div>
        </div>
        <div class="flip-back">
            <div>背面内容</div>
            <div>公式: A / B × 100%</div>
        </div>
    </div>
</div>
"""

st.markdown(html_test, unsafe_allow_html=True)

st.write("---")
st.write("### 测试 2: 使用函数渲染")

def render_test_card():
    html = """
    <div class="flip-container">
        <div class="flip-inner">
            <div class="flip-front">
                <div class="kpi-value">75.3%</div>
                <div>函数渲染正面</div>
            </div>
            <div class="flip-back">
                <div>函数渲染背面</div>
                <div>测试数据明细</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

render_test_card()

st.write("---")
st.info("💡 悬停在卡片上查看翻转效果。如果看到原始HTML代码而不是卡片，说明unsafe_allow_html有问题。")
