"""
PDF 보고서 생성 모듈
"""

import os
from io import BytesIO
import logging
from datetime import datetime
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

# 기본 폰트 사용 (한글 폰트 대신)
KOREAN_FONT = 'Helvetica'

def create_skin_analysis_pdf(analysis, lang='en'):
    """
    피부 분석 결과를 PDF로 생성합니다. 모든 내용을 1페이지에 맞춰 출력합니다.
    
    Args:
        analysis: 피부 분석 결과 객체
        lang: 언어 설정 (en 또는 ko)
        
    Returns:
        BytesIO: PDF 파일 데이터
    """
    buffer = BytesIO()
    
    # PDF 스타일과 설정 - 폰트 크기 조정으로 1페이지에 맞춤
    styles = getSampleStyleSheet()
    if lang == 'ko':
        title_style = ParagraphStyle(
            'KoreanTitle',
            parent=styles['Title'],
            fontName=KOREAN_FONT,
            fontSize=18,  # 폰트 크기 축소
            leading=22    # 줄 간격 축소
        )
        normal_style = ParagraphStyle(
            'KoreanNormal',
            parent=styles['Normal'],
            fontName=KOREAN_FONT,
            fontSize=10,  # 폰트 크기 축소
            leading=12    # 줄 간격 축소
        )
        heading_style = ParagraphStyle(
            'KoreanHeading',
            parent=styles['Heading2'],
            fontName=KOREAN_FONT,
            fontSize=12,  # 폰트 크기 축소
            leading=16    # 줄 간격 축소
        )
    else:
        title_style = ParagraphStyle(
            'EnTitle',
            parent=styles['Title'],
            fontSize=18,  # 폰트 크기 축소
            leading=22    # 줄 간격 축소
        )
        normal_style = ParagraphStyle(
            'EnNormal',
            parent=styles['Normal'],
            fontSize=10,  # 폰트 크기 축소
            leading=12    # 줄 간격 축소
        )
        heading_style = ParagraphStyle(
            'EnHeading',
            parent=styles['Heading2'],
            fontSize=12,  # 폰트 크기 축소
            leading=16    # 줄 간격 축소
        )
    
    # PDF 문서 생성 - 마진 축소로 공간 확보
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=15*mm,     # 마진 축소
        leftMargin=15*mm,    # 마진 축소
        rightMargin=15*mm,   # 마진 축소
        bottomMargin=15*mm   # 마진 축소
    )
    
    # PDF에 포함될 요소들
    elements = []
    
    # 로고 및 헤더
    # elements.append(ReportLabImage('static/images/logo.png', width=2*inch, height=1*inch))
    # elements.append(Spacer(1, 12))
    
    # 보고서 제목
    title = "Ooops Age Analysis Report" if lang == 'en' else "Ooops Age 피부 분석 보고서"
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))
    
    # 날짜
    date_str = datetime.now().strftime('%Y-%m-%d')
    date_text = f"Report Date: {date_str}" if lang == 'en' else f"보고서 생성일: {date_str}"
    elements.append(Paragraph(date_text, normal_style))
    elements.append(Spacer(1, 10))
    
    # 분석 이미지 - 크기 축소
    try:
        # 이미지 경로에서 이미지 로드 (크기 축소)
        if analysis.image_path and os.path.exists(analysis.image_path):
            img = ReportLabImage(analysis.image_path, width=2.5*inch, height=2*inch)
            elements.append(img)
        else:
            # 이미지 URL이 있지만 로컬 파일이 없는 경우 URL 표시
            image_note = "Image available online" if lang == 'en' else "이미지는 온라인에서 확인 가능합니다"
            elements.append(Paragraph(image_note, normal_style))
    except Exception as e:
        logger.error(f"Error loading image for PDF: {str(e)}")
        image_error = "Could not load image" if lang == 'en' else "이미지를 불러올 수 없습니다"
        elements.append(Paragraph(image_error, normal_style))
    
    elements.append(Spacer(1, 8))
    
    # 분석 결과 섹션
    results_title = "Analysis Results" if lang == 'en' else "분석 결과"
    elements.append(Paragraph(results_title, heading_style))
    elements.append(Spacer(1, 10))
    
    # 피부 나이
    skin_age_text = f"Estimated Skin Age: {analysis.skin_age:.1f}" if lang == 'en' else f"추정 피부 나이: {analysis.skin_age:.1f}"
    elements.append(Paragraph(skin_age_text, normal_style))
    elements.append(Spacer(1, 5))
    
    # 실제 나이와 비교 (있는 경우)
    if analysis.actual_age:
        age_diff = analysis.skin_age - analysis.actual_age
        if lang == 'en':
            if age_diff > 0:
                age_comparison = f"Your skin appears {age_diff:.1f} years older than your chronological age."
            elif age_diff < 0:
                age_comparison = f"Your skin appears {abs(age_diff):.1f} years younger than your chronological age."
            else:
                age_comparison = "Your skin age matches your chronological age."
        else:
            if age_diff > 0:
                age_comparison = f"피부 나이가 실제 나이보다 {age_diff:.1f}세 더 많아 보입니다."
            elif age_diff < 0:
                age_comparison = f"피부 나이가 실제 나이보다 {abs(age_diff):.1f}세 더 젊어 보입니다."
            else:
                age_comparison = "피부 나이가 실제 나이와 일치합니다."
        
        elements.append(Paragraph(age_comparison, normal_style))
        elements.append(Spacer(1, 5))
    
    # 피부 특성 섹션
    features_title = "Skin Features Analysis" if lang == 'en' else "피부 특성 분석"
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(features_title, heading_style))
    elements.append(Spacer(1, 10))
    
    # 특성 이름 한글화
    feature_names = {
        'wrinkles': '주름' if lang == 'ko' else 'Wrinkles',
        'pigmentation': '색소침착' if lang == 'ko' else 'Pigmentation',
        'elasticity': '탄력' if lang == 'ko' else 'Elasticity',
        'moisture': '수분' if lang == 'ko' else 'Moisture',
        'fine_lines': '잔주름' if lang == 'ko' else 'Fine Lines',
        'dark_spots': '다크스팟' if lang == 'ko' else 'Dark Spots',
        'pores': '모공' if lang == 'ko' else 'Pores',
        'dryness': '건조함' if lang == 'ko' else 'Dryness',
        'oiliness': '유분' if lang == 'ko' else 'Oiliness'
    }
    
    # 특성 테이블 생성 - 2열로 재구성하여 공간 절약
    # 특성을 2개 열로 나누기 위한 준비
    total_features = len(analysis.features)
    first_half = list(analysis.features.items())[:total_features//2 + total_features%2]
    second_half = list(analysis.features.items())[total_features//2 + total_features%2:]
    
    # 테이블 데이터 생성
    features_data = []
    
    # 테이블 헤더
    feature_header = "Feature" if lang == 'en' else "특성"
    score_header = "Score" if lang == 'en' else "점수"
    features_data.append([feature_header, score_header, feature_header, score_header])
    
    # 두 열에 특성 값 배치
    for i in range(max(len(first_half), len(second_half))):
        row = []
        # 첫 번째 열에 특성 추가
        if i < len(first_half):
            feature_name, feature_value = first_half[i]
            display_name = feature_names.get(feature_name, feature_name)
            score = f"{int(feature_value * 100)}%"
            row.extend([display_name, score])
        else:
            row.extend(["", ""])
        
        # 두 번째 열에 특성 추가
        if i < len(second_half):
            feature_name, feature_value = second_half[i]
            display_name = feature_names.get(feature_name, feature_name)
            score = f"{int(feature_value * 100)}%"
            row.extend([display_name, score])
        else:
            row.extend(["", ""])
            
        features_data.append(row)
    
    # 테이블 스타일 - 컬럼 4개로 조정
    feature_table = Table(features_data, colWidths=[doc.width/4.0, doc.width/4.0, doc.width/4.0, doc.width/4.0])
    feature_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (3, 0), KOREAN_FONT if lang == 'ko' else 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (3, 0), 10),  # 폰트 사이즈 축소
        ('BOTTOMPADDING', (0, 0), (3, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), KOREAN_FONT if lang == 'ko' else 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),  # 폰트 사이즈 축소
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),  # 패딩 축소
        ('TOPPADDING', (0, 1), (-1, -1), 4),     # 패딩 축소
    ]))
    
    elements.append(feature_table)
    elements.append(Spacer(1, 5))  # 간격 축소
    
    # 피드백 섹션
    feedback_title = "Personalized Feedback" if lang == 'en' else "맞춤형 피드백"
    elements.append(Paragraph(feedback_title, heading_style))
    elements.append(Spacer(1, 10))
    
    # 언어에 맞는 피드백 추출
    feedback_text = analysis.feedback
    if '\n\n' in feedback_text:
        # 영어와 한국어 피드백이 구분되어 있는 경우
        feedback_parts = feedback_text.split('\n\n')
        if lang == 'ko' and len(feedback_parts) > 1:
            feedback_text = feedback_parts[1]
        elif lang == 'en':
            feedback_text = feedback_parts[0]
    
    # 피드백 텍스트 추가
    for paragraph in feedback_text.split('\n'):
        if paragraph.strip():
            elements.append(Paragraph(paragraph, normal_style))
            elements.append(Spacer(1, 5))
    
    # 개선 팁 섹션
    tips_title = "Improvement Tips" if lang == 'en' else "개선 팁"
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(tips_title, heading_style))
    elements.append(Spacer(1, 10))
    
    # 피부 특성에 따른 맞춤형 팁 생성
    tips = []
    features = analysis.features
    
    if features.get('wrinkles', 0) > 0.5 or features.get('fine_lines', 0) > 0.5:
        if lang == 'en':
            tips.append("Use retinol products to reduce wrinkles and fine lines")
            tips.append("Apply vitamin C serum in the morning to boost collagen production")
        else:
            tips.append("주름과 잔주름 개선을 위해 레티놀 제품을 사용하세요")
            tips.append("아침에 비타민 C 세럼을 바르면 콜라겐 생성을 촉진합니다")
    
    if features.get('pigmentation', 0) > 0.5 or features.get('dark_spots', 0) > 0.5:
        if lang == 'en':
            tips.append("Use products with brightening ingredients like niacinamide")
            tips.append("Apply sunscreen diligently to prevent further pigmentation")
        else:
            tips.append("나이아신아마이드와 같은 미백 성분이 함유된 제품을 사용하세요")
            tips.append("추가적인 색소침착을 방지하기 위해 자외선 차단제를 꼼꼼히 바르세요")
    
    if features.get('elasticity', 0) < 0.5:
        if lang == 'en':
            tips.append("Use products with peptides to boost skin elasticity")
            tips.append("Consider facial massage to improve circulation and firmness")
        else:
            tips.append("피부 탄력을 높이기 위해 펩타이드가 함유된 제품을 사용하세요")
            tips.append("혈액순환과 탄력 개선을 위해 페이셜 마사지를 고려해보세요")
    
    if features.get('moisture', 0) < 0.5 or features.get('dryness', 0) > 0.5:
        if lang == 'en':
            tips.append("Use hyaluronic acid serums for deep hydration")
            tips.append("Consider using a humidifier in your bedroom")
        else:
            tips.append("깊은 보습을 위해 히알루론산 세럼을 사용하세요")
            tips.append("침실에 가습기를 사용하는 것을 고려해보세요")
    
    # 일반적인 팁 추가
    if lang == 'en':
        tips.append("Maintain a consistent skincare routine for best results")
        tips.append("Drink plenty of water and eat a balanced diet")
    else:
        tips.append("최상의 결과를 위해 일관된 스킨케어 루틴을 유지하세요")
        tips.append("물을 충분히 마시고 균형 잡힌 식단을 섭취하세요")
    
    # 팁 리스트 추가
    for tip in tips:
        bullet_text = f"• {tip}"
        elements.append(Paragraph(bullet_text, normal_style))
        elements.append(Spacer(1, 5))
    
    # PDF 생성
    doc.build(elements)
    buffer.seek(0)
    return buffer