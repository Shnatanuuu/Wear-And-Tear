import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus.flowables import Flowable
from datetime import datetime
import io
import pytz
from openai import OpenAI
import os
from dotenv import load_dotenv
import re

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# ─── Register Chinese font once ────────────────────────────────────────────────
try:
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    CHINESE_FONT = 'STSong-Light'
except Exception:
    CHINESE_FONT = 'Helvetica'

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grandstep Wear Test Assessment",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Constants ─────────────────────────────────────────────────────────────────
CHINESE_CITIES = {
    "Guangzhou":"广州","Shenzhen":"深圳","Dongguan":"东莞","Foshan":"佛山",
    "Zhongshan":"中山","Huizhou":"惠州","Zhuhai":"珠海","Jiangmen":"江门",
    "Zhaoqing":"肇庆","Shanghai":"上海","Beijing":"北京","Suzhou":"苏州",
    "Hangzhou":"杭州","Ningbo":"宁波","Wenzhou":"温州","Wuhan":"武汉",
    "Chengdu":"成都","Chongqing":"重庆","Tianjin":"天津","Nanjing":"南京",
    "Xi'an":"西安","Qingdao":"青岛","Dalian":"大连","Shenyang":"沈阳",
    "Changsha":"长沙","Zhengzhou":"郑州","Jinan":"济南","Harbin":"哈尔滨",
    "Changchun":"长春","Taiyuan":"太原","Shijiazhuang":"石家庄","Lanzhou":"兰州",
    "Xiamen":"厦门","Fuzhou":"福州","Nanning":"南宁","Kunming":"昆明",
    "Guiyang":"贵阳","Haikou":"海口","Ürümqi":"乌鲁木齐","Lhasa":"拉萨",
}

time_periods  = ["1 Hour","1 Day","1 Week","2 Weeks","3 Weeks","4 Weeks"]
days_to_track = ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7",
                 "2 Weeks","3 Weeks","4 Weeks","5 Weeks"]
questions_d   = [
    "Does shoe feel unstable when walking?",
    "Any upper broken or damage?",
    "Any sole gapping?",
    "Does lining color come off?",
    "Any appearance changes?",
    "Any piece rubbing feet?",
    "Is bottom severely worn?"
]

# ─── UI text lookup ────────────────────────────────────────────────────────────
UI_TEXTS = {
    "en": {
        "title":              "Grandstep Wear Test Assessment",
        "basic_info":         "Basic Information",
        "fit_size_tester":    "Fit Size & Tester Information",
        "before_trying":      "A. Before Trying On (Touch & Feel)",
        "fit_before_walking": "B. Fit Before Walking (Standing)",
        "after_walking":      "C. After 8-15 Minutes of Walking",
        "extended_wear":      "D. Extended Wear Testing (Over Time)",
        "comfort_appearance": "E. Comfort & Appearance Index",
        "final_assessment":   "Final Assessment",
        "generate_pdf":       "🎯 Generate PDF Report",
        "download_pdf":       "📥 Download PDF Report",
        "po_number":          "PO Number",
        "factory":            "Factory",
        "color":              "Color",
        "style":              "Style",
        "brand":              "Brand",
        "description":        "Description",
        "sample_type":        "Sample Type",
        "testers":            "Testers",
        "fit_sizes":          "Fit Sizes",
        "upper_feel":         "Upper Material Feel",
        "lining_feel":        "Lining Material Feel",
        "sock_feel":          "Sock Cushion Feel",
        "prepared_by":        "Prepared By",
        "approved_by":        "Approved By",
        "overall_result":     "Overall Result",
        "date":               "Date",
        "issues_noticed":     "Issues Noticed",
        "comfort_level":      "Comfort Level",
        "appearance":         "Appearance",
        "select_location":    "Select Test Location",
        "ui_lang":            "User Interface Language",
        "pdf_lang":           "PDF Report Language",
        "local_time":         "Local Time",
        "translation_active": "Translation API: Active",
        "translation_off":    "Translation API: Not Configured",
        "cities":             "Cities",
        "languages":          "Languages",
        "api_setup":          "API Setup",
        "tab_basic":          "📋 Basic Info",
        "tab_testing":        "🧪 Testing Data",
        "tab_final":          "📊 Final Assessment",
        "fill_required":      "Please fill in at least PO Number and Brand!",
        "creating_pdf":       "Creating your professional PDF report...",
        "generate_success":   "PDF Generated Successfully!",
        "pdf_details":        "PDF Details",
        "report_language":    "Report Language",
        "generated":          "Generated",
        "location":           "Location",
        "error_generating":   "Error generating PDF",
        "footer_text":        "Grandstep Wear Test Assessment System",
        "powered_by":         "Powered by Streamlit",
        "copyright":          "© 2025 - Professional Footwear Testing Platform",
        "comfortable":        "Comfortable",
        "somewhat_comfortable":"Somewhat Comfortable",
        "uncomfortable":      "Uncomfortable",
        "yes":                "Yes",
        "no":                 "No",
        "prototype":          "Prototype",
        "full_size":          "Full Size",
        "die_cut":            "Die Cut",
        "mass_production":    "Mass Production",
        "tester_a":           "Tester A",
        "tester_b":           "Tester B",
        "tester_c":           "Tester C",
        "toe_length_q":       "Is the toe length okay?",
        "ball_position_q":    "Is the ball of foot at correct place?",
        "shoe_flex_q":        "Does the shoe flex at proper place?",
        "arch_support_q":     "Feel arch support in correct position?",
        "top_gapping_q":      "Is the shoe gapping at top line?",
        "fit_properly_q":     "Does it appear shoes fit properly?",
        "feel_fit_q":         "Can you feel the shoe fit?",
        "feel_stability_q":   "Can you feel shoe stability?",
        "sole_flexibility_q": "Does sole have good flexibility?",
        "rubbing_q":          "Any piece rubbing your feet?",
        "interior_lining_q":  "Does interior lining feel good?",
        "slipping_q":         "Is shoe slipping on feet?",
        "toe_room_q":         "Enough room in toe area?",
        "red_marks_q":        "Red marks after removing socks?",
        "instructions_title": "Quick Guide",
        "instructions":       "1. Fill all required fields\n2. Select preferred languages\n3. Choose testing location\n4. Generate PDF report\n5. Download and share",
    },
    "zh": {
        "title":              "Grandstep 穿着测试评估",
        "basic_info":         "基本信息",
        "fit_size_tester":    "试穿尺码 & 测试人员信息",
        "before_trying":      "A. 试穿前（触摸感觉）",
        "fit_before_walking": "B. 行走前合脚性（站立）",
        "after_walking":      "C. 行走8-15分钟后",
        "extended_wear":      "D. 延长穿着测试（随时间变化）",
        "comfort_appearance": "E. 舒适度 & 外观指数",
        "final_assessment":   "最终评估",
        "generate_pdf":       "🎯 生成PDF报告",
        "download_pdf":       "📥 下载PDF报告",
        "po_number":          "PO编号",
        "factory":            "工厂",
        "color":              "颜色",
        "style":              "款式",
        "brand":              "品牌",
        "description":        "描述",
        "sample_type":        "样品类型",
        "testers":            "测试人员",
        "fit_sizes":          "试穿尺码",
        "upper_feel":         "鞋面材料感觉",
        "lining_feel":        "内里材料感觉",
        "sock_feel":          "袜垫感觉",
        "prepared_by":        "准备人",
        "approved_by":        "批准人",
        "overall_result":     "总体结果",
        "date":               "日期",
        "issues_noticed":     "发现的问题",
        "comfort_level":      "舒适度",
        "appearance":         "外观",
        "select_location":    "选择测试地点",
        "ui_lang":            "界面语言",
        "pdf_lang":           "PDF报告语言",
        "local_time":         "本地时间",
        "translation_active": "翻译API: 已启用",
        "translation_off":    "翻译API: 未配置",
        "cities":             "城市",
        "languages":          "语言",
        "api_setup":          "API设置",
        "tab_basic":          "📋 基本信息",
        "tab_testing":        "🧪 测试数据",
        "tab_final":          "📊 最终评估",
        "fill_required":      "请至少填写PO编号和品牌！",
        "creating_pdf":       "正在创建专业PDF报告...",
        "generate_success":   "PDF生成成功！",
        "pdf_details":        "PDF详情",
        "report_language":    "报告语言",
        "generated":          "生成时间",
        "location":           "地点",
        "error_generating":   "生成PDF出错",
        "footer_text":        "Grandstep 穿着测试评估系统",
        "powered_by":         "由 Streamlit 提供支持",
        "copyright":          "© 2025 - 专业鞋类测试平台",
        "comfortable":        "舒适",
        "somewhat_comfortable":"较舒适",
        "uncomfortable":      "不舒适",
        "yes":                "是",
        "no":                 "否",
        "prototype":          "样品",
        "full_size":          "全码",
        "die_cut":            "冲裁",
        "mass_production":    "大货",
        "tester_a":           "测试员A",
        "tester_b":           "测试员B",
        "tester_c":           "测试员C",
        "toe_length_q":       "脚趾长度合适吗？",
        "ball_position_q":    "脚掌位置正确吗？",
        "shoe_flex_q":        "鞋子弯曲位置正确吗？",
        "arch_support_q":     "感觉足弓支撑位置正确吗？",
        "top_gapping_q":      "鞋口处有空隙吗？",
        "fit_properly_q":     "鞋子看起来合脚吗？",
        "feel_fit_q":         "能感觉到鞋子合脚吗？",
        "feel_stability_q":   "能感觉到鞋子稳定性吗？",
        "sole_flexibility_q": "鞋底柔韧性好吗？",
        "rubbing_q":          "有任何部件摩擦脚吗？",
        "interior_lining_q":  "内里感觉好吗？",
        "slipping_q":         "鞋子在脚上滑动吗？",
        "toe_room_q":         "脚趾区域空间充足吗？",
        "red_marks_q":        "脱袜后有红色印记吗？",
        "instructions_title": "快速指南",
        "instructions":       "1. 填写所有必填字段\n2. 选择偏好语言\n3. 选择测试地点\n4. 生成PDF报告\n5. 下载并分享",
    }
}

