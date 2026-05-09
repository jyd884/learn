"""
生成客家艾粄介绍PPT
运行方式: python3 generate_ppt.py
输出文件: 艾粄_客家饮食文化介绍.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm
import copy


# ── 调色板 ────────────────────────────────────────────────
GREEN_DARK   = RGBColor(0x2E, 0x6B, 0x3E)   # 深绿（主题色）
GREEN_MID    = RGBColor(0x4C, 0xA0, 0x5A)   # 中绿（副标题/强调）
GREEN_LIGHT  = RGBColor(0xD4, 0xED, 0xDA)   # 浅绿（背景块）
GOLD         = RGBColor(0xC8, 0x9B, 0x2A)   # 金色（装饰线）
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_DARK    = RGBColor(0x33, 0x33, 0x33)
GRAY_MID     = RGBColor(0x66, 0x66, 0x66)
BG_CREAM     = RGBColor(0xF9, 0xF6, 0xEF)   # 米白底色

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


def set_bg(slide, color: RGBColor):
    """设置幻灯片纯色背景"""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill_color, line_color=None, line_width=0):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(line_width)
    else:
        shape.line.fill.background()
    return shape


def add_text_box(slide, text, left, top, width, height,
                 font_size=18, bold=False, color=GRAY_DARK,
                 align=PP_ALIGN.LEFT, font_name="微软雅黑"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name
    return txBox


def add_multiline_text(slide, lines, left, top, width, height,
                       font_size=18, bold=False, color=GRAY_DARK,
                       align=PP_ALIGN.LEFT, font_name="微软雅黑",
                       line_spacing=None, first_bold=False):
    """支持多行列表文字，每行为一个段落"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        p.alignment = align
        if line_spacing:
            p.space_before = Pt(line_spacing)
        run = p.add_run()
        run.text = line
        run.font.size = Pt(font_size)
        run.font.bold = bold if not first_bold else (i == 0)
        run.font.color.rgb = color
        run.font.name = font_name
    return txBox


