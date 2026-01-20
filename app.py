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
import re

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

# Initialize session state for all form data
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "en"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "en"
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Shanghai"
if 'translations_cache' not in st.session_state:
    st.session_state.translations_cache = {}
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'po_number': '',
        'factory': '',
        'color': '',
        'style': '',
        'brand': '',
        'sample_type': 'Prototype',
        'description': '',
        'fit_sizes': ['6/8/39'],
        'testers': ['Tester A'],
        'upper_feel': 'Comfortable',
        'lining_feel': 'Comfortable',
        'sock_feel': 'Comfortable',
        'toe_length': 'Yes',
        'ball_position': 'Yes',
        'shoe_flex': 'Yes',
        'arch_support': 'Yes',
        'top_gapping': 'No',
        'fit_properly': 'Yes',
        'feel_fit': 'Yes',
        'interior_lining': 'Yes',
        'feel_stability': 'Yes',
        'slipping': 'No',
        'sole_flexibility': 'Yes',
        'toe_room': 'Yes',
        'rubbing': 'No',
        'red_marks': 'No',
        'prepared_by': '',
        'prep_date': datetime.now().date(),
        'approved_by': '',
        'overall_result': '',
        'extended_data': {},
        'comfort_scores': {},
        'appearance_scores': {},
        'issues': {}
    }

# Store original English text separately
if 'original_english_texts' not in st.session_state:
    st.session_state.original_english_texts = {}

# Initialize extended wear data
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

# Initialize extended_data in session state
if 'extended_data' not in st.session_state.form_data:
    st.session_state.form_data['extended_data'] = {}
    for period in time_periods:
        st.session_state.form_data['extended_data'][period] = {}
        for q in questions_d:
            st.session_state.form_data['extended_data'][period][q] = "No"

# Initialize comfort data
days_to_track = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7", 
                 "2 Weeks", "3 Weeks", "4 Weeks", "5 Weeks"]

if 'comfort_scores' not in st.session_state.form_data:
    st.session_state.form_data['comfort_scores'] = {}
    for day in days_to_track:
        st.session_state.form_data['comfort_scores'][day] = 3

if 'appearance_scores' not in st.session_state.form_data:
    st.session_state.form_data['appearance_scores'] = {}
    for day in days_to_track:
        st.session_state.form_data['appearance_scores'][day] = 3

if 'issues' not in st.session_state.form_data:
    st.session_state.form_data['issues'] = {}
    for day in days_to_track:
        st.session_state.form_data['issues'][day] = ""

# Enhanced translation function with better number preservation
def translate_text(text, target_language="zh", preserve_numbers=True):
    """Translate text using GPT-4o mini with enhanced caching and number preservation"""
    if not text or not text.strip():
        return text
    
    # Check cache first
    cache_key = f"{text}_{target_language}"
    if cache_key in st.session_state.translations_cache:
        return st.session_state.translations_cache[cache_key]
    
    # Don't translate if it's mostly numbers, codes, or dates
    if preserve_numbers:
        # Check for common patterns that shouldn't be translated
        patterns_to_preserve = [
            r'^\d+[/\-]\d+[/\-]\d+$',  # Dates like 2024-01-15
            r'^\d+[/\-]\d+$',  # Sizes like 6/8 or 8-10
            r'^[A-Z]+\d+$',  # Codes like PO1234
            r'^\d+$',  # Plain numbers
            r'^\d+\.\d+$',  # Decimal numbers
            r'^[A-Z]{2,3}\s*\d+$',  # Style codes like ABC 123
        ]
        
        for pattern in patterns_to_preserve:
            if re.match(pattern, text.strip()):
                st.session_state.translations_cache[cache_key] = text
                return text
        
        # Check if text contains Chinese characters (already translated)
        if re.search(r'[\u4e00-\u9fff]', text):
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
                {"role": "system", "content": f"""You are a professional translator. 
                 Translate the following text to {'Simplified Chinese' if target_language == 'zh' else 'English'}. 
                 IMPORTANT: Preserve all numbers, dates, codes (like PO numbers, sizes), measurements, 
                 and special formatting exactly as they appear. Only translate the text parts.
                 Return ONLY the translation, no explanations."""},
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

# Store and retrieve original English text
def store_original_text(key, text):
    """Store original English text for later translation"""
    if text and text.strip():
        st.session_state.original_english_texts[key] = text

def get_translated_for_display(key, text, target_language=None):
    """Get translated text for display based on current UI language"""
    if not text or not text.strip():
        return text
    
    if target_language is None:
        target_language = st.session_state.ui_language
    
    # Store original if not already stored
    if key not in st.session_state.original_english_texts:
        store_original_text(key, text)
    
    # If target language is English or no OpenAI client, return as-is
    if target_language == "en" or not openai_client:
        return text
    
    # If we have original English stored, use it for translation
    if key in st.session_state.original_english_texts:
        original = st.session_state.original_english_texts[key]
        return translate_text(original, target_language)
    
    # Otherwise translate the current text
    return translate_text(text, target_language)

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