PERIOD_ZH = {
    "1 Hour":"1小时","1 Day":"1天","1 Week":"1周",
    "2 Weeks":"2周","3 Weeks":"3周","4 Weeks":"4周",
}
QUESTION_ZH = {
    "Does shoe feel unstable when walking?":  "行走时鞋子感觉不稳定吗？",
    "Any upper broken or damage?":            "鞋面有任何破损吗？",
    "Any sole gapping?":                       "鞋底有脱胶吗？",
    "Does lining color come off?":            "内里颜色有脱色吗？",
    "Any appearance changes?":                "外观有任何变化吗？",
    "Any piece rubbing feet?":                "有任何部件摩擦脚吗？",
    "Is bottom severely worn?":               "底部严重磨损了吗？",
}
DAY_ZH = {
    "Day 1":"第1天","Day 2":"第2天","Day 3":"第3天","Day 4":"第4天",
    "Day 5":"第5天","Day 6":"第6天","Day 7":"第7天",
    "2 Weeks":"2周","3 Weeks":"3周","4 Weeks":"4周","5 Weeks":"5周",
}

def t(key):
    lang = st.session_state.get('ui_language', 'en')
    return UI_TEXTS[lang].get(key, UI_TEXTS['en'].get(key, key))

def translate_text_api(text, target_language="zh"):
    """Translate free-form user text via GPT-4o-mini with caching."""
    if not text or not text.strip():
        return text
    if not openai_client:
        return text
    cache_key = f"{text}|{target_language}"
    if cache_key in st.session_state.translations_cache:
        return st.session_state.translations_cache[cache_key]
    # Don't translate pure numbers / codes
    clean = text.replace(' ', '').replace('-', '').replace('/', '')
    if clean.isdigit() or re.match(r'^[A-Za-z]*\d+[A-Za-z]*$', clean):
        st.session_state.translations_cache[cache_key] = text
        return text
    # Already Chinese?
    if re.search(r'[\u4e00-\u9fff]', text):
        st.session_state.translations_cache[cache_key] = text
        return text
    try:
        lang_name = "Simplified Chinese" if target_language == "zh" else "English"
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":f"Translate to {lang_name}. Preserve all numbers, codes, measurements. Return ONLY the translation."},
                {"role":"user","content":text}
            ],
            temperature=0.1, max_tokens=500
        )
        result = resp.choices[0].message.content.strip()
        st.session_state.translations_cache[cache_key] = result
        return result
    except Exception:
        st.session_state.translations_cache[cache_key] = text
        return text

# ─── Session state ──────────────────────────────────────────────────────────────
for key, val in [
    ('ui_language', 'en'),
    ('pdf_language', 'en'),
    ('selected_city', 'Shanghai'),
    ('translations_cache', {}),
]:
    if key not in st.session_state:
        st.session_state[key] = val