# ══════════════════════════════════════════════════════════
# Slide 1 — 封面
# ══════════════════════════════════════════════════════════
def slide_cover(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_bg(slide, GREEN_DARK)

    # 右侧浅色竖条装饰
    add_rect(slide, Inches(10.5), Inches(0), Inches(2.83), SLIDE_H, GREEN_MID)
    add_rect(slide, Inches(11.5), Inches(0), Inches(0.12), SLIDE_H, GOLD)

    # 金色横线
    add_rect(slide, Inches(0.6), Inches(3.1), Inches(9.5), Pt(3), GOLD)

    # 主标题
    add_text_box(slide, "艾　粄", Inches(0.6), Inches(0.9), Inches(9),
                 Inches(1.6), font_size=72, bold=True, color=WHITE,
                 align=PP_ALIGN.LEFT)

    # 副标题
    add_text_box(slide, "客家饮食文化的绿色名片",
                 Inches(0.6), Inches(2.5), Inches(9), Inches(0.7),
                 font_size=28, bold=False, color=GOLD, align=PP_ALIGN.LEFT)

    # 说明文字
    add_multiline_text(slide,
                       ["课程：文化概论",
                        "班级：2022 级 × 班",
                        "姓名：×××",
                        "日期：2025 年春季学期"],
                       Inches(0.6), Inches(3.4), Inches(6), Inches(2.5),
                       font_size=18, color=GREEN_LIGHT, align=PP_ALIGN.LEFT,
                       line_spacing=6)

    # 右侧大字装饰（繁体"粄"）
    add_text_box(slide, "粄", Inches(10.7), Inches(1.2), Inches(2.3), Inches(5),
                 font_size=200, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF),
                 align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════
# Slide 2 — 目录
# ══════════════════════════════════════════════════════════
def slide_outline(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, BG_CREAM)

    # 顶部绿色标题栏
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.2), GREEN_DARK)
    add_text_box(slide, "目  录  CONTENTS",
                 Inches(0.5), Inches(0.2), Inches(12), Inches(0.85),
                 font_size=34, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

    items = [
        ("01", "什么是艾粄？",        "起源与定义"),
        ("02", "艾粄的历史与文化背景", "客家文化溯源"),
        ("03", "主要原料介绍",         "艾草与糯米"),
        ("04", "制作工艺",             "传统手工流程"),
        ("05", "口味与种类",           "多彩的地方变体"),
        ("06", "饮食文化意义",         "节气・家族・传承"),
        ("07", "总结与感悟",           ""),
    ]

    col_x = [Inches(0.55), Inches(4.7), Inches(9.0)]
    row_h = Inches(0.75)
    start_y = Inches(1.45)

    for idx, (num, title, sub) in enumerate(items):
        y = start_y + idx * row_h
        # 编号圆形背景
        add_rect(slide, col_x[0], y + Pt(4), Inches(0.55), Inches(0.52),
                 GREEN_DARK)
        add_text_box(slide, num, col_x[0], y, Inches(0.55), Inches(0.6),
                     font_size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        # 标题
        add_text_box(slide, title, col_x[0] + Inches(0.65), y,
                     Inches(3.7), Inches(0.55),
                     font_size=19, bold=True, color=GREEN_DARK)
        # 副说明
        add_text_box(slide, sub, col_x[1] + Inches(0.2), y,
                     Inches(4.0), Inches(0.55),
                     font_size=16, bold=False, color=GRAY_MID)

    # 底部金线
    add_rect(slide, Inches(0.5), Inches(7.1), Inches(12.3), Pt(2), GOLD)


# ══════════════════════════════════════════════════════════
# 通用：带节号的内容幻灯片标题栏
# ══════════════════════════════════════════════════════════
def content_header(slide, num_text, title_text):
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.15), GREEN_DARK)
    # 编号徽章
    add_rect(slide, Inches(0.35), Inches(0.18), Inches(0.62), Inches(0.62), GOLD)
    add_text_box(slide, num_text, Inches(0.35), Inches(0.1), Inches(0.62),
                 Inches(0.8), font_size=22, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER)
    add_text_box(slide, title_text, Inches(1.1), Inches(0.18),
                 Inches(11.5), Inches(0.8),
                 font_size=30, bold=True, color=WHITE)
    # 底部金线
    add_rect(slide, Inches(0), Inches(7.15), SLIDE_W, Pt(3), GOLD)


# ══════════════════════════════════════════════════════════
# Slide 3 — 什么是艾粄？
# ══════════════════════════════════════════════════════════
def slide_what(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, BG_CREAM)
    content_header(slide, "01", "什么是艾粄？")

    # 左侧绿色卡片
    add_rect(slide, Inches(0.4), Inches(1.35), Inches(5.8), Inches(5.7), GREEN_LIGHT)
    add_rect(slide, Inches(0.4), Inches(1.35), Pt(8), Inches(5.7), GREEN_DARK)

    add_multiline_text(slide,
        ["❝ 艾粄 ❞",
         "",
         "艾粄（Ngai Baan）是客家人以",
         "艾草汁与糯米粉揉合制成的一种",
         "传统米制糕点。",
         "",
         "外皮呈翠绿色，内馅以花生、芝",
         "麻、豆沙等为主，口感软糯、清",
         "香，带有艾草特有的草本气息。",
         "",
         "又称「清明粄」「艾糍」，是客",
         "家地区清明节最具代表性的食品。"],
        Inches(0.65), Inches(1.5), Inches(5.3), Inches(5.5),
        font_size=18, color=GRAY_DARK, line_spacing=3)

    # 右侧特征卡片
    features = [
        ("🌿  外观", "翠绿色糯米皮，表面光滑柔软"),
        ("🍃  香气", "艾草清香，淡淡草本芬芳"),
        ("🍡  口感", "软糯弹牙，馅料甜而不腻"),
        ("📅  时节", "清明前后为主要制作与食用季节"),
    ]
    fy = Inches(1.45)
    for icon_title, desc in features:
        add_rect(slide, Inches(6.5), fy, Inches(6.4), Inches(1.15), WHITE,
                 line_color=GREEN_MID, line_width=1.2)
        add_text_box(slide, icon_title, Inches(6.65), fy + Pt(6),
                     Inches(6.1), Inches(0.45),
                     font_size=17, bold=True, color=GREEN_DARK)
        add_text_box(slide, desc, Inches(6.65), fy + Inches(0.5),
                     Inches(6.1), Inches(0.5),
                     font_size=15, color=GRAY_MID)
        fy += Inches(1.3)