def translate_pdf_content(text, pdf_lang, preserve_numbers=True):
    """Translate text for PDF based on selected language"""
    if pdf_lang == "en" or not openai_client:
        return text
    
    # First check if we have original English stored
    for key, original in st.session_state.original_english_texts.items():
        if original == text:
            # Use the stored original for consistent translation
            return translate_text(original, "zh", preserve_numbers)
    
    # Otherwise translate the text
    return translate_text(text, "zh", preserve_numbers)

def translate_form_data_for_pdf(data, pdf_lang):
    """Translate form data for PDF generation with proper handling"""
    if pdf_lang == "en" or not openai_client:
        return data
    
    if isinstance(data, (int, float)):
        return data
    elif isinstance(data, datetime):
        return data
    elif isinstance(data, list):
        translated_list = []
        for item in data:
            if isinstance(item, str):
                translated_list.append(translate_pdf_content(item, pdf_lang, preserve_numbers=True))
            else:
                translated_list.append(item)
        return translated_list
    elif isinstance(data, str):
        # Check if it's a date string
        try:
            datetime.strptime(data, '%Y-%m-%d')
            return data  # Don't translate date strings
        except ValueError:
            # Check if it's mostly numeric/alphanumeric
            temp_data = data.replace(' ', '').replace('-', '').replace('/', '').replace('.', '').replace(',', '')
            if temp_data.isalnum() and not re.search(r'[\u4e00-\u9fff]', data):
                # Check if it's likely a code or number
                if re.match(r'^[A-Za-z]*\d+[A-Za-z]*$', temp_data) or temp_data.isdigit():
                    return data  # Don't translate codes/numbers
            # Translate other text
            return translate_pdf_content(data, pdf_lang, preserve_numbers=True)
    else:
        return translate_pdf_content(str(data), pdf_lang, preserve_numbers=True)

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
    
    # Title - translate based on PDF language
    if pdf_lang == "zh":
        report_title = "穿着测试评估报告"
    else:
        report_title = "WEAR TEST ASSESSMENT REPORT"
    elements.append(Paragraph(report_title, title_style))
    
    # Location and date
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    
    if pdf_lang == "zh":
        location_text = f"地点: {selected_city} ({chinese_city})"
        date_label = "报告日期"
    else:
        location_text = f"Location: {selected_city}"
        date_label = "Report Date"
    
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
    
    # Get form data
    form_data = st.session_state.form_data
    
    # Translate ALL form data for PDF based on selected language
    translated_po_number = translate_form_data_for_pdf(form_data['po_number'], pdf_lang)
    translated_factory = translate_form_data_for_pdf(form_data['factory'], pdf_lang)
    translated_color = translate_form_data_for_pdf(form_data['color'], pdf_lang)
    translated_style = translate_form_data_for_pdf(form_data['style'], pdf_lang)
    translated_brand = translate_form_data_for_pdf(form_data['brand'], pdf_lang)
    translated_description = translate_form_data_for_pdf(form_data['description'], pdf_lang)
    translated_sample_type = translate_form_data_for_pdf(form_data['sample_type'], pdf_lang)
    translated_testers = translate_form_data_for_pdf(form_data['testers'], pdf_lang)
    translated_fit_sizes = translate_form_data_for_pdf(form_data['fit_sizes'], pdf_lang)
    translated_upper_feel = translate_form_data_for_pdf(form_data['upper_feel'], pdf_lang)
    translated_lining_feel = translate_form_data_for_pdf(form_data['lining_feel'], pdf_lang)
    translated_sock_feel = translate_form_data_for_pdf(form_data['sock_feel'], pdf_lang)
    translated_toe_length = translate_form_data_for_pdf(form_data['toe_length'], pdf_lang)
    translated_ball_position = translate_form_data_for_pdf(form_data['ball_position'], pdf_lang)
    translated_shoe_flex = translate_form_data_for_pdf(form_data['shoe_flex'], pdf_lang)
    translated_arch_support = translate_form_data_for_pdf(form_data['arch_support'], pdf_lang)
    translated_top_gapping = translate_form_data_for_pdf(form_data['top_gapping'], pdf_lang)
    translated_fit_properly = translate_form_data_for_pdf(form_data['fit_properly'], pdf_lang)
    translated_feel_fit = translate_form_data_for_pdf(form_data['feel_fit'], pdf_lang)
    translated_interior_lining = translate_form_data_for_pdf(form_data['interior_lining'], pdf_lang)
    translated_feel_stability = translate_form_data_for_pdf(form_data['feel_stability'], pdf_lang)
    translated_slipping = translate_form_data_for_pdf(form_data['slipping'], pdf_lang)
    translated_sole_flexibility = translate_form_data_for_pdf(form_data['sole_flexibility'], pdf_lang)
    translated_toe_room = translate_form_data_for_pdf(form_data['toe_room'], pdf_lang)
    translated_rubbing = translate_form_data_for_pdf(form_data['rubbing'], pdf_lang)
    translated_red_marks = translate_form_data_for_pdf(form_data['red_marks'], pdf_lang)
    translated_prepared_by = translate_form_data_for_pdf(form_data['prepared_by'], pdf_lang)
    translated_approved_by = translate_form_data_for_pdf(form_data['approved_by'], pdf_lang)
    translated_overall_result = translate_form_data_for_pdf(form_data['overall_result'], pdf_lang)
    
    # FIXED: Translate extended wear data - with proper error handling
    translated_extended_data = {}
    for period in time_periods:
        translated_period = translate_form_data_for_pdf(period, pdf_lang)
        translated_extended_data[translated_period] = {}
        
        # Check if period exists in form data
        if period not in form_data.get('extended_data', {}):
            # Initialize with default "No" values
            for q in questions_d:
                translated_q = translate_form_data_for_pdf(q, pdf_lang)
                translated_extended_data[translated_period][translated_q] = "No"
        else:
            # Use existing data
            for q in questions_d:
                translated_q = translate_form_data_for_pdf(q, pdf_lang)
                # Get the response - handle nested structure
                response = form_data['extended_data'].get(period, {}).get(q, "No")
                translated_response = translate_form_data_for_pdf(response, pdf_lang)
                translated_extended_data[translated_period][translated_q] = translated_response
    
    # Translate comfort data
    translated_days_to_track = [translate_form_data_for_pdf(day, pdf_lang) for day in days_to_track]
    translated_comfort_scores = {}
    translated_appearance_scores = {}
    translated_issues = {}
    
    for i, day in enumerate(days_to_track):
        translated_day = translated_days_to_track[i]
        translated_comfort_scores[translated_day] = form_data['comfort_scores'].get(day, 3)
        translated_appearance_scores[translated_day] = form_data['appearance_scores'].get(day, 3)
        translated_issues[translated_day] = translate_form_data_for_pdf(form_data['issues'].get(day, ""), pdf_lang)
    
    # Basic Info Table
    if pdf_lang == "zh":
        basic_title = "1. 基本信息"
    else:
        basic_title = "1. BASIC INFORMATION"
    elements.append(Paragraph(basic_title, heading_style))
    
    # Translate labels for PDF
    po_label = "PO编号:" if pdf_lang == "zh" else "PO Number:"
    color_label = "颜色:" if pdf_lang == "zh" else "Color:"
    brand_label = "品牌:" if pdf_lang == "zh" else "Brand:"
    date_label = "日期:" if pdf_lang == "zh" else "Date:"
    factory_label = "工厂:" if pdf_lang == "zh" else "Factory:"
    style_label = "款式:" if pdf_lang == "zh" else "Style:"
    description_label = "描述:" if pdf_lang == "zh" else "Description:"
    sample_type_label = "样品类型:" if pdf_lang == "zh" else "Sample Type:"
    testers_label = "测试人员:" if pdf_lang == "zh" else "Testers:"
    fit_sizes_label = "试穿尺码:" if pdf_lang == "zh" else "Fit Sizes:"
    
    basic_data = [
        [create_paragraph(po_label, bold=True), 
         create_paragraph(translated_po_number), 
         create_paragraph(color_label, bold=True), 
         create_paragraph(translated_color)],
        [create_paragraph(brand_label, bold=True), 
         create_paragraph(translated_brand), 
         create_paragraph(date_label, bold=True), 
         create_paragraph(form_data['prep_date'].strftime('%Y-%m-%d'))],
        [create_paragraph(factory_label, bold=True), 
         create_paragraph(translated_factory), 
         create_paragraph(style_label, bold=True), 
         create_paragraph(translated_style)],
        [create_paragraph(description_label, bold=True), 
         create_paragraph(translated_description), 
         create_paragraph(sample_type_label, bold=True), 
         create_paragraph(translated_sample_type)],
        [create_paragraph(testers_label, bold=True), 
         create_paragraph(", ".join(translated_testers) if isinstance(translated_testers, list) else translated_testers), 
         create_paragraph(fit_sizes_label, bold=True), 
         create_paragraph(", ".join(translated_fit_sizes) if isinstance(translated_fit_sizes, list) else translated_fit_sizes)]
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
    if pdf_lang == "zh":
        section_a_title = "2. 试穿前（触摸感觉）"
    else:
        section_a_title = "2. BEFORE TRYING ON (TOUCH & FEEL)"
    elements.append(Paragraph(section_a_title, heading_style))
    
    aspect_label = "方面" if pdf_lang == "zh" else "Aspect"
    rating_label = "评级" if pdf_lang == "zh" else "Rating"
    upper_label = "鞋面材料感觉" if pdf_lang == "zh" else "Upper Material Feel"
    lining_label = "内里材料感觉" if pdf_lang == "zh" else "Lining Material Feel"
    sock_label = "袜垫感觉" if pdf_lang == "zh" else "Sock Cushion Feel"
    
    feel_data = [
        [create_paragraph(aspect_label, bold=True), 
         create_paragraph(rating_label, bold=True)],
        [create_paragraph(upper_label), 
         Paragraph(f'<font color="{get_color_for_rating(form_data["upper_feel"])}">{translated_upper_feel}</font>', chinese_normal_style)],
        [create_paragraph(lining_label), 
         Paragraph(f'<font color="{get_color_for_rating(form_data["lining_feel"])}">{translated_lining_feel}</font>', chinese_normal_style)],
        [create_paragraph(sock_label), 
         Paragraph(f'<font color="{get_color_for_rating(form_data["sock_feel"])}">{translated_sock_feel}</font>', chinese_normal_style)]
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
    if pdf_lang == "zh":
        section_b_title = "3. 行走前合脚性（站立）"
    else:
        section_b_title = "3. FIT BEFORE WALKING (STANDING)"
    elements.append(Paragraph(section_b_title, heading_style))
    
    question_label = "问题" if pdf_lang == "zh" else "Question"
    response_label = "回答" if pdf_lang == "zh" else "Response"
    
    toe_length_q = "脚趾长度合适吗？" if pdf_lang == "zh" else "Is toe length okay?"
    ball_position_q = "脚掌位置正确吗？" if pdf_lang == "zh" else "Ball of foot at correct place?"
    shoe_flex_q = "鞋子弯曲位置正确吗？" if pdf_lang == "zh" else "Shoe flex at proper place?"
    arch_support_q = "感觉足弓支撑吗？" if pdf_lang == "zh" else "Feel arch support?"
    top_gapping_q = "鞋口处有空隙吗？" if pdf_lang == "zh" else "Shoe gapping at top line?"
    fit_properly_q = "鞋子合脚吗？" if pdf_lang == "zh" else "Shoes fit properly?"
    
    fit_data = [
        [create_paragraph(question_label, bold=True), 
         create_paragraph(response_label, bold=True)],
        [create_paragraph(toe_length_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["toe_length"])}">{translated_toe_length}</font>', chinese_normal_style)],
        [create_paragraph(ball_position_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["ball_position"])}">{translated_ball_position}</font>', chinese_normal_style)],
        [create_paragraph(shoe_flex_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["shoe_flex"])}">{translated_shoe_flex}</font>', chinese_normal_style)],
        [create_paragraph(arch_support_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["arch_support"])}">{translated_arch_support}</font>', chinese_normal_style)],
        [create_paragraph(top_gapping_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["top_gapping"])}">{translated_top_gapping}</font>', chinese_normal_style)],
        [create_paragraph(fit_properly_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["fit_properly"])}">{translated_fit_properly}</font>', chinese_normal_style)]
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
    if pdf_lang == "zh":
        section_c_title = "4. 行走8-15分钟后"
    else:
        section_c_title = "4. AFTER 8-15 MINUTES WALKING"
    elements.append(Paragraph(section_c_title, heading_style))
    
    feel_fit_q = "能感觉到鞋子合脚吗？" if pdf_lang == "zh" else "Can feel shoe fit?"
    interior_lining_q = "内里感觉好吗？" if pdf_lang == "zh" else "Interior lining feels good?"
    feel_stability_q = "能感觉到稳定性吗？" if pdf_lang == "zh" else "Can feel stability?"
    slipping_q = "鞋子滑脚吗？" if pdf_lang == "zh" else "Shoe slipping?"
    sole_flexibility_q = "鞋底柔韧性好吗？" if pdf_lang == "zh" else "Sole flexibility good?"
    toe_room_q = "脚趾区域有足够空间吗？" if pdf_lang == "zh" else "Enough toe room?"
    rubbing_q = "有任何摩擦吗？" if pdf_lang == "zh" else "Any rubbing?"
    red_marks_q = "脱袜后有红色印记吗？" if pdf_lang == "zh" else "Red marks after removing socks?"
    
    walk_data = [
        [create_paragraph(question_label, bold=True), 
         create_paragraph(response_label, bold=True)],
        [create_paragraph(feel_fit_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["feel_fit"])}">{translated_feel_fit}</font>', chinese_normal_style)],
        [create_paragraph(interior_lining_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["interior_lining"])}">{translated_interior_lining}</font>', chinese_normal_style)],
        [create_paragraph(feel_stability_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["feel_stability"])}">{translated_feel_stability}</font>', chinese_normal_style)],
        [create_paragraph(slipping_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["slipping"])}">{translated_slipping}</font>', chinese_normal_style)],
        [create_paragraph(sole_flexibility_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["sole_flexibility"])}">{translated_sole_flexibility}</font>', chinese_normal_style)],
        [create_paragraph(toe_room_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["toe_room"])}">{translated_toe_room}</font>', chinese_normal_style)],
        [create_paragraph(rubbing_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["rubbing"])}">{translated_rubbing}</font>', chinese_normal_style)],
        [create_paragraph(red_marks_q), 
         Paragraph(f'<font color="{get_yes_no_color(form_data["red_marks"])}">{translated_red_marks}</font>', chinese_normal_style)]
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
    if pdf_lang == "zh":
        section_d_title = "5. 延长穿着测试"
    else:
        section_d_title = "5. EXTENDED WEAR TESTING"
    elements.append(Paragraph(section_d_title, heading_style))
    
    # Use the translated extended data that we prepared earlier
    for period in translated_extended_data.keys():
        period_data = [
            [create_paragraph(question_label, bold=True), 
             create_paragraph(response_label, bold=True)]
        ]
        
        for q, response in translated_extended_data[period].items():
            period_data.append([
                create_paragraph(q), 
                Paragraph(f'<font color="{get_yes_no_color(response)}">{response}</font>', chinese_normal_style)
            ])
        
        elements.append(Paragraph(period, styles['Heading3']))
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
    if pdf_lang == "zh":
        section_e_title = "6. 舒适度与外观指数"
    else:
        section_e_title = "6. COMFORT & APPEARANCE INDEX"
    elements.append(Paragraph(section_e_title, heading_style))
    
    day_label = "天数" if pdf_lang == "zh" else "Day"
    comfort_label = "舒适度 (1-5)" if pdf_lang == "zh" else "Comfort (1-5)"
    appearance_label = "外观 (1-5)" if pdf_lang == "zh" else "Appearance (1-5)"
    issues_label = "发现的问题" if pdf_lang == "zh" else "Issues Noticed"
    
    index_data = [
        [
            create_paragraph(day_label, bold=True), 
            create_paragraph(comfort_label, bold=True), 
            create_paragraph(appearance_label, bold=True), 
            create_paragraph(issues_label, bold=True)
        ]
    ]
    
    for day in translated_days_to_track:
        comfort_color = get_score_color(translated_comfort_scores[day])
        appear_color = get_score_color(translated_appearance_scores[day])
        
        issue_text = translated_issues[day]
        
        index_data.append([
            create_paragraph(day),
            Paragraph(f'<font color="{comfort_color}"><b>{translated_comfort_scores[day]}</b></font>', chinese_normal_style),
            Paragraph(f'<font color="{appear_color}"><b>{translated_appearance_scores[day]}</b></font>', chinese_normal_style),
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
    if pdf_lang == "zh":
        final_title = "7. 最终评估"
    else:
        final_title = "7. FINAL ASSESSMENT"
    elements.append(Paragraph(f"{final_title}", heading_style))
    
    prepared_by_label = "准备人:" if pdf_lang == "zh" else "Prepared By:"
    date_label = "日期:" if pdf_lang == "zh" else "Date:"
    approved_by_label = "批准人:" if pdf_lang == "zh" else "Approved By:"
    overall_result_label = "总体结果:" if pdf_lang == "zh" else "Overall Result:"
    
    final_data = [
        [create_paragraph(prepared_by_label, bold=True), 
         create_paragraph(translated_prepared_by), 
         create_paragraph(date_label, bold=True), 
         create_paragraph(form_data['prep_date'].strftime('%Y-%m-%d'))],
        [create_paragraph(approved_by_label, bold=True), 
         create_paragraph(translated_approved_by), 
         create_paragraph(overall_result_label, bold=True), 
         create_paragraph(translated_overall_result)]
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
    prepared_by_sig = "准备人签名" if pdf_lang == "zh" else "Prepared By Signature"
    approved_by_sig = "批准人签名" if pdf_lang == "zh" else "Approved By Signature"
    
    sig_data = [
        ['', ''],
        ['_________________________', '_________________________'],
        [create_paragraph(prepared_by_sig, bold=True), 
         create_paragraph(approved_by_sig, bold=True)]
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
    if pdf_lang == "zh":
        footer_note = "本报告为GRAND STEP (H.K.) LTD机密文件，未经授权禁止分发。"
    else:
        footer_note = "This report is confidential and property of GRAND STEP (H.K.) LTD. Unauthorized distribution is prohibited."
    elements.append(Paragraph(footer_note, chinese_normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
# Enhanced helper function to display text input with proper translation
def translated_text_input(label, key, placeholder="", type="text"):
    """Create a text input that properly handles translation between languages"""
    # Get current value from session state
    current_value = st.session_state.form_data[key]
    
    # Store original English text when first entered
    if current_value and key not in st.session_state.original_english_texts:
        store_original_text(key, current_value)
    
    # Display translated value if UI is in Mandarin
    if st.session_state.ui_language == "zh" and openai_client:
        displayed_value = get_translated_for_display(key, current_value)
    else:
        displayed_value = current_value
    
    # Create the input field
    if type == "text":
        new_value = st.text_input(
            get_text(label),
            value=displayed_value,
            placeholder=get_text(placeholder) if placeholder else "",
            key=f"input_{key}"
        )
    elif type == "textarea":
        new_value = st.text_area(
            get_text(label),
            value=displayed_value,
            placeholder=get_text(placeholder) if placeholder else "",
            height=120,
            key=f"input_{key}"
        )
    
    # Update session state if value changed
    if new_value != displayed_value:
        if st.session_state.ui_language == "zh" and openai_client and new_value:
            # User entered text in Mandarin UI - check if it's different from displayed
            if new_value != displayed_value:
                # This could be new text or edited text
                # For simplicity, store as English (translate if possible)
                try:
                    # Check if it looks like Chinese text
                    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
                    if chinese_pattern.search(new_value):
                        # Translate back to English for storage
                        english_value = translate_text(new_value, "en")
                        st.session_state.form_data[key] = english_value
                        store_original_text(key, english_value)
                    else:
                        # Not Chinese, store as-is
                        st.session_state.form_data[key] = new_value
                        store_original_text(key, new_value)
                except:
                    st.session_state.form_data[key] = new_value
                    store_original_text(key, new_value)
        else:
            # English UI or no OpenAI - store as-is
            st.session_state.form_data[key] = new_value
            if new_value:
                store_original_text(key, new_value)
    
    return st.session_state.form_data[key]

# Enhanced helper function for radio buttons
def translated_radio(label, key, options, index=0, horizontal=True):
    """Create a radio button with proper translation handling"""
    # Get current value from session state
    current_value = st.session_state.form_data[key]
    
    # Store original if not already stored
    if current_value and f"{key}_options" not in st.session_state.original_english_texts:
        st.session_state.original_english_texts[f"{key}_options"] = options
    
    # Translate options if UI is in Mandarin
    if st.session_state.ui_language == "zh" and openai_client:
        translated_options = [translate_text(opt, "zh") for opt in options]
        # Find current value in translated options
        try:
            current_translated = translate_text(current_value, "zh")
            if current_translated in translated_options:
                index = translated_options.index(current_translated)
        except:
            index = 0
    else:
        translated_options = options
        try:
            index = options.index(current_value) if current_value in options else 0
        except:
            index = 0
    
    # Create radio button
    selected = st.radio(
        get_text(label),
        translated_options,
        index=index,
        horizontal=horizontal,
        key=f"radio_{key}"
    )
    
    # Update session state
    if selected != (translate_text(current_value, "zh") if st.session_state.ui_language == "zh" and openai_client else current_value):
        if st.session_state.ui_language == "zh" and openai_client:
            # Find corresponding English option
            try:
                idx = translated_options.index(selected)
                english_value = options[idx]
                st.session_state.form_data[key] = english_value
            except:
                # Translate back to English
                english_value = translate_text(selected, "en")
                st.session_state.form_data[key] = english_value
        else:
            st.session_state.form_data[key] = selected
    
    return st.session_state.form_data[key]

# Enhanced helper function for multiselect
def translated_multiselect(label, key, options, default=None):
    """Create a multiselect with proper translation handling"""
    # Get current values from session state
    current_values = st.session_state.form_data[key]
    
    # Store original options if not already stored
    if f"{key}_options" not in st.session_state.original_english_texts:
        st.session_state.original_english_texts[f"{key}_options"] = options
    
    # Translate options if UI is in Mandarin
    if st.session_state.ui_language == "zh" and openai_client:
        translated_options = [translate_text(opt, "zh") for opt in options]
        # Translate current values for display
        if current_values:
            displayed_values = [translate_text(val, "zh") for val in current_values]
        else:
            displayed_values = []
    else:
        translated_options = options
        displayed_values = current_values if current_values else []
    
    # Create multiselect
    selected = st.multiselect(
        get_text(label),
        translated_options,
        default=displayed_values,
        key=f"multiselect_{key}"
    )
    
    # Update session state
    if selected != displayed_values:
        if st.session_state.ui_language == "zh" and openai_client:
            english_values = []
            for sel in selected:
                try:
                    idx = translated_options.index(sel)
                    english_values.append(options[idx])
                except:
                    # Translate back to English
                    english_values.append(translate_text(sel, "en"))
            st.session_state.form_data[key] = english_values
        else:
            st.session_state.form_data[key] = selected
    
    return st.session_state.form_data[key]

# Helper function for slider
def translated_slider(label, key, min_value, max_value, default_value):
    """Create a slider with translated label"""
    current_value = st.session_state.form_data.get(key, default_value)
    
    value = st.slider(
        get_text(label),
        min_value=min_value,
        max_value=max_value,
        value=current_value,
        key=f"slider_{key}"
    )
    
    st.session_state.form_data[key] = value
    return value

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
    # Update UI language if changed
    new_ui_lang = "en" if ui_language == "English" else "zh"
    if new_ui_lang != st.session_state.ui_language:
        st.session_state.ui_language = new_ui_lang
        # Clear translation cache to force refresh
        st.session_state.translations_cache = {}
        st.rerun()
    
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
        po_number = translated_text_input("po_number", "po_number", "Enter PO number")
        factory = translated_text_input("factory", "factory", "Factory name")
    with col2:
        color = translated_text_input("color", "color", "Color")
        style = translated_text_input("style", "style", "Style")
    with col3:
        brand = translated_text_input("brand", "brand", "Brand name")
        # Sample type radio
        st.markdown(f"**{get_text('sample_type')}**")
        sample_type = translated_radio(
            "",
            "sample_type",
            ["Prototype", "Full Size", "Die Cut", "Mass Production"],
            horizontal=True
        )
    
    description = translated_text_input("description", "description", "Enter detailed product description here...", type="textarea")
    
    # Fit Size and Tester
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["fit_size"]}</span>
        {get_text("fit_size_tester")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fit_sizes = translated_multiselect("fit_sizes", "fit_sizes", ["4/6/37", "6/8/39", "8/10/41"])
    with col2:
        testers = translated_multiselect("testers", "testers", ["Tester A", "Tester B", "Tester C"])

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
        upper_feel = translated_radio(
            "",
            "upper_feel",
            ["Uncomfortable", "Somewhat Comfortable", "Comfortable"],
            horizontal=True
        )
    with col2:
        st.markdown(f"**{ICONS['style']} {get_text('lining_feel')}**")
        lining_feel = translated_radio(
            "",
            "lining_feel",
            ["Uncomfortable", "Somewhat Comfortable", "Comfortable"],
            horizontal=True
        )
    with col3:
        st.markdown(f"**{ICONS['style']} {get_text('sock_feel')}**")
        sock_feel = translated_radio(
            "",
            "sock_feel",
            ["Uncomfortable", "Somewhat Comfortable", "Comfortable"],
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
        toe_length = translated_radio("Is the toe length okay?", "toe_length", ["No", "Yes"], horizontal=True)
        ball_position = translated_radio("Is the ball of foot at correct place?", "ball_position", ["No", "Yes"], horizontal=True)
        shoe_flex = translated_radio("Does the shoe flex at proper place?", "shoe_flex", ["No", "Yes"], horizontal=True)
    with col2:
        arch_support = translated_radio("Feel arch support in correct position?", "arch_support", ["No", "Yes"], horizontal=True)
        top_gapping = translated_radio("Is the shoe gapping at top line?", "top_gapping", ["No", "Yes"], horizontal=True)
        fit_properly = translated_radio("Does it appear shoes fit properly?", "fit_properly", ["No", "Yes"], horizontal=True)
    
    # Section C: After Walking
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["after_walking"]}</span>
        {get_text("after_walking")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        feel_fit = translated_radio("Can you feel the shoe fit?", "feel_fit", ["No", "Yes"], horizontal=True)
        feel_stability = translated_radio("Can you feel shoe stability?", "feel_stability", ["No", "Yes"], horizontal=True)
        sole_flexibility = translated_radio("Does sole have good flexibility?", "sole_flexibility", ["No", "Yes"], horizontal=True)
        rubbing = translated_radio("Any piece rubbing your feet?", "rubbing", ["No", "Yes"], horizontal=True)
    with col2:
        interior_lining = translated_radio("Does interior lining feel good?", "interior_lining", ["No", "Yes"], horizontal=True)
        slipping = translated_radio("Is shoe slipping on feet?", "slipping", ["No", "Yes"], horizontal=True)
        toe_room = translated_radio("Enough room in toe area?", "toe_room", ["No", "Yes"], horizontal=True)
        red_marks = translated_radio("Red marks after removing socks?", "red_marks", ["No", "Yes"], horizontal=True)

with tab3:
    # Section D: Extended Wear Testing
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["extended_wear"]}</span>
        {get_text("extended_wear")}
    </div>
    """, unsafe_allow_html=True)
    
    for period in time_periods:
        with st.expander(f"{ICONS['time']} {period} Assessment"):
            for q in questions_d:
                # Create a unique key for each question
                key = f"extended_{period}_{q}"
                
                # Get current value
                current_value = st.session_state.form_data['extended_data'].get(period, {}).get(q, "No")
                
                # Store original if not stored
                if current_value and key not in st.session_state.original_english_texts:
                    st.session_state.original_english_texts[key] = current_value
                
                # Display translated question if needed
                if st.session_state.ui_language == "zh" and openai_client:
                    display_q = translate_text(q, "zh")
                else:
                    display_q = q
                
                # Display translated value if needed
                if st.session_state.ui_language == "zh" and openai_client:
                    display_value = get_translated_for_display(key, current_value)
                else:
                    display_value = current_value
                
                # Create radio button
                options = ["No", "Yes"]
                if st.session_state.ui_language == "zh" and openai_client:
                    display_options = [translate_text(opt, "zh") for opt in options]
                else:
                    display_options = options
                
                selected = st.radio(
                    display_q,
                    display_options,
                    horizontal=True,
                    index=display_options.index(display_value) if display_value in display_options else 0,
                    key=f"extended_radio_{period}_{q}"
                )
                
                # Update session state
                if selected != display_value:
                    if st.session_state.ui_language == "zh" and openai_client:
                        # Translate back to English
                        try:
                            idx = display_options.index(selected)
                            english_value = options[idx]
                            if period not in st.session_state.form_data['extended_data']:
                                st.session_state.form_data['extended_data'][period] = {}
                            st.session_state.form_data['extended_data'][period][q] = english_value
                            store_original_text(key, english_value)
                        except:
                            english_value = translate_text(selected, "en")
                            if period not in st.session_state.form_data['extended_data']:
                                st.session_state.form_data['extended_data'][period] = {}
                            st.session_state.form_data['extended_data'][period][q] = english_value
                            store_original_text(key, english_value)
                    else:
                        if period not in st.session_state.form_data['extended_data']:
                            st.session_state.form_data['extended_data'][period] = {}
                        st.session_state.form_data['extended_data'][period][q] = selected
                        store_original_text(key, selected)
    
    # Section E: Comfort & Appearance Index
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["comfort"]}</span>
        {get_text("comfort_appearance")}
    </div>
    """, unsafe_allow_html=True)
    
    for day in days_to_track:
        with st.expander(f"{ICONS['assessment']} {day} Rating"):
            col1, col2, col3 = st.columns(3)
            with col1:
                # Comfort score slider
                comfort_key = f"comfort_{day}"
                comfort_value = translated_slider(f"{ICONS['comfort']} Comfort Level", comfort_key, 1, 5, 3)
                st.session_state.form_data['comfort_scores'][day] = comfort_value
            
            with col2:
                # Appearance score slider
                appearance_key = f"appearance_{day}"
                appearance_value = translated_slider(f"{ICONS['appearance']} Appearance", appearance_key, 1, 5, 3)
                st.session_state.form_data['appearance_scores'][day] = appearance_value
            
            with col3:
                # Issues text area
                issues_key = f"issues_{day}"
                current_issues = st.session_state.form_data['issues'].get(day, "")
                
                # Store original if not stored
                if current_issues and issues_key not in st.session_state.original_english_texts:
                    st.session_state.original_english_texts[issues_key] = current_issues
                
                # Display translated if needed
                if st.session_state.ui_language == "zh" and openai_client:
                    display_issues = get_translated_for_display(issues_key, current_issues)
                else:
                    display_issues = current_issues
                
                new_issues = st.text_area(
                    f"{ICONS['info']} {get_text('Issues Noticed')}",
                    value=display_issues,
                    height=80,
                    key=f"issues_text_{day}"
                )
                
                # Update session state
                if new_issues != display_issues:
                    if st.session_state.ui_language == "zh" and openai_client and new_issues:
                        # Check if it looks like Chinese text
                        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
                        if chinese_pattern.search(new_issues):
                            # Translate back to English for storage
                            english_issues = translate_text(new_issues, "en")
                            st.session_state.form_data['issues'][day] = english_issues
                            store_original_text(issues_key, english_issues)
                        else:
                            st.session_state.form_data['issues'][day] = new_issues
                            store_original_text(issues_key, new_issues)
                    else:
                        st.session_state.form_data['issues'][day] = new_issues
                        if new_issues:
                            store_original_text(issues_key, new_issues)
    
    # Final Assessment
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["final"]}</span>
        {get_text("final_assessment")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        prepared_by = translated_text_input("prepared_by", "prepared_by", "Your name")
        # Date input
        prep_date = st.date_input(
            f"{ICONS['time']} {get_text('Date')}",
            value=st.session_state.form_data['prep_date'],
            key="prep_date_input"
        )
        st.session_state.form_data['prep_date'] = prep_date
    with col2:
        approved_by = translated_text_input("approved_by", "approved_by", "Approver name")
        overall_result = translated_text_input("overall_result", "overall_result", "Summary of test results...", type="textarea")

# Generate PDF Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(f"{ICONS['generate']} {get_text('generate_pdf')}", use_container_width=True):
        if not st.session_state.form_data['po_number'] or not st.session_state.form_data['brand']:
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
                    po_number = st.session_state.form_data['po_number']
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
