import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ================= 1. 数据构造：JD 与 候选人池 =================
@st.cache_data
def get_battle_data():
    # 1. 定义岗位画像 (JD Benchmark)
    # 假设这是 "高级算法工程师" 的标准画像
    jd_profile = {
        'role': '高级算法工程师 (Senior Algo Engineer)',
        'dimensions': ['编码能力', '算法深度', '系统设计', '沟通力', '业务Sense', '稳定性'],
        'ideal_score': [5, 5, 4, 3, 4, 4], # 理想分
        'weight':      [0.2, 0.3, 0.2, 0.1, 0.1, 0.1] # 权重
    }

    # 2. 定义候选人数据
    candidates = {
        'C-1001 (性价比小将)': {
            'scores': [4, 3, 3, 5, 4, 5], 
            'salary': 35, # 万/年
            'exp': 3,     # 年
            'tags': ['潜力股', '沟通极佳', '便宜'],
            'risk': '经验稍欠缺'
        },
        'C-1002 (技术大牛)': {
            'scores': [5, 5, 5, 2, 3, 3],
            'salary': 65,
            'exp': 8,
            'tags': ['技术大拿', '架构专家', '贵'],
            'risk': '稳定性一般，沟通成本高'
        },
        'C-1003 (稳健老手)': {
            'scores': [4, 4, 4, 4, 5, 4],
            'salary': 50,
            'exp': 6,
            'tags': ['六边形战士', '业务专家', '匹配度高'],
            'risk': '无明显短板也无特长'
        }
    }
    return jd_profile, candidates

jd, candidates = get_battle_data()

# ================= 2. 页面布局 =================
st.markdown("---")
st.header("⚔️ AI 候选人竞技场 (Candidate Battle Arena)")
st.markdown("""
> **决策辅助系统**：在此模式下，AI 将充当“裁判”，对比两名候选人的优劣势，并结合 JD 画像给出聘用建议。
""")

# --- 选择区 ---
col_sel1, col_vs, col_sel2 = st.columns([2, 1, 2])
with col_sel1:
    c1_name = st.selectbox("🥊 红方选手 (Challenger A)", list(candidates.keys()), index=0)
with col_vs:
    st.markdown("<h2 style='text-align: center; color: gray;'>VS</h2>", unsafe_allow_html=True)
with col_sel2:
    # 默认选第二个
    c2_name = st.selectbox("🥊 蓝方选手 (Challenger B)", list(candidates.keys()), index=1)

if c1_name == c2_name:
    st.warning("⚠️ 请选择两个不同的候选人进行对比。")
    st.stop()

# 获取数据
c1_data = candidates[c1_name]
c2_data = candidates[c2_name]
dims = jd['dimensions']

# ================= 3. 核心图表区 =================

col_radar, col_butterfly = st.columns([1, 1])