if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'po_number':'','factory':'','color':'','style':'','brand':'',
        'sample_type':'Prototype','description':'',
        'fit_sizes':['6/8/39'],'testers':['Tester A'],
        'upper_feel':'Comfortable','lining_feel':'Comfortable','sock_feel':'Comfortable',
        'toe_length':'Yes','ball_position':'Yes','shoe_flex':'Yes',
        'arch_support':'Yes','top_gapping':'No','fit_properly':'Yes',
        'feel_fit':'Yes','interior_lining':'Yes','feel_stability':'Yes',
        'slipping':'No','sole_flexibility':'Yes','toe_room':'Yes',
        'rubbing':'No','red_marks':'No',
        'prepared_by':'','prep_date':datetime.now().date(),
        'approved_by':'','overall_result':'',
        'extended_data':{p:{q:"No" for q in questions_d} for p in time_periods},
        'comfort_scores':{d:3 for d in days_to_track},
        'appearance_scores':{d:3 for d in days_to_track},
        'issues':{d:"" for d in days_to_track},
    }

fd = st.session_state.form_data

# ─── Colour helpers ─────────────────────────────────────────────────────────────
def rating_color(r):
    rl = r.lower()
    if "uncomfortable" in rl: return "#e74c3c"
    if "somewhat" in rl:      return "#f39c12"
    return "#2ecc71"

def yn_color(r):
    return "#2ecc71" if r.lower() == "yes" else "#e74c3c"

def score_color(s):
    if s >= 4: return "#2ecc71"
    if s >= 3: return "#f39c12"
    return "#e74c3c"

# ══════════════════════════════════════════════════════════════════════════════
#  PDF GENERATION  (modern canvas-based design)
# ══════════════════════════════════════════════════════════════════════════════

# Design tokens
C_PRIMARY   = colors.HexColor('#1a1a2e')   # deep navy
C_ACCENT    = colors.HexColor('#e94560')   # vivid red-pink
C_ACCENT2   = colors.HexColor('#0f3460')   # mid blue
C_LIGHT     = colors.HexColor('#f0f4ff')
C_WHITE     = colors.white
C_GREY_TEXT = colors.HexColor('#555555')
C_GREY_LINE = colors.HexColor('#dddddd')
C_GREEN     = colors.HexColor('#27ae60')
C_RED       = colors.HexColor('#e74c3c')
C_ORANGE    = colors.HexColor('#f39c12')
PAGE_W, PAGE_H = A4

HEADER_H    = 60
FOOTER_H    = 36
MARGIN_L    = 40
MARGIN_R    = 40
CONTENT_W   = PAGE_W - MARGIN_L - MARGIN_R


def _font(pdf_lang, bold=False):
    if pdf_lang == "zh":
        return CHINESE_FONT
    return 'Helvetica-Bold' if bold else 'Helvetica'


def draw_page_frame(c, page_num, total_pages, pdf_lang, city, city_zh, gen_time):
    """Draw header + footer on every page."""
    w, h = PAGE_W, PAGE_H

    # ── header bar ──────────────────────────────────────────────
    c.setFillColor(C_PRIMARY)
    c.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)
    # accent stripe
    c.setFillColor(C_ACCENT)
    c.rect(0, h - HEADER_H, 6, HEADER_H, fill=1, stroke=0)

    fn = _font(pdf_lang, bold=True)
    if pdf_lang == "zh":
        header_l = "GRAND STEP (H.K.) LTD"
        header_r = "穿着测试评估报告"
    else:
        header_l = "GRAND STEP (H.K.) LTD"
        header_r = "WEAR TEST ASSESSMENT REPORT"

    c.setFillColor(C_WHITE)
    c.setFont(fn, 13)
    c.drawString(MARGIN_L, h - HEADER_H + 22, header_l)
    c.setFont(_font(pdf_lang), 9)
    c.drawRightString(w - MARGIN_R, h - HEADER_H + 22, header_r)

    # ── footer bar ───────────────────────────────────────────────
    c.setFillColor(C_PRIMARY)
    c.rect(0, 0, w, FOOTER_H, fill=1, stroke=0)
    c.setFillColor(C_ACCENT)
    c.rect(0, FOOTER_H - 3, w, 3, fill=1, stroke=0)

    c.setFillColor(C_WHITE)
    c.setFont(_font(pdf_lang), 7.5)

    if pdf_lang == "zh":
        loc_str  = f"地点: {city} ({city_zh})"
        pg_str   = f"第 {page_num} 页 / 共 {total_pages} 页"
        time_str = f"生成时间: {gen_time}"
    else:
        loc_str  = f"Location: {city}"
        pg_str   = f"Page {page_num} of {total_pages}"
        time_str = f"Generated: {gen_time}"

    c.drawString(MARGIN_L, 13, loc_str)
    c.drawCentredString(w / 2, 13, time_str)
    c.drawRightString(w - MARGIN_R, 13, pg_str)


