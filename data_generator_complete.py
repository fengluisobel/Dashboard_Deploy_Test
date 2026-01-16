"""
招聘数据驾驶舱 v3.0 Pro - 完整数据生成模块
包含所有81个指标的完整实现
基于 BI指标体系.json 和 招聘指标 层级.md
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_complete_recruitment_data(months=12, recruiters=5, departments=5):
    """
    生成完整的企业级招聘数据
    包含所有81个指标 (L1: 5个, L2: 27个, L3: 54个)
    """
    np.random.seed(42)

    # 时间维度
    start_date = datetime(2025, 1, 1)
    date_range = pd.date_range(start=start_date, periods=months, freq='MS')

    # 人员维度
    recruiter_names = ['张伟', '李娜', '王芳', '刘洋', '陈静'][:recruiters]
    dept_names = ['技术部', '产品部', '市场部', '销售部', '运营部'][:departments]

    # 职级
    levels = ['初级', '中级', '高级', '专家', '管理层', 'P0战略级']

    # 渠道
    channels = ['招聘网站', '猎头', '内推', '校园招聘', '社交媒体', 'RPO']

    all_data = []

    for month_date in date_range:
        for recruiter in recruiter_names:
            for dept in dept_names:
                # 基础维度
                row = {
                    '月份': month_date,
                    '年份': month_date.year,
                    '季度': f'Q{(month_date.month-1)//3 + 1}',
                    '招聘顾问': recruiter,
                    '部门': dept,
                    '职级': np.random.choice(levels, p=[0.3, 0.3, 0.2, 0.1, 0.08, 0.02]),
                    '渠道': np.random.choice(channels, p=[0.25, 0.20, 0.25, 0.15, 0.10, 0.05]),
                }

                # ==========================================
                # 维度 A: 招聘速度与效率 (10个L2 + 10个L3)
                # ==========================================

                # L2: 平均招聘周期 (Time to Fill)
                row['平均招聘周期_天'] = np.random.randint(20, 65)
                # L3: 审批耗时
                row['审批耗时_天'] = np.random.randint(2, 12)
                # L3: 寻访耗时 (Time to Source)
                row['寻访耗时_天'] = np.random.randint(5, 25)

                # L2: 平均录用速度 (Time to Hire)
                row['平均录用速度_天'] = np.random.randint(15, 50)
                # L3: 流程停滞天数 (Stuck Days)
                row['流程停滞天数'] = np.random.randint(0, 8)

                # L2: 阶段周转时间 (Time in Stage)
                row['阶段周转时间_天'] = np.random.randint(3, 15)
                # L3: 面试反馈速度
                row['面试反馈速度_小时'] = np.random.randint(12, 96)

                # L2: 招聘及时率 (On-time Completion)
                row['招聘及时率_%'] = np.random.uniform(65, 98)
                # L3: 逾期职位数 (Overdue Reqs)
                row['逾期职位数'] = np.random.randint(0, 8)

                # L2: 职位老化率 (Aging Requisitions)
                row['职位老化率_%'] = np.random.uniform(5, 30)
                # L3: 重启职位数
                row['重启职位数'] = np.random.randint(0, 5)

                # ==========================================
                # 维度 B: 招聘质量与结果 (7个L2 + 14个L3)
                # ==========================================

                # L2: 试用期转正率 (Probation Pass Rate)
                row['试用期转正率_%'] = np.random.uniform(75, 98)
                # L3: 试用期延长率
                row['试用期延长率_%'] = np.random.uniform(2, 18)
                # L3: 试用期失败归因_能力
                row['试用期失败_能力不胜任_%'] = np.random.uniform(40, 70)
                # L3: 试用期失败归因_价值观
                row['试用期失败_价值观不合_%'] = np.random.uniform(10, 30)
                # L3: 试用期失败归因_其他
                row['试用期失败_其他_%'] = np.random.uniform(10, 30)

                # L2: 新员工首年绩效 (First Year Performance)
                row['新员工首年绩效_分'] = np.random.uniform(3.2, 4.8)
                # L3: 绩效校准差异
                row['绩效校准差异_分'] = np.random.uniform(0.1, 1.0)

                # L2: 新员工早期离职率 (Early Turnover)
                row['新员工早期离职率_%'] = np.random.uniform(3, 22)
                # L3: 首月流失率 (Infant Mortality)
                row['首月流失率_%'] = np.random.uniform(1, 10)

                # L2: 用人经理满意度 (Hiring Manager Satisfaction)
                row['用人经理满意度_分'] = np.random.uniform(3.0, 5.0)
                # L3: 简历质量满意度
                row['简历质量满意度_分'] = np.random.uniform(2.8, 5.0)

                # L2: 关键岗位达成率 (Critical Role Fill)
                row['关键岗位达成率_%'] = np.random.uniform(70, 100)
                # L3: 核心岗空窗期
                row['核心岗空窗期_天'] = np.random.randint(10, 90)

                # L2: 入职职级分布 (New Hire by Level)
                row['入职人数_初级'] = np.random.randint(0, 5)
                row['入职人数_中级'] = np.random.randint(0, 4)
                row['入职人数_高级'] = np.random.randint(0, 3)
                row['入职人数_专家'] = np.random.randint(0, 2)
                row['入职人数_管理层'] = np.random.randint(0, 2)
                row['入职人数_P0战略级'] = np.random.randint(0, 1)

                # ==========================================
                # 维度 C: 漏斗与转化 (5个L2 + 12个L3)
                # ==========================================

                # L2: 录用接受率 (Offer Acceptance Rate)
                row['录用接受率_%'] = np.random.uniform(55, 92)
                # L3: 薪酬竞争力_被拒Offer薪资分位值
                row['被拒Offer薪资分位值'] = np.random.uniform(40, 75)
                # L3: Offer拒绝归因_薪资低
                row['Offer拒绝_薪资低_%'] = np.random.uniform(30, 60)
                # L3: Offer拒绝归因_竞对截胡
                row['Offer拒绝_竞对截胡_%'] = np.random.uniform(15, 40)
                # L3: Offer拒绝归因_路程远
                row['Offer拒绝_路程远_%'] = np.random.uniform(5, 20)
                # L3: Offer拒绝归因_其他
                row['Offer拒绝_其他_%'] = np.random.uniform(5, 25)

                # L2: 全流程转化率 (Pass-through Rates)
                row['全流程转化率_%'] = np.random.uniform(8, 25)
                # L3: 简历初筛通过率
                row['简历初筛通过率_%'] = np.random.uniform(15, 45)
                # L3: 面试通过率
                row['面试通过率_%'] = np.random.uniform(20, 60)

                # L2: 渠道有效性 (Source Effectiveness)
                row['渠道有效性_得分'] = np.random.uniform(60, 95)
                # L3: 渠道简历转化率
                row['渠道简历转化率_%'] = np.random.uniform(8, 38)

                # L2: 候选人库覆盖率 (Pipeline Coverage)
                row['候选人库覆盖率'] = np.random.uniform(1.2, 4.5)
                # L3: 人才地图完备度
                row['人才地图完备度_%'] = np.random.uniform(45, 95)

                # ==========================================
                # 维度 D: 成本与生产力 (4个L2 + 8个L3)
                # ==========================================

                # L2: 单次招聘成本 (Cost per Hire)
                row['单次招聘成本_元'] = np.random.randint(3000, 25000)
                # L3: 猎头费用占比
                row['猎头费用占比_%'] = np.random.uniform(18, 55)
                # L3: 渠道单价
                row['渠道单价_元'] = np.random.randint(80, 1200)

                # L2: 招聘顾问人效 (Recruiter Productivity)
                row['招聘顾问人效_人'] = np.random.randint(3, 15)
                # L3: 人均负责职位数 (Req Load)
                row['人均负责职位数'] = np.random.randint(5, 20)

                # L2: 招聘预算执行率 (Budget Utilization)
                row['招聘预算执行率_%'] = np.random.uniform(75, 108)
                # L3: 平均定薪涨幅
                row['平均定薪涨幅_%'] = np.random.uniform(8, 35)

                # ==========================================
                # 维度 E: 体验与品牌 (5个L2 + 10个L3)
                # ==========================================

                # L2: 候选人净推荐值 (Candidate NPS)
                row['候选人NPS'] = np.random.randint(-25, 65)
                # L3: 面试官专业度评分
                row['面试官专业度评分'] = np.random.uniform(3.0, 5.0)

                # L2: 申请完成率 (Application Completion Rate)
                row['申请完成率_%'] = np.random.uniform(55, 92)
                # L3: 移动端申请占比
                row['移动端申请占比_%'] = np.random.uniform(28, 75)

                # L2: 幽灵率 (Ghosting Rate)
                row['幽灵率_%'] = np.random.uniform(5, 28)
                # L3: 面试爽约率
                row['面试爽约率_%'] = np.random.uniform(3, 20)

                # L2: 雇主品牌触达 (Brand Reach)
                row['雇主品牌触达_PV'] = np.random.randint(3000, 80000)
                # L3: 职位点击申请率
                row['职位点击申请率_%'] = np.random.uniform(12, 50)

                # L2: 多元化候选人占比 (Diversity Slate)
                row['多元化候选人占比_%'] = np.random.uniform(22, 58)
                # L3: Offer多元化率
                row['Offer多元化率_%'] = np.random.uniform(18, 55)

                # ==========================================
                # HRVP 战略指标 (基于BI指标体系.json)
                # ==========================================

                # 关键战略岗位按时达成率
                row['关键战略岗位按时达成率_%'] = np.random.uniform(70, 96)

                # 空缺岗位预期收入损失
                row['空缺岗位收入损失_万元'] = np.random.randint(30, 800)

                # 高绩效员工渠道来源占比 (S/A级员工比例)
                row['高绩效员工占比_%'] = np.random.uniform(55, 88)
                row['高绩效员工_猎头来源_%'] = np.random.uniform(25, 50)
                row['高绩效员工_内推来源_%'] = np.random.uniform(30, 55)
                row['高绩效员工_自招来源_%'] = np.random.uniform(15, 30)

                # 关键人才市场占有率
                row['人才市场占有率_%'] = np.random.uniform(12, 38)
                row['竞对挖角成功数'] = np.random.randint(0, 5)
                row['竞对流失估算数'] = np.random.randint(10, 50)

                # 组织人才结构健康度
                row['组织结构健康度_得分'] = np.random.uniform(65, 95)
                row['高P占比_%'] = np.random.uniform(8, 25)
                row['初级占比_%'] = np.random.uniform(30, 60)

                # ==========================================
                # HRD 异常管理指标 (基于BI指标体系.json)
                # ==========================================

                # 部门招聘健康度
                row['TTF超标率_%'] = np.random.uniform(8, 38)
                row['面试通过率异常_标志'] = np.random.choice([0, 0, 0, 1], p=[0.7, 0.1, 0.1, 0.1])
                row['投诉量'] = np.random.randint(0, 8)
                row['部门健康度_得分'] = np.random.uniform(60, 98)

                # Offer毁约率
                row['Offer毁约率_%'] = np.random.uniform(2, 18)
                row['Offer毁约数'] = np.random.randint(0, 5)

                # 供应商绩效
                row['猎头转正率_%'] = np.random.uniform(70, 95)
                row['猎头绩效_得分'] = np.random.uniform(60, 95)

                # 漏斗转化率异常
                row['漏斗异常_标志'] = np.random.choice([0, 0, 0, 1], p=[0.75, 0.1, 0.1, 0.05])
                row['漏斗异常_环节'] = np.random.choice(['简历筛选', '初面', '二面', '终面', 'Offer'], p=[0.3, 0.25, 0.2, 0.15, 0.1])

                # ==========================================
                # HR 执行层指标 (基于BI指标体系.json)
                # ==========================================

                # 今日待办
                row['待处理候选人数'] = np.random.randint(3, 35)
                row['待处理_超24小时数'] = np.random.randint(0, 15)
                row['待处理_超48小时数'] = np.random.randint(0, 8)
                row['待处理_超72小时数'] = np.random.randint(0, 5)

                # 即将到来的面试
                row['今日面试数'] = np.random.randint(0, 10)
                row['明日面试数'] = np.random.randint(0, 12)
                row['未来48小时面试数'] = np.random.randint(0, 20)
                row['面试确认率_%'] = np.random.uniform(75, 98)

                # 个人漏斗转化率
                row['个人推荐简历数'] = np.random.randint(20, 80)
                row['个人简历通过数'] = np.random.randint(5, 30)
                row['个人转化率_%'] = np.random.uniform(15, 45)

                # 个人月度SLA
                row['月度目标入职数'] = np.random.randint(5, 15)
                row['月度已入职数'] = np.random.randint(0, 18)
                row['月度SLA达成进度_%'] = np.random.uniform(50, 120)

                # ==========================================
                # 辅助字段
                # ==========================================
                row['总招聘人数'] = (row['入职人数_初级'] + row['入职人数_中级'] +
                                   row['入职人数_高级'] + row['入职人数_专家'] +
                                   row['入职人数_管理层'] + row['入职人数_P0战略级'])
                row['发出Offer数'] = np.random.randint(row['总招聘人数'], row['总招聘人数'] + 8)
                row['接受Offer数'] = row['总招聘人数']

                # 简历量
                row['收到简历总数'] = np.random.randint(100, 500)
                row['初筛通过简历数'] = int(row['收到简历总数'] * row['简历初筛通过率_%'] / 100)
                row['面试人数'] = int(row['初筛通过简历数'] * 0.7)

                all_data.append(row)

    df = pd.DataFrame(all_data)

    # 数据后处理和一致性修正
    df['录用接受率_%'] = (df['接受Offer数'] / df['发出Offer数']) * 100
    df['全流程转化率_%'] = (df['总招聘人数'] / df['收到简历总数']) * 100

    return df


# 指标元数据定义
METRICS_METADATA = {
    # HRVP 战略层指标
    'hrvp': {
        '关键战略岗位按时达成率_%': {
            'name': '关键战略岗位按时达成率',
            'name_en': 'Critical Role Fill Rate',
            'category': '战略交付',
            'formula': '按时入职的P0级人员数 / P0级招聘计划总数',
            'definition': '仅统计对公司战略有重大影响的岗位(如新业务线负责人、首席架构师)',
            'boss_comment': '别告诉我招了多少个前台,我只想知道那个能带队打仗的VP到了没有',
            'benchmark': {'优秀': '>85%', '良好': '75-85%', '需改进': '<75%'},
            'review_cadence': 'Monthly'
        },
        '空缺岗位收入损失_万元': {
            'name': '空缺岗位预期收入损失',
            'name_en': 'Revenue Loss Risk / Cost of Vacancy',
            'category': '财务风控',
            'formula': 'Σ(关键岗位每日预估产值 × 空窗天数)',
            'definition': '将关键岗位的空窗期转化为财务损失金额',
            'boss_comment': "把'招人慢'变成'亏钱',业务部门就会配合你了",
            'benchmark': {'优秀': '<200万', '警告': '200-500万', '严重': '>500万'},
            'review_cadence': 'Monthly'
        },
        '高绩效员工占比_%': {
            'name': '高绩效员工渠道来源占比',
            'name_en': 'Quality of Source - High Performers',
            'category': '人才质量',
            'formula': '绩效评估为S/A级的员工比例',
            'definition': '分析哪种渠道带来的员工在入职一年后表现最好',
            'boss_comment': '不要为了省钱而用便宜渠道,如果猎头招的人能多赚100万,就用猎头',
            'benchmark': {'优秀': '>70%', '良好': '60-70%', '需改进': '<60%'},
            'review_cadence': 'Quarterly'
        },
        '人才市场占有率_%': {
            'name': '关键人才市场占有率',
            'name_en': 'Competitor Talent Share',
            'category': '雇主品牌',
            'formula': '来自核心竞对的入职人数 / 核心竞对流失总人数(估算)',
            'definition': '我们在多大程度上成功挖角了竞争对手的核心人才',
            'boss_comment': 'NPS太虚,我要看我们是否削弱了对手的战斗力',
            'benchmark': {'优秀': '>25%', '良好': '15-25%', '需改进': '<15%'},
            'review_cadence': 'Quarterly'
        },
        '单次招聘成本_元': {
            'name': '单次招聘成本',
            'name_en': 'Cost per Hire',
            'category': '成本控制',
            'formula': '(外部渠道费+猎头费+内部团队成本) / 入职人数',
            'definition': '招募一名新员工的平均费用',
            'boss_comment': '控制成本但不能为了省钱降低质量',
            'benchmark': {'优秀': '<10K', '良好': '10-15K', '需改进': '>15K'},
            'review_cadence': 'Monthly'
        }
    },

    # HRD 管理层指标
    'hrd': {
        'TTF超标率_%': {
            'name': 'TTF超标率',
            'name_en': 'TTF Overdue Rate',
            'category': '异常管理',
            'formula': 'TTF>SLA天数的职位数 / 总职位数',
            'definition': '招聘周期超过承诺SLA的职位比例',
            'boss_comment': '不要给我看平均数,告诉我哪个部门出问题了',
            'benchmark': {'正常': '<15%', '警告': '15-25%', '严重': '>25%'},
            'review_cadence': 'Weekly'
        },
        'Offer毁约率_%': {
            'name': 'Offer毁约率',
            'name_en': 'Offer Renege Rate',
            'category': '风险预警',
            'formula': '接受Offer后未入职人数 / 接受Offer总数',
            'definition': '衡量"临门一脚"的失败率',
            'boss_comment': '煮熟的鸭子飞了是最伤士气的,必须严控',
            'benchmark': {'正常': '<6%', '警告': '6-10%', '严重': '>10%'},
            'review_cadence': 'Monthly'
        },
        '招聘顾问人效_人': {
            'name': '招聘团队人均产能',
            'name_en': 'Req Closed per Recruiter',
            'category': '团队效率',
            'formula': '成功关闭职位数 / 招聘专员人数',
            'definition': '衡量团队内部的工作负载分布',
            'boss_comment': '谁在摸鱼?谁快累死了?动态调整HC分配',
            'benchmark': {'优秀': '>8人/月', '良好': '5-8人/月', '需改进': '<5人/月'},
            'review_cadence': 'Monthly'
        },
        '投诉量': {
            'name': '候选人投诉量',
            'name_en': 'Candidate Complaints',
            'category': '服务质量',
            'formula': '本期收到的候选人投诉数量',
            'definition': '反映招聘服务质量和候选人体验',
            'boss_comment': '投诉就是服务质量的直接反馈',
            'benchmark': {'正常': '<5件', '警告': '5-10件', '严重': '>10件'},
            'review_cadence': 'Weekly'
        }
    },

    # HR 执行层指标
    'hr': {
        '待处理候选人数': {
            'name': '今日待办候选人数',
            'name_en': 'Action Required Candidates',
            'category': '每日作战',
            'formula': 'Count(状态=待处理 AND 停留时间>24h)',
            'definition': '列出所有卡在待筛选、待安排环节超过SLA时限的候选人',
            'boss_comment': '别盯着报表看,去干活!把这个人处理掉',
            'benchmark': {'正常': '<15人', '繁忙': '15-25人', '过载': '>25人'},
            'review_cadence': 'Daily'
        },
        '流程停滞天数': {
            'name': '流程停滞天数',
            'name_en': 'Stuck Days',
            'category': '流程卫生',
            'formula': '候选人在当前状态的停留天数',
            'definition': '监控每一个候选人的"静止时间"',
            'boss_comment': '时间就是生命,拖三天人家就去别家入职了',
            'benchmark': {'正常': '<3天', '警告': '3-5天', '严重': '>5天'},
            'review_cadence': 'Daily'
        },
        '今日面试数': {
            'name': '即将到来的面试',
            'name_en': 'Upcoming Interviews',
            'category': '日程管理',
            'formula': '未来24/48小时内的面试安排列表',
            'definition': '确保面试官和候选人都已确认出席',
            'boss_comment': '基本功不能丢',
            'benchmark': {'正常': '确认率>90%', '风险': '确认率80-90%', '危险': '确认率<80%'},
            'review_cadence': 'Daily'
        },
        '个人转化率_%': {
            'name': '个人漏斗转化率',
            'name_en': 'Personal Conversion Rate',
            'category': '自我修正',
            'formula': '我推荐的简历数 / 经理通过数',
            'definition': '衡量个人推人的"精准度"',
            'boss_comment': '不要做简历搬运工,要做人才顾问',
            'benchmark': {'优秀': '>30%', '良好': '20-30%', '需改进': '<20%'},
            'review_cadence': 'Weekly'
        },
        '月度SLA达成进度_%': {
            'name': '个人月度SLA达成进度',
            'name_en': 'SLA Progress',
            'category': '结果交付',
            'formula': '本月已入职数 / 本月承诺目标数',
            'definition': '最直观的业绩进度条',
            'boss_comment': '结果导向',
            'benchmark': {'优秀': '>100%', '达标': '90-100%', '需冲刺': '<90%'},
            'review_cadence': 'Weekly'
        }
    }
}


if __name__ == '__main__':
    # 测试数据生成
    print("正在生成完整招聘数据...")
    df = generate_complete_recruitment_data(months=12, recruiters=5, departments=5)
    print(f"数据生成完成! 共 {len(df)} 行, {len(df.columns)} 列")
    print(f"\n数据字段清单:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. {col}")
    print(f"\n数据预览:")
    print(df.head())
    print(f"\n数据统计:")
    print(df.describe())