# ══════════════════════════════════════════════════════════
# Slide 4 — 历史与文化背景
# ══════════════════════════════════════════════════════════
def slide_history(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, BG_CREAM)
    content_header(slide, "02", "艾粄的历史与文化背景")

    timeline = [
        ("先秦时期",    "艾草已被记载于《诗经》，作为药用植物广泛使用，寓意辟邪祛病。"),
        ("汉代以后",    "南迁汉人（客家先民）将艾草食俗带入岭南，与当地糯米文化融合。"),
        ("宋元时期",    "客家人随战乱南迁，艾粄随之在赣、闽、粤客家聚居地定型传播。"),
        ("明清至今",    "艾粄成为清明祭祖必备供品，并发展出丰富地方口味，流传海内外。"),
    ]

    ty = Inches(1.4)
    for period, desc in timeline:
        # 竖线
        add_rect(slide, Inches(1.55), ty + Inches(0.15), Pt(3),
                 Inches(1.0), GOLD)
        # 圆点
        add_rect(slide, Inches(1.38), ty + Inches(0.08),
                 Inches(0.22), Inches(0.22), GREEN_DARK)
        # 时期标签
        add_text_box(slide, period, Inches(0.4), ty, Inches(1.0),
                     Inches(0.55), font_size=14, bold=True, color=GREEN_DARK,
                     align=PP_ALIGN.RIGHT)
        # 描述卡片
        add_rect(slide, Inches(1.9), ty, Inches(10.8), Inches(1.0), WHITE,
                 line_color=GREEN_LIGHT, line_width=1)
        add_text_box(slide, desc, Inches(2.1), ty + Pt(8), Inches(10.4),
                     Inches(0.8), font_size=17, color=GRAY_DARK)
        ty += Inches(1.3)

    # 底部注释
    add_text_box(slide,
                 "💡  客家人因历史上多次迁徙，将中原饮食文化与南方物产结合，形成独特的\"山地饮食\"体系，艾粄正是这一融合的缩影。",
                 Inches(0.5), Inches(6.6), Inches(12.3), Inches(0.6),
                 font_size=14, color=GREEN_MID)


