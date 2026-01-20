import streamlit as st

# ==========================================
# 翻转卡片 CSS 系统 (✅ 修复黑块+翻转失效)
# ==========================================

def inject_flip_card_css(primary_color='#4A5FE8'):
    css = f"""
    <style>
    /* ========================================== */
    /* Flip Card Container - 核心：保留原生3D层级 */
    /* ========================================== */
    .flip-container {{
        perspective: 1000px;
        height: 160px;
        cursor: pointer;
        margin-bottom: 1rem;
        /* 关键：禁止 Streamlit 覆盖容器样式 */
        position: relative;
    }}

    .flip-inner {{
        position: relative;
        width: 100%;
        height: 100%;
        transition: transform 0.6s cubic-bezier(0.4, 0.0, 0.2, 1);
        transform-style: preserve-3d;
        -webkit-transform-style: preserve-3d; /* 必须加前缀 */
    }}

    .flip-container:hover .flip-inner {{
        transform: rotateY(180deg);
        -webkit-transform: rotateY(180deg); /* 必须加前缀 */
    }}

    /* ========================================== */
    /* Front and Back Faces - ✅ 修复黑块+前缀 */
    /* ========================================== */
    .flip-front,
    .flip-back {{
        position: absolute;
        width: 100%;
        height: 100%;
        /* 核心：双前缀+强制不透明，解决黑块 */
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        background-color: #FFFFFF !important; /* 强制白色背景，避免覆盖 */
        opacity: 1 !important; /* 强制不透明 */
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-sizing: border-box;
    }}

    .flip-front {{
        border: 1.5px solid #E8E8E8;
    }}

    .flip-back {{
        background-color: #F5F7FA !important; /* 略深的背景，区分正反面 */
        border: 1.5px solid #D1D1D1;
        transform: rotateY(180deg);
        -webkit-transform: rotateY(180deg); /* 必须加前缀 */
    }}

    /* ========================================== */
    /* 以下样式完全保留你的原始逻辑，仅优化颜色对比度 */
    /* ========================================== */
    .kpi-title {{
        font-size: 0.875rem;
        color: #3F3F3F;  /* Contrast: 10.5:1 ✅ AAA */
        margin-bottom: 0.75rem;
        font-weight: 500;
        line-height: 1.4;
    }}

    .kpi-value {{
        font-size: 2.25rem;
        font-weight: 700;
        color: {primary_color};
        margin-bottom: 0.5rem;
        line-height: 1;
    }}

    .kpi-value .unit {{
        font-size: 1rem;
        font-weight: 500;
        margin-left: 0.25rem;
        color: #6B6B6B;
    }}

    .kpi-delta {{
        font-size: 0.875rem;
        font-weight: 600;
        line-height: 1.2;
    }}

    .delta-positive {{
        color: #0A6930;
    }}

    .delta-negative {{
        color: #A01820;
    }}

    .back-title {{
        font-size: 0.875rem;
        color: #2C2C2C;
        font-weight: 600;
        margin-bottom: 0.75rem;
        border-bottom: 2px solid #E8E8E8;
        padding-bottom: 0.5rem;
    }}

    .back-formula {{
        font-size: 0.8rem;
        color: #3F3F3F;
        margin-bottom: 0.75rem;
        line-height: 1.5;
        background: #FFFFFF;
        padding: 0.5rem;
        border-radius: 6px;
        border: 1px solid #E8E8E8;
        font-family: 'Consolas', 'Monaco', monospace;
    }}

    .back-data {{
        font-size: 0.8rem;
        color: #3F3F3F;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }}

    .back-benchmark {{
        font-size: 0.75rem;
        color: #6B6B6B;
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #E8E8E8;
        line-height: 1.3;
    }}

    /* ========================================== */
    /* 角色主题 - 加强背景色不透明度，防止显黑 */
    /* ========================================== */
    .theme-vp .flip-front {{
        background: linear-gradient(135deg, #F8F9FF 0%, #FFFFFF 100%) !important;
        border-left: 4px solid {primary_color};
    }}

    .theme-vp .kpi-value {{
        background: linear-gradient(135deg, {primary_color} 0%, #6B7FFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    .theme-vp .flip-back {{
        background: linear-gradient(135deg, #F0F2FF 0%, #F5F7FA 100%) !important;
        border-left: 4px solid {primary_color};
    }}

    .theme-hrd .flip-front {{
        background: linear-gradient(135deg, #F0FFF7 0%, #FFFFFF 100%) !important;
        border-left: 4px solid #0D7C3A;
    }}

    .theme-hrd .kpi-value {{
        color: #0D7C3A;
    }}

    .theme-hrd .flip-back {{
        background: linear-gradient(135deg, #E8F8F0 0%, #F5F7FA 100%) !important;
        border-left: 4px solid #0D7C3A;
    }}

    .theme-hr .flip-front {{
        background: linear-gradient(135deg, #FFF5F7 0%, #FFFFFF 100%) !important;
        border-left: 4px solid #C17A00;
    }}

    .theme-hr .kpi-value {{
        color: #C17A00;
    }}

    .theme-hr .flip-back {{
        background: linear-gradient(135deg, #FFF0E8 0%, #F5F7FA 100%) !important;
        border-left: 4px solid #C17A00;
    }}

    /* ========================================== */
    /* 悬停效果+提示动画 - 保留原始逻辑 */
    /* ========================================== */
    .flip-container:hover .flip-front {{
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }}

    .flip-container:hover .flip-back {{
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }}

    @media (max-width: 768px) {{
        .flip-container {{
            height: 180px;
        }}

        .kpi-value {{
            font-size: 1.75rem;
        }}

        .back-formula {{
            font-size: 0.75rem;
        }}
    }}

    @keyframes flip-hint {{
        0%, 100% {{ transform: rotateY(0deg); }}
        50% {{ transform: rotateY(15deg); }}
    }}

    @-webkit-keyframes flip-hint {{
        0%, 100% {{ -webkit-transform: rotateY(0deg); }}
        50% {{ -webkit-transform: rotateY(15deg); }}
    }}

    .flip-container:not(:hover) .flip-inner {{
        animation: flip-hint 3s ease-in-out infinite;
        -webkit-animation: flip-hint 3s ease-in-out infinite;
        animation-delay: 2s;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ==========================================
# 翻转卡片渲染函数 (✅ 恢复 st.markdown 渲染)
# ==========================================

def render_metric_flip_card(
    metric_key: str,
    metric_info: dict,
    current_value: float,
    target_value: float,
    role: str = 'HRVP',
    raw_data_dict: dict = None
):
    theme_map = {
        'HRVP': 'theme-vp',
        'HRD': 'theme-hrd',
        'HR': 'theme-hr'
    }
    theme = theme_map.get(role, 'theme-vp')

    unit = metric_info.get('unit', '')
    is_cost_metric = '成本' in metric_key or '损失' in metric_key

    if is_cost_metric:
        delta = target_value - current_value
        delta_class = 'delta-positive' if delta >= 0 else 'delta-negative'
        delta_symbol = '▼' if delta >= 0 else '▲'
    else:
        delta = current_value - target_value
        delta_class = 'delta-positive' if delta >= 0 else 'delta-negative'
        delta_symbol = '▲' if delta >= 0 else '▼'

    if unit == '%':
        value_text = f"{current_value:.1f}"
        delta_text = f"{abs(delta):.1f}{unit}"
    elif unit == '元' or unit == '万元':
        value_text = f"{current_value:,.0f}"
        delta_text = f"{abs(delta):,.0f}{unit}"
    else:
        value_text = f"{current_value:.1f}"
        delta_text = f"{abs(delta):.1f}{unit}"

    if raw_data_dict:
        raw_data_html = "<br>".join([f"<strong>{k}:</strong> {v}" for k, v in raw_data_dict.items()])
    else:
        raw_data_html = f"<strong>当前值:</strong> {value_text}{unit}<br><strong>目标值:</strong> {target_value}{unit}"

    benchmark = metric_info.get('benchmark', {})
    benchmark_html = " | ".join([f"<strong>{k}:</strong> {v}" for k, v in benchmark.items()]) if benchmark else "暂无基准"

    # 卡片HTML结构完全不变
    html = f"""
    <div class="flip-container {theme}">
        <div class="flip-inner">
            <div class="flip-front">
                <div class="kpi-title">{metric_info['name']}</div>
                <div class="kpi-value">
                    {value_text}<span class="unit">{unit}</span>
                </div>
                <div class="kpi-delta {delta_class}">
                    {delta_symbol} {delta_text} vs 目标
                </div>
            </div>
            <div class="flip-back">
                <div class="back-title">📊 {metric_info['name']}</div>
                <div class="back-formula">
                    <strong>📐 计算公式:</strong><br>
                    {metric_info.get('formula', '暂无公式')}
                </div>
                <div class="back-data">
                    <strong>📈 数据明细:</strong><br>
                    {raw_data_html}
                </div>
                <div class="back-benchmark">
                    <strong>🎯 基准参考:</strong> {benchmark_html}
                </div>
            </div>
        </div>
    </div>
    """
    # ✅ 核心恢复：用 st.markdown + unsafe_allow_html=True 渲染
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 批量渲染函数 (保留原逻辑)
# ==========================================
def render_metrics_flip_cards_row(
    metrics_list: list,
    df_filtered,
    role: str = 'HRVP',
    columns_count: int = 5
):
    cols = st.columns(columns_count)
    for idx, metric_dict in enumerate(metrics_list):
        metric_key = metric_dict['metric_key']
        metric_info = metric_dict['metric_info']
        current_value = df_filtered[metric_key].sum() if '损失' in metric_key or '成本' in metric_key else df_filtered[metric_key].mean()
        target = metric_info['target']
        with cols[idx % columns_count]:
            render_metric_flip_card(metric_key, metric_info, current_value, target, role)

# ==========================================
# 测试代码 (直接运行)
# ==========================================
if __name__ == '__main__':
    st.set_page_config(page_title="Flip Card System Test", layout="wide")
    inject_flip_card_css(primary_color='#4A5FE8')

    st.title("🎴 Flip Card System - 最终修复版")
    st.markdown("### ✅ 能翻转 + 无黑块 + 保留所有主题功能")

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

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### HRVP Theme")
        render_metric_flip_card(
            metric_key='关键战略岗位按时达成率_%',
            metric_info=test_metric_info,
            current_value=88.5,
            target_value=85.0,
            role='HRVP',
            raw_data_dict={'按时入职': 34, '总计划': 40}
        )

    with col2:
        st.markdown("#### HRD Theme")
        render_metric_flip_card(
            metric_key='关键战略岗位按时达成率_%',
            metric_info=test_metric_info,
            current_value=82.3,
            target_value=85.0,
            role='HRD',
            raw_data_dict={'按时入职': 31, '总计划': 40}
        )

    with col3:
        st.markdown("#### HR Theme")
        render_metric_flip_card(
            metric_key='关键战略岗位按时达成率_%',
            metric_info=test_metric_info,
            current_value=78.2,
            target_value=85.0,
            role='HR',
            raw_data_dict={'按时入职': 28, '总计划': 40}
        )

    st.success("✅ 修复完成：卡片可正常翻转 + 无黑块 + 所有主题样式生效")