def draw_section_header(c, y, label, pdf_lang):
    """Draw a coloured section title bar. Returns new y."""
    bar_h = 22
    c.setFillColor(C_ACCENT2)
    c.roundRect(MARGIN_L, y - bar_h, CONTENT_W, bar_h, 4, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont(_font(pdf_lang, bold=True), 10)
    c.drawString(MARGIN_L + 10, y - bar_h + 7, label)
    return y - bar_h - 8


def draw_kv_row(c, x, y, w, label, value, pdf_lang, shade=False):
    """Draw a label-value pair row. Returns new y."""
    ROW_H = 18
    if shade:
        c.setFillColor(C_LIGHT)
        c.rect(x, y - ROW_H, w, ROW_H, fill=1, stroke=0)
    c.setStrokeColor(C_GREY_LINE)
    c.setLineWidth(0.4)
    c.line(x, y - ROW_H, x + w, y - ROW_H)
    lw = w * 0.35
    c.setFillColor(C_ACCENT2)
    c.setFont(_font(pdf_lang, bold=True), 8)
    c.drawString(x + 6, y - ROW_H + 6, label)
    c.setFillColor(C_PRIMARY)
    c.setFont(_font(pdf_lang), 8)
    c.drawString(x + lw + 6, y - ROW_H + 6, str(value)[:80])
    return y - ROW_H


def draw_two_col_kv(c, y, pairs, pdf_lang, shade_alt=True):
    """Draw a two-column grid of label:value rows."""
    col_w = (CONTENT_W - 10) / 2
    for i, (l1, v1, l2, v2) in enumerate(pairs):
        shade = (i % 2 == 0) and shade_alt
        draw_kv_row(c, MARGIN_L,              y, col_w, l1, v1, pdf_lang, shade)
        draw_kv_row(c, MARGIN_L + col_w + 10, y, col_w, l2, v2, pdf_lang, shade)
        y -= 18
    return y


def draw_description_block(c, y, label, text, pdf_lang):
    """
    Draw a full-width multi-line description block.
    Wraps long text across multiple lines so nothing is clipped.
    Returns new y position.
    """
    if not text or not text.strip():
        return y

    fn_b = _font(pdf_lang, bold=True)
    fn_r = _font(pdf_lang)
    FONT_SIZE  = 8
    LINE_H     = 13        # line height in pts
    PADDING    = 7         # inner padding
    LABEL_H    = 18        # height of the label bar
    MAX_CHARS_PER_LINE = int(CONTENT_W / (FONT_SIZE * 0.52))  # approx chars per line

    # Word-wrap the text into lines
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if len(test) <= MAX_CHARS_PER_LINE:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    total_text_h = len(lines) * LINE_H + PADDING * 2
    block_h = LABEL_H + total_text_h

    # Label bar
    c.setFillColor(C_LIGHT)
    c.rect(MARGIN_L, y - block_h, CONTENT_W, block_h, fill=1, stroke=0)
    c.setFillColor(C_ACCENT2)
    c.rect(MARGIN_L, y - LABEL_H, CONTENT_W, LABEL_H, fill=1, stroke=0)
    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.4)
    c.rect(MARGIN_L, y - block_h, CONTENT_W, block_h, fill=0, stroke=1)

    c.setFillColor(C_WHITE)
    c.setFont(fn_b, 8)
    c.drawString(MARGIN_L + 8, y - LABEL_H + 6, label)

    # Text lines
    ty = y - LABEL_H - PADDING - LINE_H + 4
    c.setFillColor(C_PRIMARY)
    c.setFont(fn_r, FONT_SIZE)
    for line in lines:
        c.drawString(MARGIN_L + 10, ty, line)
        ty -= LINE_H

    return y - block_h - 6