# ══════════════════════════════════════════════════════════
# Slide 5 — 主要原料
# ══════════════════════════════════════════════════════════
def slide_ingredients(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, BG_CREAM)
    content_header(slide, "03", "主要原料介绍")

    ingredients = [
        ("🌿", "艾　草", "Mugwort",
         ["• 学名：Artemisia argyi",
          "• 性味温，有祛湿、驱寒之效",
          "• 鲜叶洗净后打汁，赋予粄皮",
          "  翠绿色与独特清香",
          "• 清明前后嫩叶品质最佳"]),
        ("🍚", "糯　米", "Glutinous Rice",
         ["• 粳糯或籼糯均可使用",
          "• 磨成米粉后与艾草汁揉和",
          "• 提供软糯、弹牙的口感",
          "• 客家地区多自磨手工米粉"]),
        ("🥜", "馅　料", "Fillings",
         ["• 甜馅：花生碎、芝麻、红糖",
          "• 豆沙：红豆沙最为常见",
          "• 咸馅：萝卜丝、腊肉（部分地区）",
          "• 馅料体现各地客家饮食偏好"]),
    ]

    col_w = Inches(4.0)
    for i, (icon, name, eng, details) in enumerate(ingredients):
        x = Inches(0.4) + i * (col_w + Inches(0.25))
        # 卡片背景
        add_rect(slide, x, Inches(1.35), col_w, Inches(5.7), WHITE,
                 line_color=GREEN_MID, line_width=1.5)
        add_rect(slide, x, Inches(1.35), col_w, Inches(1.0), GREEN_MID)
        # 图标和名称
        add_text_box(slide, icon, x, Inches(1.4), col_w, Inches(0.6),
                     font_size=28, bold=False, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(slide, f"{name}  {eng}", x, Inches(2.5), col_w,
                     Inches(0.55), font_size=18, bold=True, color=GREEN_DARK,
                     align=PP_ALIGN.CENTER)
        add_multiline_text(slide, details, x + Inches(0.15), Inches(3.15),
                           col_w - Inches(0.3), Inches(3.7),
                           font_size=16, color=GRAY_DARK, line_spacing=4)


# ══════════════════════════════════════════════════════════
# Slide 6 — 制作工艺（步骤流程）
# ══════════════════════════════════════════════════════════
def slide_process(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, BG_CREAM)
    content_header(slide, "04", "传统制作工艺")

    steps = [
        ("采摘艾草", "清明前后采摘新鲜嫩叶，洗净备用"),
        ("煮烫去苦", "沸水焯烫2分钟，去除苦涩味"),
        ("打汁混合", "将艾草打碎取汁，加入糯米粉揉成团"),
        ("包入馅料", "分剂子，压扁后包入花生/豆沙馅"),
        ("造型封口", "捏合收口，可做圆形或饺子形"),
        ("蒸制成型", "上笼大火蒸15–20分钟至熟透"),
    ]

    arrow_w = Inches(0.35)
    box_w   = Inches(1.85)
    box_h   = Inches(1.6)
    start_x = Inches(0.3)
    y_top   = Inches(1.45)
    y_bot   = Inches(4.3)

    for i, (title, desc) in enumerate(steps):
        row = i // 3
        col = i % 3
        x = start_x + col * (box_w + arrow_w + Inches(0.1))
        y = y_top if row == 0 else y_bot

        # 步骤方块
        add_rect(slide, x, y, box_w, box_h, GREEN_DARK)
        add_text_box(slide, f"STEP {i+1}", x, y + Pt(8),
                     box_w, Inches(0.4), font_size=13, bold=True,
                     color=GOLD, align=PP_ALIGN.CENTER)
        add_text_box(slide, title, x, y + Inches(0.45),
                     box_w, Inches(0.45), font_size=17, bold=True,
                     color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(slide, desc, x + Pt(6), y + Inches(0.95),
                     box_w - Pt(12), Inches(0.65), font_size=13,
                     color=GREEN_LIGHT)

        # 箭头（非每行最后一个）
        if col < 2:
            ax = x + box_w + Inches(0.05)
            add_text_box(slide, "▶", ax, y + Inches(0.55),
                         arrow_w, Inches(0.5), font_size=22,
                         color=GOLD, align=PP_ALIGN.CENTER)

    # 中间换行连接箭头
    add_text_box(slide, "▼ 继续", Inches(10.8), Inches(3.1),
                 Inches(1.5), Inches(0.6), font_size=14,
                 color=GREEN_MID, align=PP_ALIGN.LEFT)

    # 小贴士
    add_rect(slide, Inches(0.3), Inches(6.1), Inches(12.6), Inches(0.95),
             GREEN_LIGHT)
    add_text_box(slide,
                 "🍃 传统做法小贴士：揉面时艾草汁需趁热加入，可使颜色更鲜亮；"
                 "蒸前在笼布上抹油，防止粘连。",
                 Inches(0.5), Inches(6.15), Inches(12.2), Inches(0.85),
                 font_size=15, color=GREEN_DARK)


# ══════════════════════════════════════════════════════════
# Slide 7 — 口味与种类
# ══════════════════════════════════════════════════════════
def slide_varieties(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, BG_CREAM)
    content_header(slide, "05", "口味与地方种类")

    varieties = [
        ("梅州艾粄",   "🌟 最经典",
         "甜馅为主（花生+芝麻+红糖），粄皮薄而均匀，清明祭祖必备。"),
        ("赣南艾糍",   "🎋 偏咸香",
         "部分地区包入萝卜丝炒腊肉，口味咸鲜，体现山区饮食风格。"),
        ("闽西清明粿", "🍃 形似饺",
         "外形捏成饺子状，馅料以豆沙或笋丁为主，色泽翠绿鲜亮。"),
        ("台湾草仔粿", "🌺 现代风",
         "客家移民带入台湾，演化出多种口味，并发展成商业化产品。"),
    ]

    vy = Inches(1.4)
    for i, (name, tag, desc) in enumerate(varieties):
        row, col = divmod(i, 2)
        x = Inches(0.4) + col * Inches(6.45)
        y = vy + row * Inches(2.65)

        add_rect(slide, x, y, Inches(6.2), Inches(2.4), WHITE,
                 line_color=GREEN_DARK, line_width=1.5)
        add_rect(slide, x, y, Inches(6.2), Inches(0.62), GREEN_DARK)
        add_text_box(slide, f"{name}  {tag}",
                     x + Pt(8), y + Pt(6), Inches(6.0), Inches(0.5),
                     font_size=18, bold=True, color=WHITE)
        add_text_box(slide, desc, x + Pt(10), y + Inches(0.75),
                     Inches(5.9), Inches(1.5), font_size=16, color=GRAY_DARK)

    # 共同点说明
    add_rect(slide, Inches(0.4), Inches(6.9), Inches(12.5), Inches(0.42),
             GREEN_DARK)
    add_text_box(slide,
                 "各地艾粄虽形态各异，但核心相同：以艾草入食、糯米为皮、寄托思乡之情。",
                 Inches(0.6), Inches(6.92), Inches(12.2), Inches(0.38),
                 font_size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════
# Slide 8 — 饮食文化意义
# ══════════════════════════════════════════════════════════
def slide_culture(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, BG_CREAM)
    content_header(slide, "06", "饮食文化意义")

    dimensions = [
        ("🌾", "节气与时令",
         ["艾粄以清明节为核心时节",
          "体现客家人\"不时不食\"的饮食智慧",
          "艾草季节性生长决定了食俗的周期性"]),
        ("👨‍👩‍👧‍👦", "家族与祭祖",
         ["清明艾粄作为供品祭扫先祖",
          "全家动手制粄，强化家族凝聚力",
          "\"做粄\"是重要的家庭集体记忆"]),
        ("💊", "药食同源",
         ["艾草性温，有驱寒、祛湿之效",
          "春季进食契合中医\"春养阳\"理念",
          "体现客家饮食\"以食补身\"的传统"]),
        ("🌍", "文化传承",
         ["随客家移民传播至东南亚、台湾",
          "成为海外客家人的乡愁符号",
          "非物质文化遗产保护对象之一"]),
    ]

    cols = 2
    dw = Inches(5.9)
    dh = Inches(2.4)
    for i, (icon, title, points) in enumerate(dimensions):
        row, col = divmod(i, cols)
        x = Inches(0.4) + col * (dw + Inches(0.6))
        y = Inches(1.35) + row * (dh + Inches(0.3))

        add_rect(slide, x, y, dw, dh, WHITE,
                 line_color=GREEN_LIGHT, line_width=1)
        add_rect(slide, x, y, Inches(0.75), dh, GREEN_DARK)
        add_text_box(slide, icon, x, y + Inches(0.75),
                     Inches(0.75), Inches(0.8), font_size=24,
                     align=PP_ALIGN.CENTER, color=WHITE)
        add_text_box(slide, title, x + Inches(0.85), y + Pt(10),
                     dw - Inches(0.95), Inches(0.5),
                     font_size=18, bold=True, color=GREEN_DARK)
        add_multiline_text(slide, points,
                           x + Inches(0.85), y + Inches(0.65),
                           dw - Inches(0.95), dh - Inches(0.7),
                           font_size=15, color=GRAY_DARK, line_spacing=3)


# ══════════════════════════════════════════════════════════
# Slide 9 — 总结与感悟
# ══════════════════════════════════════════════════════════
def slide_summary(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, GREEN_DARK)

    # 右侧竖条
    add_rect(slide, Inches(10.8), Inches(0), Inches(2.53), SLIDE_H, GREEN_MID)
    add_rect(slide, Inches(10.8), Inches(0), Pt(4), SLIDE_H, GOLD)

    # 标题
    add_text_box(slide, "总 结 与 感 悟",
                 Inches(0.6), Inches(0.4), Inches(10), Inches(0.9),
                 font_size=38, bold=True, color=WHITE)
    add_rect(slide, Inches(0.6), Inches(1.3), Inches(9.8), Pt(2), GOLD)

    points = [
        "🌿  艾粄不仅仅是一道食物，更是客家人对自然、祖先与家园的深情表达。",
        "🧬  从艾草到糯米，从煮汁到蒸制，每一个步骤都凝聚着代代相传的手艺智慧。",
        "🌏  随着客家人走遍世界，艾粄也成为维系海内外客家人文化认同的纽带。",
        "📚  研究饮食文化，是理解一个民系精神气质最生动、最鲜活的切入口。",
    ]
    py = Inches(1.55)
    for pt in points:
        add_rect(slide, Inches(0.5), py, Inches(9.9), Inches(0.95),
                 RGBColor(0x3A, 0x7A, 0x4E))
        add_text_box(slide, pt, Inches(0.65), py + Pt(6),
                     Inches(9.5), Inches(0.75),
                     font_size=17, color=WHITE)
        py += Inches(1.1)

    # 结语
    add_text_box(slide,
                 "「一口艾粄，一缕乡愁，一份传承。」",
                 Inches(0.5), Inches(6.1), Inches(10), Inches(0.8),
                 font_size=22, bold=True, color=GOLD, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════
# Slide 10 — 谢谢 / Q&A
# ══════════════════════════════════════════════════════════
def slide_thanks(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, BG_CREAM)

    add_rect(slide, Inches(0), Inches(0), Inches(0.25), SLIDE_H, GREEN_DARK)
    add_rect(slide, Inches(0.25), Inches(0), Inches(0.12), SLIDE_H, GOLD)

    # 大字
    add_text_box(slide, "谢  谢  聆  听",
                 Inches(0.8), Inches(1.5), Inches(11.5), Inches(1.8),
                 font_size=72, bold=True, color=GREEN_DARK,
                 align=PP_ALIGN.CENTER)

    add_text_box(slide, "THANK YOU",
                 Inches(0.8), Inches(3.1), Inches(11.5), Inches(0.8),
                 font_size=28, bold=False, color=GREEN_MID,
                 align=PP_ALIGN.CENTER)

    add_rect(slide, Inches(3.0), Inches(4.0), Inches(7.3), Pt(2), GOLD)

    add_text_box(slide, "Q & A  欢迎提问",
                 Inches(0.8), Inches(4.2), Inches(11.5), Inches(0.7),
                 font_size=26, bold=True, color=GRAY_DARK,
                 align=PP_ALIGN.CENTER)

    add_multiline_text(slide,
                       ["参考资料：",
                        "1. 《客家饮食文化》，温锐君著，广东人民出版社",
                        "2. 《中国传统节日饮食》，王学泰著",
                        "3. 梅州市非物质文化遗产保护中心相关文献"],
                       Inches(2.0), Inches(5.3), Inches(9.5), Inches(1.8),
                       font_size=13, color=GRAY_MID, line_spacing=4)


# ══════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════
def main():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_cover(prs)
    slide_outline(prs)
    slide_what(prs)
    slide_history(prs)
    slide_ingredients(prs)
    slide_process(prs)
    slide_varieties(prs)
    slide_culture(prs)
    slide_summary(prs)
    slide_thanks(prs)

    out = "艾粄_客家饮食文化介绍.pptx"
    prs.save(out)
    print(f"✅  PPT 已生成：{out}  （共 {len(prs.slides)} 页）")


if __name__ == "__main__":
    main()
