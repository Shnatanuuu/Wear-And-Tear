import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import io
import pytz
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
else:
    openai_client = None
    st.warning("OpenAI API key not found. Translation features will be limited.")

# Page config
st.set_page_config(
    page_title="Grandstep Wear Test Assessment",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chinese cities dictionary
CHINESE_CITIES = {
    "Guangzhou": "广州",
    "Shenzhen": "深圳",
    "Dongguan": "东莞",
    "Foshan": "佛山",
    "Zhongshan": "中山",
    "Huizhou": "惠州",
    "Zhuhai": "珠海",
    "Jiangmen": "江门",
    "Zhaoqing": "肇庆",
    "Shanghai": "上海",
    "Beijing": "北京",
    "Suzhou": "苏州",
    "Hangzhou": "杭州",
    "Ningbo": "宁波",
    "Wenzhou": "温州",
    "Wuhan": "武汉",
    "Chengdu": "成都",
    "Chongqing": "重庆",
    "Tianjin": "天津",
    "Nanjing": "南京",
    "Xi'an": "西安",
    "Qingdao": "青岛",
    "Dalian": "大连",
    "Shenyang": "沈阳",
    "Changsha": "长沙",
    "Zhengzhou": "郑州",
    "Jinan": "济南",
    "Harbin": "哈尔滨",
    "Changchun": "长春",
    "Taiyuan": "太原",
    "Shijiazhuang": "石家庄",
    "Lanzhou": "兰州",
    "Xiamen": "厦门",
    "Fuzhou": "福州",
    "Nanning": "南宁",
    "Kunming": "昆明",
    "Guiyang": "贵阳",
    "Haikou": "海口",
    "Ürümqi": "乌鲁木齐",
    "Lhasa": "拉萨"
}

# Custom icons for better UI
ICONS = {
    "title": "👟",
    "basic_info": "📋",
    "fit_size": "📏",
    "tester": "👥",
    "before_trying": "🤚",
    "fit_walking": "🚶",
    "after_walking": "👣",
    "extended_wear": "📅",
    "comfort": "⭐",
    "appearance": "✨",
    "final": "📝",
    "generate": "🎯",
    "download": "📥",
    "settings": "⚙️",
    "language": "🌐",
    "location": "📍",
    "time": "🕐",
    "info": "ℹ️",
    "factory": "🏭",
    "brand": "🏷️",
    "color": "🎨",
    "style": "👕",
    "description": "📄",
    "sample": "🧪",
    "test": "🧪",
    "assessment": "📊",
    "success": "✅",
    "error": "⚠️",
    "warning": "⚠️"
}

# Custom CSS with enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        padding: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .section-header {
        font-size: 1.9rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding: 0.8rem 1.2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-header-icon {
        font-size: 1.8rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        padding: 1rem 2.5rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .stButton>button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: 0.5s;
    }
    .stButton>button:hover:before {
        left: 100%;
    }
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem;
        border-radius: 15px;
        color: white;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-right: 1px solid #dee2e6;
    }
    .stSelectbox, .stTextInput, .stTextArea, .stRadio {
        background-color: white;
        border-radius: 10px;
        padding: 0.8rem;
        box-shadow: 0 3px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
    }
    .stSelectbox:hover, .stTextInput:hover, .stTextArea:hover, .stRadio:hover {
        border-color: #667eea;
        box-shadow: 0 5px 10px rgba(102, 126, 234, 0.1);
    }
    .stExpander {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.2rem;
        border: 1px solid #e0e0e0;
        overflow: hidden;
    }
    .stExpander > div:first-child {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px 12px 0 0;
    }
    div[data-baseweb="tab"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px !important;
        padding: 0.5rem;
        margin: 0.2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .location-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        margin-top: 2rem;
        border-top: 3px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "en"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "en"
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Shanghai"
if 'translations_cache' not in st.session_state:
    st.session_state.translations_cache = {}

# Translation function using GPT-4o mini
def translate_text(text, target_language="zh"):
    """Translate text using GPT-4o mini with caching"""
    if not text or not text.strip():
        return text
    
    # Check cache first
    cache_key = f"{text}_{target_language}"
    if cache_key in st.session_state.translations_cache:
        return st.session_state.translations_cache[cache_key]
    
    # Don't translate numbers or alphanumeric codes
    if text.strip().replace('.', '').replace(',', '').replace('-', '').replace('/', '').isdigit():
        st.session_state.translations_cache[cache_key] = text
        return text
    
    if not openai_client:
        # Fallback translations if no API key
        st.session_state.translations_cache[cache_key] = text
        return text
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text to {'Chinese (Simplified)' if target_language == 'zh' else 'English'}. Only return the translation, no explanations. Preserve any numbers, dates, and special formatting."},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        translated_text = response.choices[0].message.content.strip()
        st.session_state.translations_cache[cache_key] = translated_text
        return translated_text
    except Exception as e:
        st.warning(f"Translation failed: {str(e)}. Using original text.")
        st.session_state.translations_cache[cache_key] = text
        return text

def translate_list(text_list, target_language="zh"):
    """Translate a list of texts"""
    return [translate_text(text, target_language) for text in text_list]

# Helper function to get translated text with caching
def get_text(key, fallback=None):
    """Get translated text based on current UI language"""
    lang = st.session_state.ui_language
    
    # Base English texts
    texts = {
        "title": "Grandstep Wear Test Assessment",
        "basic_info": "Basic Information",
        "fit_size_tester": "Fit Size & Tester Information",
        "before_trying": "A. Before Trying On (Touch & Feel)",
        "fit_before_walking": "B. Fit Before Walking (Standing)",
        "after_walking": "C. After 8-15 Minutes of Walking",
        "extended_wear": "D. Extended Wear Testing (Over Time)",
        "comfort_appearance": "E. Comfort & Appearance Index",
        "final_assessment": "Final Assessment",
        "generate_pdf": "Generate PDF Report",
        "download_pdf": "Download PDF Report",
        "po_number": "PO Number",
        "factory": "Factory",
        "color": "Color",
        "style": "Style",
        "brand": "Brand",
        "description": "Description",
        "sample_type": "Sample Type",
        "testers": "Testers",
        "fit_sizes": "Fit Sizes",
        "upper_feel": "Upper Material Feel",
        "lining_feel": "Lining Material Feel",
        "sock_feel": "Sock Cushion Feel",
        "prepared_by": "Prepared By",
        "approved_by": "Approved By",
        "overall_result": "Overall Result",
        "footer_text": "Grandstep Wear Test Assessment System",
        "generate_success": "PDF Generated Successfully!",
        "fill_required": "Please fill in at least PO Number and Brand!",
        "creating_pdf": "Creating your professional PDF report...",
        "pdf_details": "PDF Details",
        "report_language": "Report Language",
        "generated": "Generated",
        "location": "Location",
        "error_generating": "Error generating PDF",
        "select_location": "Select Location",
        "user_interface_language": "User Interface Language",
        "pdf_report_language": "PDF Report Language",
        "test_location": "Test Location",
        "local_time": "Local Time",
        "quick_guide": "Quick Guide",
        "powered_by": "Powered by Streamlit",
        "copyright": "© 2025 - Professional Footwear Testing Platform"
    }
    
    text = texts.get(key, fallback or key)
    
    # Translate if needed
    if lang == "zh" and openai_client:
        return translate_text(text, "zh")
    return text

# Helper functions for styling
def get_color_for_rating(rating):
    """Get color based on rating"""
    rating_lower = rating.lower()
    if "comfortable" in rating_lower and "somewhat" not in rating_lower:
        return "#2ecc71"  # Green
    elif "somewhat" in rating_lower:
        return "#f39c12"  # Orange
    else:
        return "#e74c3c"  # Red

def get_yes_no_color(response):
    """Get color for Yes/No responses"""
    return "#2ecc71" if response.lower() == "yes" else "#e74c3c"

def get_score_color(score):
    """Get color for numeric scores"""
    if score >= 4:
        return "#2ecc71"  # Green
    elif score >= 3:
        return "#f39c12"  # Orange
    else:
        return "#e74c3c"  # Red

def translate_pdf_content(text, pdf_lang):
    """Translate text for PDF based on selected language"""
    if pdf_lang == "en" or not openai_client:
        return text
    return translate_text(text, "zh")

# Enhanced PDF Generation with Headers and Footers
class PDFWithHeaderFooter(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self.header_text = kwargs.pop('header_text', '')
        self.location = kwargs.pop('location', '')
        self.pdf_language = kwargs.pop('pdf_language', 'en')
        self.selected_city = kwargs.pop('selected_city', '')
        self.chinese_city = kwargs.pop('chinese_city', '')
        self.chinese_font = kwargs.pop('chinese_font', 'Helvetica')
        super().__init__(*args, **kwargs)
        
    def afterFlowable(self, flowable):
        """Add header and footer"""
        if isinstance(flowable, PageBreak):
            return
            
        # Add header on all pages except first
        if self.page > 1:
            self.canv.saveState()
            # Header with gradient effect
            self.canv.setFillColor(colors.HexColor('#667eea'))
            self.canv.rect(0, self.pagesize[1] - 0.6*inch, self.pagesize[0], 0.6*inch, fill=1, stroke=0)
            
            # Use Chinese font if needed
            font_size = 12
            if self.pdf_language == "zh":
                self.canv.setFont(self.chinese_font, font_size)
                header_title = "GRAND STEP (H.K.) LTD - 穿着测试评估"
            else:
                self.canv.setFont('Helvetica-Bold', font_size)
                header_title = "GRAND STEP (H.K.) LTD - WEAR TEST ASSESSMENT"
                
            self.canv.setFillColor(colors.white)
            self.canv.drawCentredString(
                self.pagesize[0]/2.0, 
                self.pagesize[1] - 0.4*inch, 
                header_title
            )
            self.canv.restoreState()
            
        # Footer on all pages
        self.canv.saveState()
        
        # Footer background with subtle gradient
        self.canv.setFillColor(colors.HexColor('#f8f9fa'))
        self.canv.rect(0, 0, self.pagesize[0], 0.7*inch, fill=1, stroke=0)
        
        # Top border
        self.canv.setStrokeColor(colors.HexColor('#667eea'))
        self.canv.setLineWidth(1)
        self.canv.line(0, 0.7*inch, self.pagesize[0], 0.7*inch)
        
        # Footer text - use Chinese font if needed
        font_size = 8
        if self.pdf_language == "zh":
            self.canv.setFont(self.chinese_font, font_size)
        else:
            self.canv.setFont('Helvetica', font_size)
            
        self.canv.setFillColor(colors.HexColor('#666666'))
        
        # Left: Location
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(china_tz)
        
        if self.pdf_language == "zh" and self.chinese_city:
            location_info = f"地点: {self.selected_city} ({self.chinese_city})"
        else:
            location_info = f"Location: {self.selected_city}"
        
        self.canv.drawString(0.5*inch, 0.25*inch, location_info)
        
        # Center: Timestamp
        if self.pdf_language == "zh":
            timestamp = f"生成时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            timestamp = f"Generated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.canv.drawCentredString(self.pagesize[0]/2.0, 0.25*inch, timestamp)
        
        # Right: Page number
        if self.pdf_language == "zh":
            page_num = f"第 {self.page} 页"
        else:
            page_num = f"Page {self.page}"
        self.canv.drawRightString(self.pagesize[0] - 0.5*inch, 0.25*inch, page_num)
        
        self.canv.restoreState()

def generate_pdf():
    buffer = io.BytesIO()
    
    # Get location info
    selected_city = st.session_state.selected_city
    chinese_city = CHINESE_CITIES[selected_city]
    pdf_lang = st.session_state.pdf_language
    
    # Register Chinese font if needed
    chinese_font = 'Helvetica'  # Default font
    
    if pdf_lang == "zh":
        try:
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                chinese_font = 'STSong-Light'
            except Exception as e1:
                try:
                    pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
                    chinese_font = 'SimSun'
                except Exception as e2:
                    try:
                        pdfmetrics.registerFont(TTFont('YaHei', 'msyh.ttc'))
                        chinese_font = 'YaHei'
                    except Exception as e3:
                        chinese_font = 'Helvetica'
        except Exception as e:
            chinese_font = 'Helvetica'
    
    # Create PDF with custom header/footer
    doc = PDFWithHeaderFooter(
        buffer, 
        pagesize=A4,
        topMargin=0.8*inch,
        bottomMargin=0.8*inch,
        header_text="GRAND STEP (H.K.) LTD - WEAR TEST ASSESSMENT",
        location=f"{selected_city}",
        pdf_language=pdf_lang,
        selected_city=selected_city,
        chinese_city=chinese_city,
        chinese_font=chinese_font
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Create styles with appropriate fonts
    title_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    normal_font = 'Helvetica' if pdf_lang != "zh" else chinese_font
    bold_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    
    # Improved title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName=bold_font,
        underlineWidth=1,
        underlineColor=colors.HexColor('#764ba2'),
        underlineOffset=-3
    )
    
    # Company header style
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName=bold_font
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#764ba2'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName=bold_font
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.white,
        spaceAfter=10,
        spaceBefore=12,
        fontName=bold_font,
        borderPadding=8,
        borderColor=colors.HexColor('#667eea'),
        borderWidth=1,
        borderRadius=6,
        backColor=colors.HexColor('#667eea'),
        alignment=TA_LEFT
    )
    
    # Add Chinese normal style
    chinese_normal_style = ParagraphStyle(
        'ChineseNormal',
        parent=styles['Normal'],
        fontName=normal_font,
        fontSize=9,
        leading=12
    )
    styles.add(chinese_normal_style)
    
    # Company Header
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("GRAND STEP (H.K.) LTD", company_style))
    
    # Title
    report_title = translate_pdf_content("WEAR TEST ASSESSMENT REPORT", pdf_lang)
    elements.append(Paragraph(report_title, title_style))
    
    # Location and date
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    
    if pdf_lang == "zh":
        location_text = f"地点: {selected_city} ({chinese_city})"
    else:
        location_text = f"Location: {selected_city}"
    
    date_label = translate_pdf_content("Report Date", pdf_lang)
    date_text = f"{date_label}: {current_time.strftime('%Y-%m-%d')}"
    
    elements.append(Paragraph(location_text, subtitle_style))
    elements.append(Paragraph(date_text, subtitle_style))
    
    # Decorative line
    elements.append(Paragraph("<hr width='80%' color='#667eea'/>", chinese_normal_style))
    elements.append(Spacer(1, 20))
    
    # Helper function for creating paragraphs with appropriate font
    def create_paragraph(text, style=None, bold=False):
        """Create paragraph with appropriate font"""
        if style is None:
            style = chinese_normal_style if pdf_lang == "zh" else styles['Normal']
        
        if bold:
            font_name = bold_font
        else:
            font_name = normal_font
        
        custom_style = ParagraphStyle(
            f"CustomStyle_{bold}",
            parent=style,
            fontName=font_name
        )
        
        return Paragraph(text, custom_style)
    
    # Basic Info Table
    basic_title = translate_pdf_content("1. BASIC INFORMATION", pdf_lang)
    elements.append(Paragraph(basic_title, heading_style))
    
    basic_data = [
        [create_paragraph(translate_pdf_content("PO Number:", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content(po_number, pdf_lang)), 
         create_paragraph(translate_pdf_content("Color:", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content(color, pdf_lang))],
        [create_paragraph(translate_pdf_content("Brand:", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content(brand, pdf_lang)), 
         create_paragraph(translate_pdf_content("Date:", pdf_lang), bold=True), 
         create_paragraph(prep_date.strftime('%Y-%m-%d'))],
        [create_paragraph(translate_pdf_content("Factory:", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content(factory, pdf_lang)), 
         create_paragraph(translate_pdf_content("Style:", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content(style, pdf_lang))],
        [create_paragraph(translate_pdf_content("Description:", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content(description, pdf_lang)), 
         create_paragraph(translate_pdf_content("Sample Type:", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content(sample_type, pdf_lang))],
        [create_paragraph(translate_pdf_content("Testers:", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content(", ".join(testers), pdf_lang)), 
         create_paragraph(translate_pdf_content("Fit Sizes:", pdf_lang), bold=True), 
         create_paragraph(", ".join(fit_sizes))]
    ]
    
    basic_table = Table(basic_data, colWidths=[1.3*inch, 2.3*inch, 1.3*inch, 2.3*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f4ff')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f4ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (2, 0), (2, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d4d4d4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9ff')])
    ]))
    elements.append(basic_table)
    elements.append(Spacer(1, 20))
    
    # Section A
    section_a_title = translate_pdf_content("2. BEFORE TRYING ON (TOUCH & FEEL)", pdf_lang)
    elements.append(Paragraph(section_a_title, heading_style))
    
    feel_data = [
        [create_paragraph(translate_pdf_content("Aspect", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content("Rating", pdf_lang), bold=True)],
        [create_paragraph(translate_pdf_content("Upper Material Feel", pdf_lang)), 
         Paragraph(f'<font color="{get_color_for_rating(upper_feel)}">{translate_pdf_content(upper_feel, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Lining Material Feel", pdf_lang)), 
         Paragraph(f'<font color="{get_color_for_rating(lining_feel)}">{translate_pdf_content(lining_feel, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Sock Cushion Feel", pdf_lang)), 
         Paragraph(f'<font color="{get_color_for_rating(sock_feel)}">{translate_pdf_content(sock_feel, pdf_lang)}</font>', chinese_normal_style)]
    ]
    
    feel_table = Table(feel_data, colWidths=[3.5*inch, 2.5*inch])
    feel_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9ff')])
    ]))
    elements.append(feel_table)
    elements.append(Spacer(1, 20))
    
    # Section B
    section_b_title = translate_pdf_content("3. FIT BEFORE WALKING (STANDING)", pdf_lang)
    elements.append(Paragraph(section_b_title, heading_style))
    
    fit_data = [
        [create_paragraph(translate_pdf_content("Question", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content("Response", pdf_lang), bold=True)],
        [create_paragraph(translate_pdf_content("Is toe length okay?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(toe_length)}">{translate_pdf_content(toe_length, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Ball of foot at correct place?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(ball_position)}">{translate_pdf_content(ball_position, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Shoe flex at proper place?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(shoe_flex)}">{translate_pdf_content(shoe_flex, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Feel arch support?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(arch_support)}">{translate_pdf_content(arch_support, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Shoe gapping at top line?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(top_gapping)}">{translate_pdf_content(top_gapping, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Shoes fit properly?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(fit_properly)}">{translate_pdf_content(fit_properly, pdf_lang)}</font>', chinese_normal_style)]
    ]
    
    fit_table = Table(fit_data, colWidths=[4*inch, 2*inch])
    fit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9ff')])
    ]))
    elements.append(fit_table)
    elements.append(Spacer(1, 20))
    
    # Section C
    section_c_title = translate_pdf_content("4. AFTER 8-15 MINUTES WALKING", pdf_lang)
    elements.append(Paragraph(section_c_title, heading_style))
    
    walk_data = [
        [create_paragraph(translate_pdf_content("Question", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content("Response", pdf_lang), bold=True)],
        [create_paragraph(translate_pdf_content("Can feel shoe fit?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(feel_fit)}">{translate_pdf_content(feel_fit, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Interior lining feels good?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(interior_lining)}">{translate_pdf_content(interior_lining, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Can feel stability?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(feel_stability)}">{translate_pdf_content(feel_stability, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Shoe slipping?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(slipping)}">{translate_pdf_content(slipping, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Sole flexibility good?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(sole_flexibility)}">{translate_pdf_content(sole_flexibility, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Enough toe room?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(toe_room)}">{translate_pdf_content(toe_room, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Any rubbing?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(rubbing)}">{translate_pdf_content(rubbing, pdf_lang)}</font>', chinese_normal_style)],
        [create_paragraph(translate_pdf_content("Red marks after removing socks?", pdf_lang)), 
         Paragraph(f'<font color="{get_yes_no_color(red_marks)}">{translate_pdf_content(red_marks, pdf_lang)}</font>', chinese_normal_style)]
    ]
    
    walk_table = Table(walk_data, colWidths=[4*inch, 2*inch])
    walk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9ff')])
    ]))
    elements.append(walk_table)
    elements.append(PageBreak())
    
    # Section D
    section_d_title = translate_pdf_content("5. EXTENDED WEAR TESTING", pdf_lang)
    elements.append(Paragraph(section_d_title, heading_style))
    
    for period in time_periods:
        period_data = [
            [create_paragraph(translate_pdf_content("Question", pdf_lang), bold=True), 
             create_paragraph(translate_pdf_content("Response", pdf_lang), bold=True)]
        ]
        for q in questions_d:
            response = extended_data[period][q]
            period_data.append([
                create_paragraph(translate_pdf_content(q, pdf_lang)), 
                Paragraph(f'<font color="{get_yes_no_color(response)}">{translate_pdf_content(response, pdf_lang)}</font>', chinese_normal_style)
            ])
        
        elements.append(Paragraph(translate_pdf_content(period, pdf_lang), styles['Heading3']))
        period_table = Table(period_data, colWidths=[4*inch, 2*inch])
        period_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9ff')])
        ]))
        elements.append(period_table)
        elements.append(Spacer(1, 12))
    
    elements.append(PageBreak())
    
    # Section E
    section_e_title = translate_pdf_content("6. COMFORT & APPEARANCE INDEX", pdf_lang)
    elements.append(Paragraph(section_e_title, heading_style))
    
    index_data = [
        [
            create_paragraph(translate_pdf_content("Day", pdf_lang), bold=True), 
            create_paragraph(translate_pdf_content("Comfort (1-5)", pdf_lang), bold=True), 
            create_paragraph(translate_pdf_content("Appearance (1-5)", pdf_lang), bold=True), 
            create_paragraph(translate_pdf_content("Issues Noticed", pdf_lang), bold=True)
        ]
    ]
    
    for day in days_to_track:
        comfort_color = get_score_color(comfort_scores[day])
        appear_color = get_score_color(appearance_scores[day])
        
        issue_text = translate_pdf_content(issues[day], pdf_lang)
        
        index_data.append([
            create_paragraph(translate_pdf_content(day, pdf_lang)),
            Paragraph(f'<font color="{comfort_color}"><b>{comfort_scores[day]}</b></font>', chinese_normal_style),
            Paragraph(f'<font color="{appear_color}"><b>{appearance_scores[day]}</b></font>', chinese_normal_style),
            issue_text[:60] + "..." if len(issue_text) > 60 else issue_text
        ])
    
    index_table = Table(index_data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 2.5*inch])
    index_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9ff')])
    ]))
    elements.append(index_table)
    elements.append(Spacer(1, 25))
    
    # Final Assessment
    final_title = translate_pdf_content("7. FINAL ASSESSMENT", pdf_lang)
    elements.append(Paragraph(f"{final_title}", heading_style))
    
    translated_result = translate_pdf_content(overall_result, pdf_lang)
    
    final_data = [
        [create_paragraph(translate_pdf_content("Prepared By:", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content(prepared_by, pdf_lang)), 
         create_paragraph(translate_pdf_content("Date:", pdf_lang), bold=True), 
         create_paragraph(prep_date.strftime('%Y-%m-%d'))],
        [create_paragraph(translate_pdf_content("Approved By:", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content(approved_by, pdf_lang)), 
         create_paragraph(translate_pdf_content("Overall Result:", pdf_lang), bold=True), 
         create_paragraph(translated_result)]
    ]
    
    final_table = Table(final_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    final_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f4ff')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f4ff')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (2, 0), (2, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(final_table)
    
    # Signature lines
    elements.append(Spacer(1, 40))
    sig_data = [
        ['', ''],
        ['_________________________', '_________________________'],
        [create_paragraph(translate_pdf_content("Prepared By Signature", pdf_lang), bold=True), 
         create_paragraph(translate_pdf_content("Approved By Signature", pdf_lang), bold=True)]
    ]
    
    sig_table = Table(sig_data, colWidths=[3*inch, 3*inch])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 2), (-1, 2), bold_font),
        ('SPACEAFTER', (0, 0), (-1, -1), 5),
    ]))
    elements.append(sig_table)
    
    # Footer note
    elements.append(Spacer(1, 15))
    footer_note = translate_pdf_content(
        "This report is confidential and property of GRAND STEP (H.K.) LTD. Unauthorized distribution is prohibited.",
        pdf_lang
    )
    elements.append(Paragraph(footer_note, chinese_normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Sidebar with enhanced filters
with st.sidebar:
    st.markdown(f'### {ICONS["settings"]} Settings & Filters')
    
    # Language filters with icons
    st.markdown(f'#### {ICONS["language"]} Language Settings')
    ui_language = st.selectbox(
        "User Interface Language",
        ["English", "Mandarin"],
        index=0 if st.session_state.ui_language == "en" else 1,
        key="ui_lang_select"
    )
    st.session_state.ui_language = "en" if ui_language == "English" else "zh"
    
    pdf_language = st.selectbox(
        "PDF Report Language",
        ["English", "Mandarin"],
        index=0 if st.session_state.pdf_language == "en" else 1,
        key="pdf_lang_select"
    )
    st.session_state.pdf_language = "en" if pdf_language == "English" else "zh"
    
    # Location filter with enhanced UI
    st.markdown(f'#### {ICONS["location"]} Location Settings')
    selected_city = st.selectbox(
        "Select Test Location",
        list(CHINESE_CITIES.keys()),
        index=list(CHINESE_CITIES.keys()).index(st.session_state.selected_city) 
        if st.session_state.selected_city in CHINESE_CITIES else 0,
        key="city_select"
    )
    st.session_state.selected_city = selected_city
    
    # Display selected location in a badge
    st.markdown(f"""
    <div class="location-badge">
        {ICONS["location"]} {selected_city} ({CHINESE_CITIES[selected_city]})
    </div>
    """, unsafe_allow_html=True)
    
    # Timezone information
    st.markdown(f'#### {ICONS["time"]} Timezone Info')
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    st.metric(
        "Local Time", 
        current_time.strftime('%H:%M:%S'),
        current_time.strftime('%Y-%m-%d')
    )
    
    # Translation status
    if openai_client:
        st.success(f"{ICONS['success']} Translation API: Active")
    else:
        st.warning(f"{ICONS['warning']} Translation API: Not Configured")
    
    st.markdown("---")
    
    # Quick stats
    st.markdown(f'#### {ICONS["info"]} Report Stats')
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Cities", len(CHINESE_CITIES))
    with col2:
        st.metric("Languages", 2)
    
    st.markdown("---")
    st.markdown(f'### {ICONS["info"]} Instructions')
    st.info(f"""
    {ICONS["info"]} **Quick Guide:**
    1. {ICONS["basic_info"]} Fill all required fields
    2. {ICONS["language"]} Select preferred languages
    3. {ICONS["location"]} Choose testing location
    4. {ICONS["generate"]} Generate PDF report
    5. {ICONS["download"]} Download and share
    """)

# Title with enhanced styling
st.markdown(f"""
<div class="main-header">
    {ICONS["title"]} {get_text("title")}
</div>
""", unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs([
    f"{ICONS['basic_info']} {get_text('basic_info')}",
    f"{ICONS['test']} Testing Data",
    f"{ICONS['assessment']} {get_text('final_assessment')}"
])

with tab1:
    # Basic Information
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["basic_info"]}</span>
        {get_text("basic_info")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        po_number = st.text_input(
            f"{ICONS['description']} {get_text('po_number')}", 
            placeholder="Enter PO number"
        )
        factory = st.text_input(
            f"{ICONS['factory']} {get_text('factory')}", 
            placeholder="Factory name"
        )
    with col2:
        color = st.text_input(
            f"{ICONS['color']} {get_text('color')}", 
            placeholder="Color"
        )
        style = st.text_input(
            f"{ICONS['style']} {get_text('style')}", 
            placeholder="Style"
        )
    with col3:
        brand = st.text_input(
            f"{ICONS['brand']} {get_text('brand')}", 
            placeholder="Brand name"
        )
        sample_type = st.radio(
            f"{ICONS['sample']} {get_text('sample_type')}",
            ["Prototype", "Full Size", "Die Cut", "Mass Production"], 
            horizontal=True
        )
    
    description = st.text_area(
        f"{ICONS['description']} {get_text('description')}", 
        placeholder="Enter detailed product description here...",
        height=120
    )
    
    # Fit Size and Tester
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["fit_size"]}</span>
        {get_text("fit_size_tester")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fit_sizes = st.multiselect(
            f"{ICONS['fit_size']} {get_text('fit_sizes')}",
            ["4/6/37", "6/8/39", "8/10/41"], 
            default=["6/8/39"]
        )
    with col2:
        testers = st.multiselect(
            f"{ICONS['tester']} {get_text('testers')}",
            ["Tester A", "Tester B", "Tester C"], 
            default=["Tester A"]
        )

with tab2:
    # Section A: Before Trying On
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["before_trying"]}</span>
        {get_text("before_trying")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**{ICONS['style']} {get_text('upper_feel')}**")
        upper_feel = st.radio(
            "How does the upper material feel?", 
            ["Uncomfortable", "Somewhat Comfortable", "Comfortable"],
            key="upper_feel", 
            label_visibility="collapsed",
            horizontal=True
        )
    with col2:
        st.markdown(f"**{ICONS['style']} {get_text('lining_feel')}**")
        lining_feel = st.radio(
            "How does the lining feel?", 
            ["Uncomfortable", "Somewhat Comfortable", "Comfortable"],
            key="lining_feel", 
            label_visibility="collapsed",
            horizontal=True
        )
    with col3:
        st.markdown(f"**{ICONS['style']} {get_text('sock_feel')}**")
        sock_feel = st.radio(
            "How does the sock cushion feel?", 
            ["Uncomfortable", "Somewhat Comfortable", "Comfortable"],
            key="sock_feel", 
            label_visibility="collapsed",
            horizontal=True
        )
    
    # Section B: Fit Before Walking
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["fit_walking"]}</span>
        {get_text("fit_before_walking")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        toe_length = st.radio("Is the toe length okay?", ["No", "Yes"], horizontal=True)
        ball_position = st.radio("Is the ball of foot at correct place?", ["No", "Yes"], horizontal=True)
        shoe_flex = st.radio("Does the shoe flex at proper place?", ["No", "Yes"], horizontal=True)
    with col2:
        arch_support = st.radio("Feel arch support in correct position?", ["No", "Yes"], horizontal=True)
        top_gapping = st.radio("Is the shoe gapping at top line?", ["No", "Yes"], horizontal=True)
        fit_properly = st.radio("Does it appear shoes fit properly?", ["No", "Yes"], horizontal=True)
    
    # Section C: After Walking
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["after_walking"]}</span>
        {get_text("after_walking")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        feel_fit = st.radio("Can you feel the shoe fit?", ["No", "Yes"], horizontal=True, key="feel_fit")
        feel_stability = st.radio("Can you feel shoe stability?", ["No", "Yes"], horizontal=True, key="stability")
        sole_flexibility = st.radio("Does sole have good flexibility?", ["No", "Yes"], horizontal=True, key="flex")
        rubbing = st.radio("Any piece rubbing your feet?", ["No", "Yes"], horizontal=True, key="rub")
    with col2:
        interior_lining = st.radio("Does interior lining feel good?", ["No", "Yes"], horizontal=True, key="lining")
        slipping = st.radio("Is shoe slipping on feet?", ["No", "Yes"], horizontal=True, key="slip")
        toe_room = st.radio("Enough room in toe area?", ["No", "Yes"], horizontal=True, key="toe")
        red_marks = st.radio("Red marks after removing socks?", ["No", "Yes"], horizontal=True, key="marks")

with tab3:
    # Define time periods and questions for Section D
    time_periods = ["1 Hour", "1 Day", "1 Week", "2 Weeks", "3 Weeks", "4 Weeks"]
    questions_d = [
        "Does shoe feel unstable when walking?",
        "Any upper broken or damage?",
        "Any sole gapping?",
        "Does lining color come off?",
        "Any appearance changes?",
        "Any piece rubbing feet?",
        "Is bottom severely worn?"
    ]
    
    # Section D: Extended Wear Testing
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["extended_wear"]}</span>
        {get_text("extended_wear")}
    </div>
    """, unsafe_allow_html=True)
    
    extended_data = {}
    for period in time_periods:
        with st.expander(f"{ICONS['time']} {period} Assessment"):
            extended_data[period] = {}
            for q in questions_d:
                extended_data[period][q] = st.radio(q, ["No", "Yes"], horizontal=True, key=f"{period}_{q}")
    
    # Define days for Section E
    days_to_track = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7", 
                     "2 Weeks", "3 Weeks", "4 Weeks", "5 Weeks"]
    
    # Section E: Comfort & Appearance Index
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["comfort"]}</span>
        {get_text("comfort_appearance")}
    </div>
    """, unsafe_allow_html=True)
    
    comfort_scores = {}
    appearance_scores = {}
    issues = {}
    
    for day in days_to_track:
        with st.expander(f"{ICONS['assessment']} {day} Rating"):
            col1, col2, col3 = st.columns(3)
            with col1:
                comfort_scores[day] = st.slider(
                    f"{ICONS['comfort']} Comfort Level", 
                    1, 5, 3, 
                    key=f"comfort_{day}"
                )
            with col2:
                appearance_scores[day] = st.slider(
                    f"{ICONS['appearance']} Appearance", 
                    1, 5, 3, 
                    key=f"appear_{day}"
                )
            with col3:
                issues[day] = st.text_area(
                    f"{ICONS['info']} Issues Noticed", 
                    "", 
                    key=f"issue_{day}", 
                    height=80
                )
    
    # Final Assessment
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["final"]}</span>
        {get_text("final_assessment")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        prepared_by = st.text_input(
            f"{ICONS['tester']} {get_text('prepared_by')}", 
            placeholder="Your name"
        )
        prep_date = st.date_input(
            f"{ICONS['time']} Date", 
            datetime.now()
        )
    with col2:
        approved_by = st.text_input(
            f"{ICONS['tester']} {get_text('approved_by')}", 
            placeholder="Approver name"
        )
        overall_result = st.text_area(
            f"{ICONS['assessment']} {get_text('overall_result')}", 
            placeholder="Summary of test results...",
            height=120
        )

# Generate PDF Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(f"{ICONS['generate']} {get_text('generate_pdf')}", use_container_width=True):
        if not po_number or not brand:
            st.error(f"{ICONS['error']} {get_text('fill_required')}")
        else:
            with st.spinner(f"{ICONS['time']} {get_text('creating_pdf')}"):
                try:
                    pdf_buffer = generate_pdf()
                    st.success(f"{ICONS['success']} {get_text('generate_success')}")
                    
                    # Display PDF preview info
                    with st.expander(f"{ICONS['info']} {get_text('pdf_details')}"):
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric(get_text("location"), f"{selected_city} ({CHINESE_CITIES[selected_city]})")
                            st.metric(get_text("report_language"), "Mandarin" if st.session_state.pdf_language == "zh" else "English")
                        with col_info2:
                            china_tz = pytz.timezone('Asia/Shanghai')
                            current_time = datetime.now(china_tz)
                            st.metric(get_text("generated"), current_time.strftime('%H:%M:%S'))
                    
                    # Download button
                    filename = f"Wear_Test_Report_{po_number}_{selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label=f"{ICONS['download']} {get_text('download_pdf')}",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"{ICONS['error']} {get_text('error_generating')}: {str(e)}")

# Footer
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <p style='font-size: 1.2rem; font-weight: 600; color: #667eea; margin-bottom: 0.5rem;'>
        {ICONS['title']} {get_text('footer_text')}
    </p>
    <p style='font-size: 0.9rem; color: #666666;'>
        {ICONS['location']} {get_text('location')}: {selected_city} ({CHINESE_CITIES[selected_city]}) | 
        {ICONS['language']} {get_text('report_language')}: {'Mandarin' if st.session_state.pdf_language == 'zh' else 'English'}
    </p>
    <p style='font-size: 0.8rem; color: #999999; margin-top: 1rem;'>
        {get_text('powered_by')} | {get_text('copyright')}
    </p>
</div>
""", unsafe_allow_html=True)

# Create .env file instructions in sidebar
with st.sidebar:
    with st.expander(f"{ICONS['info']} API Setup"):
        st.code("""
# Create .env file in your project folder
OPENAI_API_KEY=your-api-key-here
""")
        st.info("Restart the app after adding your API key to enable translations.")