# --- 图表 A：三方雷达图 (JD vs A vs B) ---
with col_radar:
    st.subheader("1. 综合能力覆盖度 (Radar)")
    fig_radar = go.Figure()

    # 1. 画 JD 基准 (背景阴影)
    fig_radar.add_trace(go.Scatterpolar(
        r=jd['ideal_score'], theta=dims,
        fill='toself', name='JD 理想画像',
        line=dict(color='gray', dash='dash'),
        fillcolor='rgba(200, 200, 200, 0.2)',
        hoverinfo='skip'
    ))

    # 2. 画 候选人 A (红)
    fig_radar.add_trace(go.Scatterpolar(
        r=c1_data['scores'], theta=dims,
        fill='toself', name=c1_name.split('(')[0],
        line=dict(color='#e74c3c'),
        fillcolor='rgba(231, 76, 60, 0.1)'
    ))

    # 3. 画 候选人 B (蓝)
    fig_radar.add_trace(go.Scatterpolar(
        r=c2_data['scores'], theta=dims,
        fill='toself', name=c2_name.split('(')[0],
        line=dict(color='#3498db'),
        fillcolor='rgba(52, 152, 219, 0.1)'
    ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        legend=dict(orientation="h", y=-0.1),
        height=400,
        margin=dict(t=20, b=20, l=40, r=40)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# --- 图表 B：技能差异蝴蝶图 (Butterfly Chart) ---
with col_butterfly:
    st.subheader("2. 技能强弱对抗 (Skill Diff)")
    
    # 计算差异：A - B
    diffs = np.array(c1_data['scores']) - np.array(c2_data['scores'])
    
    # 颜色逻辑：A强显红，B强显蓝
    colors = ['#e74c3c' if x > 0 else '#3498db' if x < 0 else 'gray' for x in diffs]
    
    fig_bf = go.Figure()
    
    fig_bf.add_trace(go.Bar(
        y=dims,
        x=diffs,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{abs(x):.0f}" if x!=0 else "平" for x in diffs],
        textposition="outside"
    ))
    
    # 布局美化
    fig_bf.update_layout(
        title="◀ 红方更强 ———— 蓝方更强 ▶",
        xaxis=dict(
            title="分差 (Score Delta)", 
            range=[-4, 4], 
            tickvals=[-3, 0, 3],
            ticktext=[f"{c2_name[:4]} 胜", "平手", f"{c1_name[:4]} 胜"]
        ),
        yaxis=dict(autorange="reversed"), # 翻转Y轴让第一个维度在最上面
        height=400,
        showlegend=False
    )
    # 添加中间的竖线
    fig_bf.add_vline(x=0, line_width=2, line_color="black")
    
    st.plotly_chart(fig_bf, use_container_width=True)

# ================= 4. AI 智能决策裁判 (NLG) =================
st.subheader("🤖 AI 决策建议 (Decision Intelligence)")

# --- 逻辑计算 ---
salary_diff = c1_data['salary'] - c2_data['salary']
exp_diff = c1_data['exp'] - c2_data['exp']

# 找出各自的优势维度
c1_adv_indices = [i for i, x in enumerate(c1_data['scores']) if x > c2_data['scores'][i]]
c2_adv_indices = [i for i, x in enumerate(c2_data['scores']) if x > c1_data['scores'][i]]

c1_strong = ", ".join([dims[i] for i in c1_adv_indices]) if c1_adv_indices else "无明显技能优势"
c2_strong = ", ".join([dims[i] for i in c2_adv_indices]) if c2_adv_indices else "无明显技能优势"

# 渲染对比卡片
col_res1, col_res2 = st.columns(2)

with col_res1:
    st.markdown(f"""
    <div style='background-color:rgba(231, 76, 60, 0.1); padding:15px; border-radius:10px; border-left:5px solid #e74c3c'>
        <h4>🔴 为什么选 {c1_name}?</h4>
        <ul>
            <li><b>成本优势：</b> 年薪比对方 {"低" if salary_diff < 0 else "高"} <b>{abs(salary_diff)}万</b></li>
            <li><b>技能长板：</b> 在 <b>{c1_strong}</b> 方面表现更好</li>
            <li><b>适合场景：</b> {c1_data['tags'][0]}，适合预算有限或需要强沟通的团队。</li>
            <li><b>风险提示：</b> {c1_data['risk']}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_res2:
    st.markdown(f"""
    <div style='background-color:rgba(52, 152, 219, 0.1); padding:15px; border-radius:10px; border-left:5px solid #3498db'>
        <h4>🔵 为什么选 {c2_name}?</h4>
        <ul>
            <li><b>经验优势：</b> 工作年限多 <b>{abs(exp_diff)}年</b> (资深程度)</li>
            <li><b>技能长板：</b> 在 <b>{c2_strong}</b> 方面表现更好</li>
            <li><b>适合场景：</b> {c2_data['tags'][0]}，适合技术攻坚或核心架构岗位。</li>
            <li><b>风险提示：</b> {c2_data['risk']}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- AI 最终总结 ---
st.markdown("### 📝 AI 最终裁决")

if salary_diff < -10 and len(c2_adv_indices) > len(c1_adv_indices):
    verdict = f"**建议录用 {c1_name} (高性价比)**。虽然技术稍弱，但成本优势巨大，且沟通能力能弥补部分技术短板，符合当前降本增效的大环境。"
elif len(c2_adv_indices) >= 3 and c2_data['scores'][1] == 5: # 假设索引1是算法深度
    verdict = f"**建议录用 {c2_name} (技术导向)**。虽然更贵，但在核心的【算法深度】和【系统设计】上具备碾压优势，是解决当前技术瓶颈的关键人选。"
else:
    verdict = "**双方势均力敌**。建议结合具体的团队当前缺口决定：缺干活的人选红方，缺带队的人选蓝方。"

st.info(verdict)