def draw_qa_table(c, y, rows, pdf_lang):
    """
    rows: list of (question_str, answer_str)
    Draws a clean alternating-row Q&A table.
    Returns new y.
    """
    ROW_H = 17
    q_col  = CONTENT_W * 0.72
    a_col  = CONTENT_W * 0.28
    hdr_h  = 20

    # Header
    c.setFillColor(C_ACCENT)
    c.rect(MARGIN_L, y - hdr_h, CONTENT_W, hdr_h, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    fn = _font(pdf_lang, bold=True)
    c.setFont(fn, 8.5)
    q_lbl = "问题" if pdf_lang == "zh" else "Question"
    a_lbl = "回答" if pdf_lang == "zh" else "Response"
    c.drawString(MARGIN_L + 8, y - hdr_h + 7, q_lbl)
    c.drawRightString(MARGIN_L + CONTENT_W - 8, y - hdr_h + 7, a_lbl)
    y -= hdr_h

    for i, (q, a) in enumerate(rows):
        shade = (i % 2 == 0)
        if shade:
            c.setFillColor(C_LIGHT)
            c.rect(MARGIN_L, y - ROW_H, CONTENT_W, ROW_H, fill=1, stroke=0)
        c.setStrokeColor(C_GREY_LINE)
        c.setLineWidth(0.3)
        c.line(MARGIN_L, y - ROW_H, MARGIN_L + CONTENT_W, y - ROW_H)

        # Question
        c.setFillColor(C_PRIMARY)
        c.setFont(_font(pdf_lang), 8)
        c.drawString(MARGIN_L + 8, y - ROW_H + 5, q[:80])

        # Answer badge
        ans_en = a.strip().lower()
        if ans_en in ("yes", "是"):
            badge_c = C_GREEN
        elif ans_en in ("no", "否"):
            badge_c = C_RED
        elif "comfortable" in ans_en or "舒适" in ans_en:
            badge_c = C_GREEN
        elif "somewhat" in ans_en or "较" in ans_en:
            badge_c = C_ORANGE
        elif "uncomfortable" in ans_en or "不舒" in ans_en:
            badge_c = C_RED
        else:
            badge_c = C_GREY_TEXT

        badge_x = MARGIN_L + CONTENT_W - 60
        c.setFillColor(badge_c)
        c.roundRect(badge_x, y - ROW_H + 3, 52, 12, 3, fill=1, stroke=0)
        c.setFillColor(C_WHITE)
        c.setFont(_font(pdf_lang, bold=True), 7.5)
        c.drawCentredString(badge_x + 26, y - ROW_H + 7, a[:14])
        y -= ROW_H

    return y - 6


def draw_score_bar(c, x, y, score, max_score=5, bar_w=80, bar_h=8):
    """Draw a mini progress-bar for numeric scores."""
    c.setFillColor(C_GREY_LINE)
    c.roundRect(x, y, bar_w, bar_h, 3, fill=1, stroke=0)
    fill_w = bar_w * (score / max_score)
    col = C_GREEN if score >= 4 else (C_ORANGE if score >= 3 else C_RED)
    c.setFillColor(col)
    c.roundRect(x, y, fill_w, bar_h, 3, fill=1, stroke=0)


def generate_pdf():
    pdf_lang   = st.session_state.pdf_language
    city       = st.session_state.selected_city
    city_zh    = CHINESE_CITIES.get(city, city)
    china_tz   = pytz.timezone('Asia/Shanghai')
    now        = datetime.now(china_tz)
    gen_time   = now.strftime('%Y-%m-%d %H:%M')
    gen_date   = now.strftime('%Y-%m-%d')

    # ── Helper to translate user-entered free-text ──────────────────────────
    def tx(text):
        """Translate user-entered free text for the PDF."""
        if pdf_lang == "en" or not openai_client:
            return text
        return translate_text_api(text, "zh")

    # ── Localisation helpers ─────────────────────────────────────────────────
    def loc(en_key, zh_val):
        return zh_val if pdf_lang == "zh" else en_key

    def yn(val):
        if pdf_lang == "zh":
            return "是" if val == "Yes" else "否"
        return val

    def feel(val):
        map_ = {"Comfortable":"舒适","Somewhat Comfortable":"较舒适","Uncomfortable":"不舒适"}
        return map_.get(val, val) if pdf_lang == "zh" else val

    # ── Two-pass rendering: first count pages, then draw with correct total ──
    #    We build a lightweight "script" of (page_number) -> content calls,
    #    then replay with the real total_pages known in advance.

    def _build_pdf(buf_out, total_pages_known):
        """Inner function that actually draws everything onto buf_out."""
        c = rl_canvas.Canvas(buf_out, pagesize=A4)
        fn_b = _font(pdf_lang, bold=True)
        fn_r = _font(pdf_lang)

        # ── helper: new page ───────────────────────────────────────────────
        page_counter = [1]   # mutable reference
        def new_page():
            c.showPage()
            page_counter[0] += 1
            draw_page_frame(c, page_counter[0], total_pages_known,
                            pdf_lang, city, city_zh, gen_time)
            return PAGE_H - HEADER_H - 20

        def maybe_new_page(y, min_space=120):
            """Start a new page if remaining space is too tight."""
            if y < FOOTER_H + min_space:
                return new_page()
            return y

        # ════════════════════════════════════════════════════════════════════
        # PAGE 1 – Cover + Basic Information
        # ════════════════════════════════════════════════════════════════════
        draw_page_frame(c, 1, total_pages_known, pdf_lang, city, city_zh, gen_time)
        y = PAGE_H - HEADER_H - 20

        # Cover banner
        c.setFillColor(C_PRIMARY)
        c.rect(MARGIN_L, y - 120, CONTENT_W, 120, fill=1, stroke=0)
        c.setFillColor(C_ACCENT)
        c.rect(MARGIN_L, y - 120, 8, 120, fill=1, stroke=0)
        c.setFillColor(C_ACCENT)
        c.rect(MARGIN_L, y - 6, CONTENT_W, 6, fill=1, stroke=0)

        c.setFillColor(C_WHITE)
        c.setFont(fn_b, 20)
        c.drawString(MARGIN_L + 24, y - 40, "GRAND STEP (H.K.) LTD")
        c.setFont(fn_r, 11)
        c.setFillColor(colors.HexColor('#aab8ff'))
        c.drawString(MARGIN_L + 24, y - 60,
                     "穿着测试评估报告" if pdf_lang == "zh" else "WEAR TEST ASSESSMENT REPORT")

        pill_items = [
            (loc("Date","日期"),     gen_date),
            (loc("Location","地点"), f"{city} {city_zh}" if pdf_lang == "zh" else city),
            (loc("Language","语言"), "中文" if pdf_lang == "zh" else "English"),
        ]
        px = MARGIN_L + 24
        for lbl, val in pill_items:
            c.setFillColor(colors.HexColor('#0d2244'))
            pill_w = len(f"{lbl}: {val}") * 5.5 + 16
            c.roundRect(px, y - 108, pill_w, 16, 4, fill=1, stroke=0)
            c.setFillColor(colors.HexColor('#aab8ff'))
            c.setFont(fn_b, 7)
            c.drawString(px + 8, y - 100, f"{lbl}:")
            c.setFillColor(C_WHITE)
            c.setFont(fn_r, 7)
            c.drawString(px + 8 + len(lbl) * 4.3 + 8, y - 100, val)
            px += pill_w + 8
        y -= 136

        # Basic Information
        y = draw_section_header(c, y, loc("1. BASIC INFORMATION","1. 基本信息"), pdf_lang)

        prep_date     = fd.get('prep_date', now.date())
        prep_date_str = str(prep_date)
        desc_text     = tx(fd.get('description','')) or ''

        pairs = [
            (loc("PO Number","PO编号"),    tx(fd.get('po_number','')) or '—',
             loc("Brand","品牌"),           tx(fd.get('brand',''))     or '—'),
            (loc("Factory","工厂"),        tx(fd.get('factory',''))   or '—',
             loc("Style","款式"),           tx(fd.get('style',''))     or '—'),
            (loc("Color","颜色"),          tx(fd.get('color',''))     or '—',
             loc("Date","日期"),            prep_date_str),
            (loc("Sample Type","样品类型"),tx(fd.get('sample_type','Prototype')),
             loc("Testers","测试人员"),     ", ".join(fd.get('testers',['—']))),
            (loc("Fit Sizes","试穿尺码"),  ", ".join(fd.get('fit_sizes',['—'])),
             "",""),
        ]
        y = draw_two_col_kv(c, y, pairs, pdf_lang)
        y -= 4

        # Full-width description block (handles 4-5 sentences)
        if desc_text:
            desc_label = loc("Description","描述")
            y = draw_description_block(c, y, desc_label, desc_text, pdf_lang)
        y -= 6

        # Section A
        y = maybe_new_page(y, 140)
        y = draw_section_header(c, y, loc("2. BEFORE TRYING ON (TOUCH & FEEL)","2. 试穿前（触摸感觉）"), pdf_lang)
        rows_a = [
            (loc("Upper Material Feel","鞋面材料感觉"),  feel(fd.get('upper_feel','Comfortable'))),
            (loc("Lining Material Feel","内里材料感觉"), feel(fd.get('lining_feel','Comfortable'))),
            (loc("Sock Cushion Feel","袜垫感觉"),        feel(fd.get('sock_feel','Comfortable'))),
        ]
        y = draw_qa_table(c, y, rows_a, pdf_lang)

        # Section B
        y = maybe_new_page(y, 160)
        y = draw_section_header(c, y, loc("3. FIT BEFORE WALKING (STANDING)","3. 行走前合脚性（站立）"), pdf_lang)
        rows_b = [
            (loc("Is toe length okay?","脚趾长度合适吗？"),             yn(fd.get('toe_length','Yes'))),
            (loc("Ball of foot at correct place?","脚掌位置正确吗？"),  yn(fd.get('ball_position','Yes'))),
            (loc("Shoe flex at proper place?","鞋子弯曲位置正确吗？"),  yn(fd.get('shoe_flex','Yes'))),
            (loc("Feel arch support?","感觉足弓支撑吗？"),              yn(fd.get('arch_support','Yes'))),
            (loc("Shoe gapping at top line?","鞋口处有空隙吗？"),       yn(fd.get('top_gapping','No'))),
            (loc("Shoes fit properly?","鞋子合脚吗？"),                 yn(fd.get('fit_properly','Yes'))),
        ]
        y = draw_qa_table(c, y, rows_b, pdf_lang)

        # ════════════════════════════════════════════════════════════════════
        # PAGE 2 – Section C: After Walking
        # ════════════════════════════════════════════════════════════════════
        y = new_page()
        y = draw_section_header(c, y, loc("4. AFTER 8-15 MINUTES WALKING","4. 行走8-15分钟后"), pdf_lang)
        rows_c = [
            (loc("Can feel shoe fit?","能感觉到鞋子合脚吗？"),            yn(fd.get('feel_fit','Yes'))),
            (loc("Interior lining feels good?","内里感觉好吗？"),         yn(fd.get('interior_lining','Yes'))),
            (loc("Can feel stability?","能感觉到稳定性吗？"),             yn(fd.get('feel_stability','Yes'))),
            (loc("Shoe slipping?","鞋子滑脚吗？"),                        yn(fd.get('slipping','No'))),
            (loc("Sole flexibility good?","鞋底柔韧性好吗？"),            yn(fd.get('sole_flexibility','Yes'))),
            (loc("Enough toe room?","脚趾区域有足够空间吗？"),            yn(fd.get('toe_room','Yes'))),
            (loc("Any rubbing?","有任何摩擦吗？"),                        yn(fd.get('rubbing','No'))),
            (loc("Red marks after removing socks?","脱袜后有红色印记吗？"),yn(fd.get('red_marks','No'))),
        ]
        y = draw_qa_table(c, y, rows_c, pdf_lang)

        # ════════════════════════════════════════════════════════════════════
        # PAGE 3+ – Section D: Extended Wear Testing
        # ════════════════════════════════════════════════════════════════════
        y = new_page()
        y = draw_section_header(c, y, loc("5. EXTENDED WEAR TESTING","5. 延长穿着测试"), pdf_lang)

        for period in time_periods:
            period_lbl = PERIOD_ZH.get(period, period) if pdf_lang == "zh" else period
            y = maybe_new_page(y, 160)

            # Period sub-header
            c.setFillColor(C_PRIMARY)
            c.roundRect(MARGIN_L, y - 16, CONTENT_W, 16, 3, fill=1, stroke=0)
            c.setFillColor(colors.HexColor('#aab8ff'))
            c.setFont(fn_b, 8)
            c.drawString(MARGIN_L + 8, y - 11, period_lbl)
            y -= 20

            period_data = fd.get('extended_data', {}).get(period, {})
            rows = [(QUESTION_ZH.get(q,q) if pdf_lang=="zh" else q, yn(period_data.get(q,"No")))
                    for q in questions_d]
            y = draw_qa_table(c, y, rows, pdf_lang)

        # ════════════════════════════════════════════════════════════════════
        # Next page – Section E: Comfort Index + Final Assessment
        # ════════════════════════════════════════════════════════════════════
        y = new_page()
        y = draw_section_header(c, y, loc("6. COMFORT & APPEARANCE INDEX","6. 舒适度与外观指数"), pdf_lang)

        ROW_H = 20
        cols  = [70, 80, 80, CONTENT_W - 230]
        hdr_labels = [
            loc("Day","天"),
            loc("Comfort (1-5)","舒适 (1-5)"),
            loc("Appear (1-5)","外观 (1-5)"),
            loc("Issues Noticed","发现的问题"),
        ]
        c.setFillColor(C_ACCENT)
        c.rect(MARGIN_L, y - 20, CONTENT_W, 20, fill=1, stroke=0)
        c.setFillColor(C_WHITE); c.setFont(fn_b, 8)
        cx = MARGIN_L + 6
        for i, lbl in enumerate(hdr_labels):
            c.drawString(cx, y - 14, lbl)
            cx += cols[i]
        y -= 20

        for idx, day in enumerate(days_to_track):
            y = maybe_new_page(y, 30)
            day_lbl = DAY_ZH.get(day, day) if pdf_lang == "zh" else day
            comfort = fd.get('comfort_scores', {}).get(day, 3)
            appear  = fd.get('appearance_scores', {}).get(day, 3)
            issue   = tx(fd.get('issues', {}).get(day, ''))

            shade = (idx % 2 == 0)
            if shade:
                c.setFillColor(C_LIGHT)
                c.rect(MARGIN_L, y - ROW_H, CONTENT_W, ROW_H, fill=1, stroke=0)
            c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.3)
            c.line(MARGIN_L, y - ROW_H, MARGIN_L + CONTENT_W, y - ROW_H)

            cx = MARGIN_L + 6
            c.setFillColor(C_PRIMARY); c.setFont(fn_r, 8)
            c.drawString(cx, y - ROW_H + 6, day_lbl)
            cx += cols[0]

            draw_score_bar(c, cx, y - ROW_H + 6, comfort, bar_w=55, bar_h=8)
            c.setFillColor(score_color(comfort)); c.setFont(fn_b, 7)
            c.drawString(cx + 58, y - ROW_H + 6, str(comfort))
            cx += cols[1]

            draw_score_bar(c, cx, y - ROW_H + 6, appear, bar_w=55, bar_h=8)
            c.setFillColor(score_color(appear)); c.setFont(fn_b, 7)
            c.drawString(cx + 58, y - ROW_H + 6, str(appear))
            cx += cols[2]

            c.setFillColor(C_GREY_TEXT); c.setFont(fn_r, 7)
            c.drawString(cx, y - ROW_H + 6, (issue or '—')[:55])
            y -= ROW_H

        y -= 14

        # Final Assessment
        y = maybe_new_page(y, 180)
        y = draw_section_header(c, y, loc("7. FINAL ASSESSMENT","7. 最终评估"), pdf_lang)

        final_pairs = [
            (loc("Prepared By","准备人"),   tx(fd.get('prepared_by','')) or '—',
             loc("Date","日期"),             prep_date_str),
            (loc("Approved By","批准人"),   tx(fd.get('approved_by','')) or '—',
             loc("Overall Result","总体结果"), tx(fd.get('overall_result','')) or '—'),
        ]
        y = draw_two_col_kv(c, y, final_pairs, pdf_lang)

        y -= 30
        c.setStrokeColor(C_PRIMARY); c.setLineWidth(1)
        c.line(MARGIN_L, y, MARGIN_L + 180, y)
        c.line(MARGIN_L + 210, y, MARGIN_L + 390, y)
        c.setFillColor(C_GREY_TEXT); c.setFont(fn_r, 8)
        c.drawString(MARGIN_L,       y - 12, loc("Prepared By Signature","准备人签名"))
        c.drawString(MARGIN_L + 210, y - 12, loc("Approved By Signature","批准人批准"))

        conf = ("本报告为GRAND STEP (H.K.) LTD机密文件，未经授权禁止分发。"
                if pdf_lang == "zh"
                else "This report is confidential property of GRAND STEP (H.K.) LTD. Unauthorised distribution is prohibited.")
        c.setFillColor(C_GREY_TEXT); c.setFont(fn_r, 7.5)
        c.drawCentredString(PAGE_W / 2, FOOTER_H + 12, conf)

        c.save()
        return page_counter[0]   # actual total pages used

    # ── Pass 1: dry-run to count pages ───────────────────────────────────────
    count_buf = io.BytesIO()
    actual_total = _build_pdf(count_buf, 99)   # placeholder "99" during counting

    # ── Pass 2: real render with correct page total ───────────────────────────
    buf = io.BytesIO()
    _build_pdf(buf, actual_total)
    buf.seek(0)
    return buf




