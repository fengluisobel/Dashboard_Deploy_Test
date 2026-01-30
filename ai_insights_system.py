"""
AI 洞察系统 v3.0 Pro
智能分析招聘数据，生成可执行的洞察和建议

功能:
- 自动分析数据趋势
- 识别异常和风险点
- 生成可执行的改进建议
- 分角色定制洞察内容
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# ==========================================
# AI 洞察生成核心引擎
# ==========================================

class RecruitmentInsightsEngine:
    """
    招聘数据洞察生成引擎
    """

    def __init__(self, df):
        """
        初始化引擎

        Parameters:
        -----------
        df : pandas.DataFrame
            完整招聘数据
        """
        self.df = df
        self.insights = []

    def generate_all_insights(self, role='HRVP'):
        """
        生成所有洞察

        Parameters:
        -----------
        role : str
            角色类型 ('HRVP', 'HRD', 'HR')

        Returns:
        --------
        list of dict
            洞察列表
        """
        self.insights = []

        if role == 'HRVP':
            self._analyze_strategic_gaps()
            self._analyze_cost_quality_balance()
            self._analyze_talent_market_share()
            self._analyze_revenue_loss_risk()

        elif role == 'HRD':
            self._analyze_department_health()
            self._analyze_offer_renege_risk()
            self._analyze_team_productivity()
            self._analyze_funnel_anomalies()

        elif role == 'HR':
            self._analyze_personal_performance()
            self._analyze_conversion_rate()
            self._analyze_sla_progress()
            self._analyze_backlog_trend()

        return self.insights

    # ==========================================
    # HRVP 战略洞察
    # ==========================================

    def _analyze_strategic_gaps(self):
        """分析关键战略岗位达成率缺口"""
        avg_fill_rate = self.df['关键战略岗位按时达成率_%'].mean()
        target = 85.0

        if avg_fill_rate < target:
            gap = target - avg_fill_rate

            insight = {
                'type': 'critical' if gap > 15 else 'warning',
                'category': '战略交付',
                'title': '关键战略岗位达成率未达标',
                'finding': f"当前达成率 {avg_fill_rate:.1f}%，低于目标 {target}%，缺口 {gap:.1f}%",
                'impact': f"业务战略落地速度受阻，预计影响 {int(gap * 0.5)} 个关键岗位",
                'root_cause': self._identify_fill_rate_bottleneck(),
                'recommendation': [
                    "建立P0级岗位快速通道，专人专项推进",
                    f"增加预算 {int(gap * 10000)}元用于猎头资源",
                    "与业务部门重新对齐需求，避免职位描述偏差"
                ],
                'metric_key': '关键战略岗位按时达成率_%'
            }

            self.insights.append(insight)

        else:
            insight = {
                'type': 'success',
                'category': '战略交付',
                'title': '关键战略岗位达成率健康',
                'finding': f"当前达成率 {avg_fill_rate:.1f}%，超过目标 {target}%",
                'impact': "业务战略落地有力支撑",
                'recommendation': [
                    "继续保持当前招聘策略",
                    "总结成功经验，形成方法论复制到其他岗位"
                ],
                'metric_key': '关键战略岗位按时达成率_%'
            }

            self.insights.append(insight)

    def _identify_fill_rate_bottleneck(self):
        """识别达成率瓶颈"""
        avg_ttf = self.df['平均招聘周期_天'].mean()
        avg_approval = self.df['审批耗时_天'].mean()
        avg_sourcing = self.df['寻访耗时_天'].mean()

        bottlenecks = []

        if avg_approval > 7:
            bottlenecks.append(f"审批流程慢 ({avg_approval:.0f}天)")
        if avg_sourcing > 15:
            bottlenecks.append(f"候选人寻访慢 ({avg_sourcing:.0f}天)")
        if avg_ttf > 45:
            bottlenecks.append(f"整体到岗周期过长 ({avg_ttf:.0f}天)")

        return "、".join(bottlenecks) if bottlenecks else "各环节正常，可能是JD要求过高"

    def _analyze_cost_quality_balance(self):
        """分析成本与质量平衡"""
        avg_cost = self.df['单次招聘成本_元'].mean()
        avg_quality = self.df['高绩效员工占比_%'].mean()

        cost_target = 10000
        quality_target = 70.0

        if avg_cost > cost_target and avg_quality < quality_target:
            insight = {
                'type': 'critical',
                'category': '成本控制',
                'title': '高成本低质量 - 严重问题',
                'finding': f"成本 {avg_cost:.0f}元 > 目标 {cost_target}元，质量 {avg_quality:.1f}% < 目标 {quality_target}%",
                'impact': "招聘ROI极低，财务和业务双重压力",
                'root_cause': "渠道选择不当，或面试标准不清晰",
                'recommendation': [
                    "立即优化渠道结构，减少低效猎头使用",
                    "培训面试官，提升人岗匹配精准度",
                    "考虑建立内部推荐激励机制（降成本提质量）"
                ],
                'metric_key': '单次招聘成本_元'
            }

            self.insights.append(insight)

        elif avg_cost < cost_target and avg_quality >= quality_target:
            insight = {
                'type': 'success',
                'category': '成本控制',
                'title': '低成本高质量 - 最优状态',
                'finding': f"成本 {avg_cost:.0f}元，质量 {avg_quality:.1f}%，ROI极佳",
                'impact': "招聘效能行业领先",
                'recommendation': [
                    "总结最佳实践，形成标准化流程",
                    "向其他部门推广成功经验"
                ],
                'metric_key': '单次招聘成本_元'
            }

            self.insights.append(insight)

    def _analyze_talent_market_share(self):
        """分析人才市场占有率"""
        avg_share = self.df['人才市场占有率_%'].mean()
        target = 25.0

        if avg_share < 15:
            insight = {
                'type': 'warning',
                'category': '雇主品牌',
                'title': '人才市场竞争力不足',
                'finding': f"市场占有率 {avg_share:.1f}%，低于良好线 15%",
                'impact': "难以吸引竞对核心人才，雇主品牌弱势",
                'root_cause': "薪酬竞争力不足，或雇主品牌知名度低",
                'recommendation': [
                    "提升薪酬分位值（建议P50 -> P65）",
                    "加大雇主品牌宣传（LinkedIn、脉脉）",
                    "建立竞对人才地图，精准挖角"
                ],
                'metric_key': '人才市场占有率_%'
            }

            self.insights.append(insight)

    def _analyze_revenue_loss_risk(self):
        """分析收入损失风险"""
        total_loss = self.df['空缺岗位收入损失_万元'].sum()

        if total_loss > 500:
            insight = {
                'type': 'critical',
                'category': '财务风控',
                'title': '空缺岗位收入损失严重',
                'finding': f"累计损失 {total_loss:.0f}万元，超过危险线 500万",
                'impact': "需向董事会解释，影响公司财务表现",
                'root_cause': "关键岗位空窗期过长",
                'recommendation': [
                    "建立紧急响应机制，P0岗位7天内必须启动",
                    "考虑临时外包/顾问方案填补空窗期",
                    "与CFO沟通，量化损失推动资源投入"
                ],
                'metric_key': '空缺岗位收入损失_万元'
            }

            self.insights.append(insight)

    # ==========================================
    # HRD 异常洞察
    # ==========================================

    def _analyze_department_health(self):
        """分析部门健康度"""
        dept_health = self.df.groupby('部门')['部门健康度_得分'].mean()
        unhealthy_depts = dept_health[dept_health < 60]

        if not unhealthy_depts.empty:
            worst_dept = unhealthy_depts.idxmin()
            worst_score = unhealthy_depts.min()

            insight = {
                'type': 'critical',
                'category': '异常管理',
                'title': f'部门健康度预警 - {worst_dept}',
                'finding': f"{worst_dept} 健康度 {worst_score:.0f}分，低于及格线60分",
                'impact': "该部门招聘运营严重问题，影响业务推进",
                'root_cause': self._diagnose_department_issues(worst_dept),
                'recommendation': [
                    f"立即约谈 {worst_dept} 负责人，了解具体困难",
                    "分析该部门到岗周期逾期原因，可能需要调整JD或薪资",
                    "考虑增派招聘顾问支援"
                ],
                'metric_key': '部门健康度_得分'
            }

            self.insights.append(insight)

    def _diagnose_department_issues(self, dept):
        """诊断部门问题"""
        dept_data = self.df[self.df['部门'] == dept]

        issues = []

        if dept_data['到岗周期逾期率_%'].mean() > 25:
            issues.append("到岗周期严重逾期")
        if dept_data['Offer毁约率_%'].mean() > 10:
            issues.append("Offer毁约率高")
        if dept_data['投诉量'].sum() > 10:
            issues.append("候选人投诉多")

        return "、".join(issues) if issues else "综合因素"

    def _analyze_offer_renege_risk(self):
        """分析Offer毁约风险"""
        avg_renege = self.df['Offer毁约率_%'].mean()

        if avg_renege > 10:
            insight = {
                'type': 'critical',
                'category': '风险预警',
                'title': 'Offer毁约率严重超标',
                'finding': f"毁约率 {avg_renege:.1f}%，超过危险线 10%",
                'impact': "煮熟的鸭子飞了，严重打击团队士气",
                'root_cause': self._analyze_renege_reasons(),
                'recommendation': [
                    "缩短Offer发放到入职的时间间隔（建议<7天）",
                    "提升薪酬竞争力，减少被竞对截胡",
                    "入职前保持高频沟通，增强归属感"
                ],
                'metric_key': 'Offer毁约率_%'
            }

            self.insights.append(insight)

    def _analyze_renege_reasons(self):
        """分析毁约原因"""
        salary_issue = self.df['Offer拒绝_薪资低_%'].mean()
        competitor_issue = self.df['Offer拒绝_竞对截胡_%'].mean()

        if salary_issue > competitor_issue:
            return f"薪资竞争力不足 ({salary_issue:.1f}%)"
        else:
            return f"被竞对截胡 ({competitor_issue:.1f}%)"

    def _analyze_team_productivity(self):
        """分析团队生产力"""
        recruiter_productivity = self.df.groupby('招聘顾问')['招聘顾问人效_人'].mean()

        underperformers = recruiter_productivity[recruiter_productivity < 5]
        overloaded = self.df.groupby('招聘顾问')['人均负责职位数'].mean()
        overloaded = overloaded[overloaded > 15]

        if not underperformers.empty:
            insight = {
                'type': 'warning',
                'category': '团队效率',
                'title': '部分招聘顾问人效不足',
                'finding': f"{len(underperformers)}人人效低于5人/月",
                'impact': "团队整体产能受限",
                'root_cause': "能力不足或负载分配不均",
                'recommendation': [
                    "安排1v1辅导，提升个人能力",
                    "重新分配职位负载，平衡团队工作量",
                    f"高负载人员: {', '.join(overloaded.index.tolist() if not overloaded.empty else [])}"
                ],
                'metric_key': '招聘顾问人效_人'
            }

            self.insights.append(insight)

    def _analyze_funnel_anomalies(self):
        """分析漏斗异常"""
        anomaly_count = self.df['漏斗异常_标志'].sum()

        if anomaly_count > 0:
            insight = {
                'type': 'warning',
                'category': '流程监控',
                'title': f'发现 {int(anomaly_count)} 处漏斗异常',
                'finding': "部分环节转化率显著低于历史均值",
                'impact': "招聘效率受损，需要介入修正",
                'root_cause': "面试标准变化，或简历质量下降",
                'recommendation': [
                    "与用人经理对齐面试标准",
                    "优化简历筛选标准，提升推荐质量"
                ],
                'metric_key': '漏斗异常_标志'
            }

            self.insights.append(insight)

    # ==========================================
    # HR 个人洞察
    # ==========================================

    def _analyze_personal_performance(self):
        """分析个人绩效"""
        # 这里假设分析第一个招聘顾问
        recruiter = self.df['招聘顾问'].iloc[0]
        personal_data = self.df[self.df['招聘顾问'] == recruiter]

        avg_productivity = personal_data['招聘顾问人效_人'].mean()

        if avg_productivity < 5:
            insight = {
                'type': 'warning',
                'category': '个人绩效',
                'title': '个人人效需要提升',
                'finding': f"当前人效 {avg_productivity:.1f}人/月，低于及格线 5人/月",
                'impact': "可能影响个人绩效评估和奖金",
                'root_cause': "转化率低或负载不足",
                'recommendation': [
                    "提升简历推荐精准度，减少无效推荐",
                    "主动向主管申请更多职位负载",
                    "学习高人效同事的工作方法"
                ],
                'metric_key': '招聘顾问人效_人'
            }

            self.insights.append(insight)

    def _analyze_conversion_rate(self):
        """分析转化率"""
        recruiter = self.df['招聘顾问'].iloc[0]
        personal_data = self.df[self.df['招聘顾问'] == recruiter]

        avg_conversion = personal_data['个人转化率_%'].mean()

        if avg_conversion < 20:
            insight = {
                'type': 'warning',
                'category': '自我修正',
                'title': '简历推荐转化率过低',
                'finding': f"转化率 {avg_conversion:.1f}%，低于及格线 20%",
                'impact': "推荐精准度不足，浪费用人经理时间",
                'root_cause': "对JD理解不深，或筛选标准过宽",
                'recommendation': [
                    "与用人经理深入沟通，重新对焦JD要求",
                    "提升简历筛选标准，宁缺毋滥",
                    "学习高转化率同事的筛选方法"
                ],
                'metric_key': '个人转化率_%'
            }

            self.insights.append(insight)

    def _analyze_sla_progress(self):
        """分析SLA进度"""
        recruiter = self.df['招聘顾问'].iloc[0]
        personal_data = self.df[self.df['招聘顾问'] == recruiter]

        avg_progress = personal_data['月度SLA达成进度_%'].mean()

        if avg_progress < 90:
            insight = {
                'type': 'warning',
                'category': '结果交付',
                'title': '月度SLA进度预警',
                'finding': f"当前进度 {avg_progress:.0f}%，低于达标线 90%",
                'impact': "月度绩效考核可能不达标",
                'root_cause': "入职数不足，需要加速推进",
                'recommendation': [
                    "优先处理停滞候选人，加快流程推进",
                    "增加每日面试安排量",
                    "主动跟进Offer确认，防止毁约"
                ],
                'metric_key': '月度SLA达成进度_%'
            }

            self.insights.append(insight)

    def _analyze_backlog_trend(self):
        """分析待办趋势"""
        recruiter = self.df['招聘顾问'].iloc[0]
        personal_data = self.df[self.df['招聘顾问'] == recruiter]

        avg_backlog = personal_data['待处理候选人数'].mean()

        if avg_backlog > 25:
            insight = {
                'type': 'critical',
                'category': '工作负荷',
                'title': '工作负荷过载',
                'finding': f"平均待处理 {avg_backlog:.0f}人，超过过载线 25人",
                'impact': "工作负荷过重，可能导致服务质量下降",
                'root_cause': "职位负载过多，或处理效率不足",
                'recommendation': [
                    "向主管申请支援或减少职位负载",
                    "优化工作流程，提升处理效率",
                    "使用工具自动化部分重复性工作"
                ],
                'metric_key': '待处理候选人数'
            }

            self.insights.append(insight)


# ==========================================
# 洞察展示组件
# ==========================================

def render_insights_panel(df, role='HRVP'):
    """
    渲染洞察面板

    Parameters:
    -----------
    df : pandas.DataFrame
        完整招聘数据
    role : str
        角色类型
    """
    import streamlit as st

    # 生成洞察
    engine = RecruitmentInsightsEngine(df)
    insights = engine.generate_all_insights(role=role)

    if not insights:
        st.success("✅ 暂无重要洞察，所有指标健康！")
        return

    st.subheader("🤖 AI 智能洞察")

    # 按类型分组
    critical_insights = [i for i in insights if i.get('type') == 'critical']
    warning_insights = [i for i in insights if i.get('type') == 'warning']
    success_insights = [i for i in insights if i.get('type') == 'success']

    # 展示严重洞察
    if critical_insights:
        st.markdown("### 🔴 严重问题 (Critical)")
        for insight in critical_insights:
            with st.expander(f"🔴 {insight['title']}", expanded=True):
                st.markdown(f"**📊 发现**: {insight['finding']}")
                st.markdown(f"**💥 影响**: {insight['impact']}")
                if 'root_cause' in insight:
                    st.markdown(f"**🔍 根因**: {insight['root_cause']}")

                st.markdown("**💡 建议行动**:")
                for idx, rec in enumerate(insight['recommendation'], 1):
                    st.markdown(f"{idx}. {rec}")

    # 展示警告洞察
    if warning_insights:
        st.markdown("### 🟡 需要关注 (Warning)")
        for insight in warning_insights:
            with st.expander(f"🟡 {insight['title']}"):
                st.markdown(f"**📊 发现**: {insight['finding']}")
                st.markdown(f"**💥 影响**: {insight['impact']}")
                if 'root_cause' in insight:
                    st.markdown(f"**🔍 根因**: {insight['root_cause']}")

                st.markdown("**💡 建议行动**:")
                for idx, rec in enumerate(insight['recommendation'], 1):
                    st.markdown(f"{idx}. {rec}")

    # 展示成功洞察
    if success_insights:
        st.markdown("### 🟢 表现优秀 (Success)")
        for insight in success_insights:
            with st.expander(f"🟢 {insight['title']}"):
                st.markdown(f"**📊 发现**: {insight['finding']}")
                st.markdown(f"**💥 影响**: {insight['impact']}")

                st.markdown("**💡 建议**:")
                for idx, rec in enumerate(insight['recommendation'], 1):
                    st.markdown(f"{idx}. {rec}")


# ==========================================
# 测试入口
# ==========================================

if __name__ == '__main__':
    import streamlit as st
    from data_generator_complete import generate_complete_recruitment_data

    st.set_page_config(page_title="AI 洞察系统测试", layout="wide")

    st.title("🤖 AI 洞察系统测试")

    # 生成测试数据
    df = generate_complete_recruitment_data(months=12, recruiters=5, departments=5)

    # 选择角色
    role = st.selectbox("选择角色", ["HRVP", "HRD", "HR"])

    st.markdown("---")

    # 渲染洞察
    render_insights_panel(df, role=role)

