"""
颜色对比度验证脚本
验证所有颜色是否符合WCAG 2.1 AAA级标准 (对比度 >= 7:1)
"""

def calculate_relative_luminance(hex_color):
    """计算相对亮度"""
    # 移除 # 号
    hex_color = hex_color.lstrip('#')

    # 转换为RGB
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255

    # 应用gamma校正
    def gamma_correct(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    r = gamma_correct(r)
    g = gamma_correct(g)
    b = gamma_correct(b)

    # 计算相对亮度
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def calculate_contrast_ratio(color1, color2):
    """计算两个颜色之间的对比度"""
    l1 = calculate_relative_luminance(color1)
    l2 = calculate_relative_luminance(color2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    contrast = (lighter + 0.05) / (darker + 0.05)
    return contrast


def get_wcag_grade(contrast_ratio):
    """获取WCAG等级"""
    if contrast_ratio >= 7.0:
        return "AAA [EXCELLENT]"
    elif contrast_ratio >= 4.5:
        return "AA [GOOD]"
    elif contrast_ratio >= 3.0:
        return "A [WARNING]"
    else:
        return "FAIL [NEEDS FIX]"


# 定义颜色方案
colors = {
    "主色系": {
        "主蓝色 (#4A5FE8) vs 白色": ("#4A5FE8", "#FFFFFF"),
        "深蓝色 (#2A3F98) vs 白色": ("#2A3F98", "#FFFFFF"),
    },
    "语义色系": {
        "成功绿 (#0D7C3A) vs 白色": ("#0D7C3A", "#FFFFFF"),
        "警告橙 (#C17A00) vs 白色": ("#C17A00", "#FFFFFF"),
        "错误红 (#C01C28) vs 白色": ("#C01C28", "#FFFFFF"),
        "信息蓝 (#1B6EA8) vs 白色": ("#1B6EA8", "#FFFFFF"),
    },
    "文字色系": {
        "纯黑 (#1A1A1A) vs 白色": ("#1A1A1A", "#FFFFFF"),
        "深灰 (#2C2C2C) vs 白色": ("#2C2C2C", "#FFFFFF"),
        "中灰 (#3F3F3F) vs 白色": ("#3F3F3F", "#FFFFFF"),
        "浅灰 (#6B6B6B) vs 白色": ("#6B6B6B", "#FFFFFF"),
    },
    "旧配色对比 (已废弃)": {
        "旧成功绿 (#28a745) vs 白色": ("#28a745", "#FFFFFF"),
        "旧警告黄 (#ffc107) vs 白色": ("#ffc107", "#FFFFFF"),
        "旧错误红 (#dc3545) vs 白色": ("#dc3545", "#FFFFFF"),
        "旧灰色 (#666666) vs 白色": ("#666666", "#FFFFFF"),
    }
}


# 验证并输出结果
print("=" * 80)
print(" 招聘数据驾驶舱 v3.0 Pro Max - 颜色对比度验证报告")
print(" WCAG 2.1 AAA级标准: 对比度 >= 7:1")
print("=" * 80)
print()

total_colors = 0
aaa_colors = 0
aa_colors = 0
failed_colors = 0

for category, color_pairs in colors.items():
    print(f"\n[{category}]")
    print("-" * 80)

    for name, (color1, color2) in color_pairs.items():
        contrast = calculate_contrast_ratio(color1, color2)
        grade = get_wcag_grade(contrast)

        total_colors += 1
        if contrast >= 7.0:
            aaa_colors += 1
        elif contrast >= 4.5:
            aa_colors += 1
        else:
            failed_colors += 1

        print(f"{name:45} -> Contrast: {contrast:5.2f}:1  Grade: {grade}")

print()
print("=" * 80)
print(" 总结统计")
print("=" * 80)
print(f"总颜色数: {total_colors}")
print(f"AAA级 (>=7:1): {aaa_colors}  ({aaa_colors/total_colors*100:.1f}%)")
print(f"AA级 (>=4.5:1): {aa_colors}  ({aa_colors/total_colors*100:.1f}%)")
print(f"不合格 (<4.5:1): {failed_colors}  ({failed_colors/total_colors*100:.1f}%)")
print()

if aaa_colors == total_colors:
    print("[PERFECT] All colors meet WCAG 2.1 AAA standard!")
elif aaa_colors + aa_colors == total_colors:
    print("[GOOD] All colors meet WCAG 2.1 AA or above standard!")
else:
    print("[WARNING] Some colors need optimization!")

print()
print("=" * 80)
print(" 新旧配色对比度提升")
print("=" * 80)

improvements = [
    ("成功绿", "#28a745", "#0D7C3A"),
    ("警告色", "#ffc107", "#C17A00"),
    ("错误红", "#dc3545", "#C01C28"),
    ("文字灰", "#666666", "#3F3F3F"),
]

for name, old_color, new_color in improvements:
    old_contrast = calculate_contrast_ratio(old_color, "#FFFFFF")
    new_contrast = calculate_contrast_ratio(new_color, "#FFFFFF")
    improvement = ((new_contrast - old_contrast) / old_contrast) * 100

    old_grade = get_wcag_grade(old_contrast)
    new_grade = get_wcag_grade(new_contrast)

    print(f"\n{name}:")
    print(f"  Old: {old_color} -> Contrast {old_contrast:.2f}:1  {old_grade}")
    print(f"  New: {new_color} -> Contrast {new_contrast:.2f}:1  {new_grade}")
    print(f"  Improvement: +{improvement:.1f}%")

print()
print("=" * 80)

