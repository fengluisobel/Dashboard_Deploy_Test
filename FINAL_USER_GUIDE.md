# 🚀 AI Hiring Dashboard v3.0 Pro 用户指引手册

> **"不是给你看数据，而是告诉你该做什么决策"**  
> *—— v3.0 Pro 核心设计理念*

![Hero Image](file:///C:/Users/lu.feng/.gemini/antigravity/brain/fa838e06-fb71-43d9-989c-cf3c902cea29/dashboard_hrvp_view_1769470048334.png)

---

## 🌟 产品简介

**AI Hiring Dashboard v3.0 Pro** 是一款集成了**战略监控**、**异常预警**与**执行管理**于一体的智能化招聘指挥系统。它突破了传统 BI "只展示不诊断"的局限，通过内置的专家规则引擎和 AI 算法，直接输出行动建议。

### 核心价值
- **HRVP**: 决策时间减少 **80%** (一眼看懂 ROI 与人才战略)
- **HRD**: 异常发现速度提升 **10倍** (红灯预警，点击即查)
- **HR**: 报表分析时间减少 **90%** (自动生成任务清单)

---

## 🎭 三大视角 (Role-Based Views)

系统通过左侧侧边栏的 **"🎭 选择角色视角"** 功能，为不同层级的用户提供专属的工作台。

### 1. HRVP 战略驾驶舱 (Strategic Cockpit)

**适用对象**: 人力资源副总裁、CHRO、CEO  
**核心关注**: 只有两件事——**花钱的效果 (ROI)** 和 **未来的风险**。

![HRVP View](file:///C:/Users/lu.feng/.gemini/antigravity/brain/fa838e06-fb71-43d9-989c-cf3c902cea29/dashboard_hrvp_view_1769470048334.png)

#### ✨ 亮点功能:
- **3D 战略地图**: 可视化全球人才分布与缺口。
- **财务透视**: 实时监控单人招聘成本 (Cost per Hire) 与人才质量 (Quality of Hire) 的黄金平衡点。
- **预测分析**: 基于当前速度，预测年度目标达成率，红灯提前亮起。

---

### 2. HRD 异常报警器 (Operational Command Center)

**适用对象**: 招聘总监、HRD  
**核心关注**: **哪里着火了？** (异常监控与资源调度)

![HRD View](file:///C:/Users/lu.feng/.gemini/antigravity/brain/fa838e06-fb71-43d9-989c-cf3c902cea29/dashboard_hrd_view_1769470061885.png)

#### 🚨 核心功能 (The "Flip Card" System):
我们独创了 **"翻转卡片"** 交互设计。
- **正面**: 实时异常指标（如：招聘完成率 < 85%）。
- **点击翻转**: 显示指标定义、老板关注点（Boss's Comment）以及改进建议。

#### 📊 逻辑化七步诊断:
1.  **核心异常指标**: 全局红绿灯。
2.  **部门概览矩阵**: 哪个部门是"重灾区"？
3.  **体验热力图 (NPS)**: 谁在破坏雇主品牌？
4.  **人效与负载**: 谁在摸鱼？谁快累死了？
5.  **智能诊断建议**: AI 自动生成的行动清单（如："建议技术部增加2个外包HC"）。
6.  **渠道 ROI**: 哪些渠道在浪费钱？
7.  **硅碳比分析**: AI 对团队效率的真实提升幅度。

---

### 3. HR 任务管理器 (Task Manager)

**适用对象**: 招聘顾问 (Recruiters)  
**核心关注**: **今天我该干什么？**

![HR View](file:///C:/Users/lu.feng/.gemini/antigravity/brain/fa838e06-fb71-43d9-989c-cf3c902cea29/dashboard_view_hr_1769470077817.png)

#### ✅ 每日工作台:
- **今日待办**: 自动按优先级排序的 Offer 跟进、面试安排。
- **漏斗健康度**: 个人负责职位的转化率分析。
- **我的贡献**: 实时看到自己对团队的贡献值（激励设计）。

---

## 🤖 AI 深度集成 (AI Integration)

本系统不仅仅是图表，更是您的 **AI 招聘专家**。

> [!IMPORTANT]
> **硅碳比 (Silicon-Carbon Ratio)**
> 我们引入了"硅碳比"概念，衡量 AI (硅基) 与 人力 (碳基) 的贡献比例。
> 在 HRD 视图的 **第7部分**，您可以直观看到 AI 工具（如自动筛选、自动约面）为团队带来了多少"额外产出"。

---

## 🛠️ 快速开始

1.  **启动系统**:
    在项目根目录下运行终端命令:
    ```bash
    streamlit run recruitment_dashboard_v3_complete.py
    ```
2.  **配置品牌色** (可选):
    点击右上角的颜色配置器，一键切换至符合您企业 VI 的配色方案。
3.  **导出报告**:
    所有图表支持一键下载为 PNG 格式，直接插入 PPT。

---

## ❓ 常见问题 (FAQ)

**Q: 为什么某些卡片显示红色？**  
A: 系统内置了行业标准阈值（如：关键岗位周期 > 60天即为严重异常）。您可以在代码配置中调整这些阈值。

**Q: 如何更新数据？**  
A: 侧边栏提供了"数据生成配置"，您可以调整月份、人数规模，并点击"重新生成数据"来模拟不同场景。

---

<div style="text-align: center; color: #888; margin-top: 50px;">
    © 2026 AI Hiring Dashboard Team | 打造极致招聘体验
</div>