# ══════════════════════════════════════════════════════════════════════════════
#  STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
  .main-header{font-size:2.6rem;font-weight:800;text-align:center;
  color: #4A5568; /* Light gray color - change this to any color you want */
  margin-bottom:1.5rem;padding:0.5rem;}
  .section-header{font-size:1.4rem;font-weight:700;color:#1a1a2e;
    margin:2rem 0 1rem;padding:0.7rem 1.2rem;
    background:linear-gradient(135deg,#f0f4ff 0%,#dde4ff 100%);
    border-radius:10px;border-left:5px solid #e94560;}
  .stButton>button{background:linear-gradient(135deg,#1a1a2e 0%,#e94560 100%);
    color:white;font-size:1.1rem;font-weight:600;padding:0.9rem 2rem;
    border-radius:10px;border:none;width:100%;transition:all .3s;}
  .stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 16px rgba(233,69,96,.35);}
  .footer{text-align:center;padding:1.5rem;
    background:linear-gradient(135deg,#f0f4ff 0%,#dde4ff 100%);
    border-radius:12px;margin-top:2rem;border-top:3px solid #e94560;}
  .location-badge{display:inline-flex;align-items:center;gap:6px;
    background:linear-gradient(135deg,#1a1a2e 0%,#0f3460 100%);
    color:white;padding:.4rem .9rem;border-radius:20px;font-weight:600;font-size:.85rem;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    st.markdown(f"#### 🌐 {t('ui_lang')}")
    ui_lang_choice = st.selectbox(
        t('ui_lang'),
        ["English", "中文 (Mandarin)"],
        index=0 if st.session_state.ui_language == "en" else 1,
        key="ui_lang_select", label_visibility="collapsed"
    )
    new_ui = "en" if ui_lang_choice == "English" else "zh"
    if new_ui != st.session_state.ui_language:
        st.session_state.ui_language = new_ui
        st.session_state.translations_cache = {}
        st.rerun()

    st.markdown(f"#### 📄 {t('pdf_lang')}")
    pdf_lang_choice = st.selectbox(
        t('pdf_lang'),
        ["English", "中文 (Mandarin)"],
        index=0 if st.session_state.pdf_language == "en" else 1,
        key="pdf_lang_select", label_visibility="collapsed"
    )
    st.session_state.pdf_language = "en" if pdf_lang_choice == "English" else "zh"

    st.markdown(f"#### 📍 {t('select_location')}")
    city_keys = list(CHINESE_CITIES.keys())
    city_idx  = city_keys.index(st.session_state.selected_city) if st.session_state.selected_city in city_keys else 0
    sel_city  = st.selectbox(
        t('select_location'), city_keys, index=city_idx,
        key="city_select", label_visibility="collapsed"
    )
    st.session_state.selected_city = sel_city
    st.markdown(f'<div class="location-badge">📍 {sel_city} ({CHINESE_CITIES.get(sel_city,"")})</div>', unsafe_allow_html=True)

    st.markdown(f"#### 🕐 {t('local_time')}")
    china_tz = pytz.timezone('Asia/Shanghai')
    now_cn   = datetime.now(china_tz)
    st.metric(t('local_time'), now_cn.strftime('%H:%M:%S'), now_cn.strftime('%Y-%m-%d'))

    if openai_client:
        st.success(f"✅ {t('translation_active')}")
    else:
        st.warning(f"⚠️ {t('translation_off')}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1: st.metric(t('cities'), len(CHINESE_CITIES))
    with col2: st.metric(t('languages'), 2)

    st.markdown("---")
    st.markdown(f"### ℹ️ {t('instructions_title')}")
    for line in t('instructions').split('\n'):
        st.write(line)

    with st.expander(f"🔑 {t('api_setup')}"):
        st.code("# Create .env file\nOPENAI_API_KEY=your-api-key-here")
        st.info("Restart after adding key to enable translation.")

# ── Main header ──────────────────────────────────────────────────────────────
st.markdown(f'<div class="main-header">👟 {t("title")}</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([t('tab_basic'), t('tab_testing'), t('tab_final')])

# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<div class="section-header">📋 {t("basic_info")}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        fd['po_number']  = st.text_input(t('po_number'),  value=fd.get('po_number',''),  key="po")
        fd['factory']    = st.text_input(t('factory'),    value=fd.get('factory',''),    key="fac")
    with c2:
        fd['color']      = st.text_input(t('color'),      value=fd.get('color',''),      key="col")
        fd['style']      = st.text_input(t('style'),      value=fd.get('style',''),      key="sty")
    with c3:
        fd['brand']      = st.text_input(t('brand'),      value=fd.get('brand',''),      key="brd")
        sample_opts = ["Prototype","Full Size","Die Cut","Mass Production"]
        sample_disp = [t('prototype'),t('full_size'),t('die_cut'),t('mass_production')]
        cur_samp_idx = sample_opts.index(fd.get('sample_type','Prototype')) if fd.get('sample_type','Prototype') in sample_opts else 0
        sel_samp = st.selectbox(t('sample_type'), sample_disp, index=cur_samp_idx, key="samp")
        fd['sample_type'] = sample_opts[sample_disp.index(sel_samp)]

    fd['description'] = st.text_area(t('description'), value=fd.get('description',''), height=110, key="desc")

    st.markdown(f'<div class="section-header">📏 {t("fit_size_tester")}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        size_opts = ["4/6/37","6/8/39","8/10/41"]
        fd['fit_sizes'] = st.multiselect(t('fit_sizes'), size_opts, default=fd.get('fit_sizes',['6/8/39']), key="fs")
    with c2:
        tester_opts = ["Tester A","Tester B","Tester C"]
        fd['testers'] = st.multiselect(t('testers'), tester_opts, default=fd.get('testers',['Tester A']), key="ts")

# ════════════════════════════════════════════════════════════════════════════
with tab2:
    # Section A
    st.markdown(f'<div class="section-header">🤚 {t("before_trying")}</div>', unsafe_allow_html=True)
    feel_opts     = ["Uncomfortable","Somewhat Comfortable","Comfortable"]
    feel_disp     = [t('uncomfortable'),t('somewhat_comfortable'),t('comfortable')]
    c1, c2, c3   = st.columns(3)

    def feel_radio(label_key, data_key, col):
        cur = feel_opts.index(fd.get(data_key,'Comfortable')) if fd.get(data_key,'Comfortable') in feel_opts else 2
        with col:
            sel = st.radio(t(label_key), feel_disp, index=cur, horizontal=False, key=f"r_{data_key}")
            fd[data_key] = feel_opts[feel_disp.index(sel)]

    feel_radio('upper_feel',  'upper_feel',  c1)
    feel_radio('lining_feel', 'lining_feel', c2)
    feel_radio('sock_feel',   'sock_feel',   c3)

    # Sections B & C
    def yn_radio(label_key, data_key, col):
        yn_opts = ["No","Yes"]
        yn_disp = [t('no'),t('yes')]
        cur = yn_opts.index(fd.get(data_key,'Yes')) if fd.get(data_key,'Yes') in yn_opts else 1
        with col:
            sel = st.radio(t(label_key), yn_disp, index=cur, horizontal=True, key=f"r_{data_key}")
            fd[data_key] = yn_opts[yn_disp.index(sel)]

    st.markdown(f'<div class="section-header">🚶 {t("fit_before_walking")}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    for lk, dk, col in [
        ('toe_length_q','toe_length',c1), ('ball_position_q','ball_position',c2),
        ('shoe_flex_q','shoe_flex',c1),   ('arch_support_q','arch_support',c2),
        ('top_gapping_q','top_gapping',c1),('fit_properly_q','fit_properly',c2),
    ]:
        yn_radio(lk, dk, col)

    st.markdown(f'<div class="section-header">👣 {t("after_walking")}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    for lk, dk, col in [
        ('feel_fit_q','feel_fit',c1),             ('interior_lining_q','interior_lining',c2),
        ('feel_stability_q','feel_stability',c1),  ('slipping_q','slipping',c2),
        ('sole_flexibility_q','sole_flexibility',c1),('toe_room_q','toe_room',c2),
        ('rubbing_q','rubbing',c1),                ('red_marks_q','red_marks',c2),
    ]:
        yn_radio(lk, dk, col)

# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f'<div class="section-header">📅 {t("extended_wear")}</div>', unsafe_allow_html=True)
    for period in time_periods:
        with st.expander(f"🕐 {period}"):
            for q in questions_d:
                yn_opts = ["No","Yes"]
                yn_disp = [t('no'),t('yes')]
                cur_val = fd['extended_data'].get(period,{}).get(q,'No')
                cur_idx = yn_opts.index(cur_val) if cur_val in yn_opts else 0
                sel = st.radio(q, yn_disp, index=cur_idx, horizontal=True, key=f"ext_{period}_{q}")
                fd['extended_data'].setdefault(period, {})[q] = yn_opts[yn_disp.index(sel)]

    st.markdown(f'<div class="section-header">⭐ {t("comfort_appearance")}</div>', unsafe_allow_html=True)
    for day in days_to_track:
        with st.expander(f"📊 {day}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                fd['comfort_scores'][day] = st.slider(
                    f"⭐ {t('comfort_level')}", 1, 5,
                    fd['comfort_scores'].get(day,3), key=f"cs_{day}")
            with c2:
                fd['appearance_scores'][day] = st.slider(
                    f"✨ {t('appearance')}", 1, 5,
                    fd['appearance_scores'].get(day,3), key=f"as_{day}")
            with c3:
                fd['issues'][day] = st.text_area(
                    f"ℹ️ {t('issues_noticed')}", value=fd['issues'].get(day,''),
                    height=80, key=f"iss_{day}")

    st.markdown(f'<div class="section-header">📝 {t("final_assessment")}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fd['prepared_by'] = st.text_input(t('prepared_by'), value=fd.get('prepared_by',''), key="prep_by")
        fd['prep_date']   = st.date_input(f"📅 {t('date')}", value=fd.get('prep_date',datetime.now().date()), key="pdate")
    with c2:
        fd['approved_by']    = st.text_input(t('approved_by'), value=fd.get('approved_by',''), key="app_by")
        fd['overall_result'] = st.text_area(t('overall_result'), value=fd.get('overall_result',''), height=100, key="ores")

# ── Generate button ──────────────────────────────────────────────────────────
st.markdown("---")
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    if st.button(t('generate_pdf'), use_container_width=True):
        if not fd.get('po_number') or not fd.get('brand'):
            st.error(f"⚠️ {t('fill_required')}")
        else:
            with st.spinner(f"⏳ {t('creating_pdf')}"):
                try:
                    pdf_buf = generate_pdf()
                    st.success(f"✅ {t('generate_success')}")
                    with st.expander(f"ℹ️ {t('pdf_details')}"):
                        mc1, mc2 = st.columns(2)
                        with mc1:
                            st.metric(t('location'), f"{st.session_state.selected_city} ({CHINESE_CITIES.get(st.session_state.selected_city,'')})")
                            st.metric(t('report_language'), "中文" if st.session_state.pdf_language=="zh" else "English")
                        with mc2:
                            st.metric(t('generated'), datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%H:%M:%S'))
                    fname = f"WearTest_{fd.get('po_number','report')}_{st.session_state.selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label=t('download_pdf'),
                        data=pdf_buf, file_name=fname, mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ {t('error_generating')}: {str(e)}")
                    with st.expander("Debug"):
                        import traceback; st.code(traceback.format_exc())

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
  <p style="font-size:1.1rem;font-weight:700;color:#1a1a2e;margin-bottom:.4rem;">
    👟 {t('footer_text')}
  </p>
  <p style="font-size:.85rem;color:#555;">
    📍 {st.session_state.selected_city} ({CHINESE_CITIES.get(st.session_state.selected_city,'')}) &nbsp;|&nbsp;
    🌐 {("中文" if st.session_state.pdf_language=="zh" else "English")}
  </p>
  <p style="font-size:.75rem;color:#999;margin-top:.8rem;">
    {t('powered_by')} &nbsp;|&nbsp; {t('copyright')}
  </p>
</div>
""", unsafe_allow_html=True)
