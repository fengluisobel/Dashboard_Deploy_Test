import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ================= 1. 模拟 AI 评分模型数据 =================
# 假设我们有一个简单的线性模型：基准分 + 加分项 - 减分项
xai_data = {
    'C-1024 (王强)': {
        'total_score': 82,
        'breakdown': [
            dict(measure="relative", name="基础分 (Base)", value=60),
            dict(measure="relative", name="学历匹配 (985/211)", value=10),
            dict(measure="relative", name="技能匹配 (Python/Go)", value=15),
            dict(measure="relative", name="行业经验 (3-5年)", value=5),
            dict(measure="relative", name="跳槽频繁 (2年3跳)", value=-5),
            dict(measure="relative", name="期望薪资偏高", value=-3),
            dict(measure="total", name="最终得分", value=82)
        ],
        'skills': {
            'Python': {'req': 5, 'act': 5, 'status': 'perfect'},
            'SQL': {'req': 4, 'act': 4, 'status': 'good'},
            'Machine Learning': {'req': 4, 'act': 2, 'status': 'gap'},
            'Communication': {'req': 3, 'act': 4, 'status': 'good'},
            'Java': {'req': 3, 'act': 0, 'status': 'missing'}
        }
    },
    'C-1025 (李娜)': {
        'total_score': 91,
        'breakdown': [
            dict(measure="relative", name="基础分 (Base)", value=60),
            dict(measure="relative", name="学历匹配 (硕士)", value=12),
            dict(measure="relative", name="大厂背景", value=8),
            dict(measure="relative", name="核心技能 (算法)", value=15),
            dict(measure="relative", name="管理经验缺失", value=-2),
            dict(measure="relative", name="面试表现", value=-2),
            dict(measure="total", name="最终得分", value=91)
        ],
        'skills': {
            'Python': {'req': 5, 'act': 4, 'status': 'good'},
            'SQL': {'req': 4, 'act': 5, 'status': 'good'},
            'Machine Learning': {'req': 4, 'act': 5, 'status': 'perfect'},
            'Communication': {'req': 3, 'act': 3, 'status': 'good'},
            'Java': {'req': 3, 'act': 1, 'status': 'missing'}
        }
    }
}

# ================= 2. 页面布局 =================
st.markdown("---")
st.header("🤖 AI 评分透视镜 (XAI Score Explainer)")
st.markdown("""
> **白盒化展示**：此处展示 AI 算法是如何计算出候选人分数的。
> *   **左侧瀑布图**：展示分数的加分项（绿色）和扣分项（红色）。
> *   **右侧技能图**：展示候选人技能与 JD 要求的匹配差距。
""")

# 交互：选择候选人
selected_candidate = st.selectbox("👤 选择候选人进行分析:", list(xai_data.keys()))
candidate_data = xai_data[selected_candidate]

# 布局
col_waterfall, col_skills = st.columns([1.5, 1])

# --- 3. 左侧：分数归因瀑布图 (Waterfall Chart) ---
with col_waterfall:
    st.subheader("1. 分数构成归因 (Score Breakdown)")
    
    # 提取数据
    breakdown_df = pd.DataFrame(candidate_data['breakdown'])
    
    fig_waterfall = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = breakdown_df['measure'],
        x = breakdown_df['name'],
        textposition = "outside",
        text = [f"{'+' if v>0 and m!='total' else ''}{v}" for v, m in zip(breakdown_df['value'], breakdown_df['measure'])],
        y = breakdown_df['value'],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        # 颜色逻辑：涨是绿，跌是红，总计是蓝
        increasing = {"marker":{"color":"#2ecc71"}},
        decreasing = {"marker":{"color":"#e74c3c"}},
        totals = {"marker":{"color":"#3498db"}}
    ))
    
    fig_waterfall.update_layout(
        title = f"为什么 {selected_candidate} 得了 {candidate_data['total_score']} 分?",
        showlegend = False,
        height = 450,
        yaxis=dict(title="分数贡献", range=[0, 100])
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)

# --- 4. 右侧：技能匹配差距分析 (Skill Gap Analysis) ---
with col_skills:
    st.subheader("2. 技能匹配详情 (Skill Gap)")
    
    skills = candidate_data['skills']
    
    # 构造绘图数据
    skill_names = list(skills.keys())
    req_levels = [v['req'] for v in skills.values()] # JD要求
    act_levels = [v['act'] for v in skills.values()] # 实际掌握
    
    # 使用水平条形图对比
    fig_gap = go.Figure()
    
    # JD 要求 (灰色背景条)
    fig_gap.add_trace(go.Bar(
        y=skill_names,
        x=req_levels,
        name='JD 要求',
        orientation='h',
        marker=dict(color='rgba(189, 195, 199, 0.5)', line=dict(color='gray', width=1))
    ))
    
    # 候选人实际能力 (动态颜色)
    # 逻辑：如果 实际 >= 要求，绿色；否则 橙色/红色
    colors = []
    for s in skill_names:
        if skills[s]['act'] >= skills[s]['req']:
            colors.append('#2ecc71') # 达标-绿
        elif skills[s]['act'] == 0:
            colors.append('#e74c3c') # 缺失-红
        else:
            colors.append('#f39c12') # 差距-橙
            
    fig_gap.add_trace(go.Bar(
        y=skill_names,
        x=act_levels,
        name='候选人能力',
        orientation='h',
        marker=dict(color=colors),
        text=act_levels,
        textposition='auto'
    ))
    
    fig_gap.update_layout(
        title="JD要求(灰) vs 实际能力(彩)",
        barmode='overlay', # 叠加模式
        xaxis=dict(title="熟练度 (0-5)", range=[0, 6]),
        height=450,
        legend=dict(orientation="h", y=1.1)
    )
    
    st.plotly_chart(fig_gap, use_container_width=True)

# --- 5. 补充：自然语言解释 (NLG) ---
st.info(f"""
💡 **AI 分析总结**：
**{selected_candidate}** 的主要优势在于 **{breakdown_df.iloc[2]['name']}** (+{breakdown_df.iloc[2]['value']})。
需要注意的是，其 **{list(skills.keys())[2]}** 能力与岗位要求存在差距 (JD要求 {skills[list(skills.keys())[2]]['req']} vs 实际 {skills[list(skills.keys())[2]]['act']})，
且存在 **{breakdown_df.iloc[4]['name'] if breakdown_df.iloc[4]['value'] < 0 else ''}** 的风险因素，建议在面试中重点考察。
""")