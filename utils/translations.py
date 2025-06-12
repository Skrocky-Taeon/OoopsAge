"""
Translation utilities for the Beauty Diary app.
Provides a simple localization system for English and Korean.
"""

class Translations:
    """Simple translation system for the Beauty Diary app"""
    
    # Main translations dictionary
    _translations = {
        # Layout translations
        "title": {
            "en": "Beauty Diary - Photo Analysis App",
            "ko": "Beauty Diary - 뷰티 분석 앱"
        },
        "history_btn": {
            "en": "History",
            "ko": "기록"
        },
        "privacy_policy": {
            "en": "Privacy Policy",
            "ko": "개인정보 처리방침"
        },
        "terms_of_service": {
            "en": "Terms of Service",
            "ko": "이용약관"
        },
        "footer_copyright": {
            "en": "© 2023 Beauty Diary - Photo Analysis App",
            "ko": "© 2023 Beauty Diary - 뷰티 분석 앱"
        },
        "loading_message": {
            "en": "Analyzing your skin...",
            "ko": "피부 분석 중..."
        },
        "loading_submessage": {
            "en": "This may take a few moments",
            "ko": "잠시만 기다려주세요"
        },
        
        # Index page translations
        "upload_title": {
            "en": "Upload Your Facial Image",
            "ko": "얼굴 이미지를 업로드하세요"
        },
        "drag_drop": {
            "en": "Drag & Drop Your Image Here",
            "ko": "여기에 이미지를 끌어다 놓으세요"
        },
        "or_click": {
            "en": "or click to browse",
            "ko": "또는 클릭하여 찾아보기"
        },
        "select_file": {
            "en": "Select File",
            "ko": "파일 선택"
        },
        "preview": {
            "en": "Preview",
            "ko": "미리보기"
        },
        "change_image": {
            "en": "Change Image",
            "ko": "이미지 변경"
        },
        "analyze_btn": {
            "en": "Analyze Skin Age",
            "ko": "피부 나이 분석하기"
        },
        "how_it_works": {
            "en": "How It Works",
            "ko": "작동 방식"
        },
        "step1_title": {
            "en": "1. Upload Photo",
            "ko": "1. 사진 업로드"
        },
        "step1_desc": {
            "en": "Upload a clear facial photo",
            "ko": "얼굴이 명확히 보이는 사진 업로드"
        },
        "step2_title": {
            "en": "2. AI Analysis",
            "ko": "2. AI 분석"
        },
        "step2_desc": {
            "en": "Our AI analyzes your skin features",
            "ko": "AI가 피부 특성을 분석"
        },
        "step3_title": {
            "en": "3. Get Results",
            "ko": "3. 결과 확인"
        },
        "step3_desc": {
            "en": "Review your personalized skin report",
            "ko": "맞춤형 피부 분석 보고서 확인"
        },
        "tips_title": {
            "en": "Tips for Better Results",
            "ko": "더 나은 결과를 위한 팁"
        },
        "tip1": {
            "en": "Use a well-lit, front-facing photo",
            "ko": "밝은 조명의 정면 사진 사용"
        },
        "tip2": {
            "en": "Ensure your face is clearly visible",
            "ko": "얼굴이 명확히 보이도록 하세요"
        },
        "tip3": {
            "en": "Remove glasses and avoid heavy makeup",
            "ko": "안경을 벗고 진한 화장은 피하세요"
        },
        "tip4": {
            "en": "Have a neutral expression (no smiling)",
            "ko": "무표정으로 촬영 (웃지 마세요)"
        },
        
        # History view translations
        "history_title": {
            "en": "Your Analysis History",
            "ko": "나의 분석 기록"
        },
        "new_analysis": {
            "en": "New Analysis",
            "ko": "새 분석"
        },
        "skin_age": {
            "en": "Skin Age",
            "ko": "피부 나이"
        },
        "view_btn": {
            "en": "View",
            "ko": "보기"
        },
        "no_history": {
            "en": "No Analysis History",
            "ko": "분석 기록 없음"
        },
        "no_history_desc": {
            "en": "You haven't uploaded any images for analysis yet.",
            "ko": "아직 분석을 위한 이미지를 업로드하지 않았습니다."
        },
        "start_new": {
            "en": "Start a New Analysis",
            "ko": "새 분석 시작하기"
        },
        
        # Results page translations
        "results_title": {
            "en": "Your Skin Analysis Results",
            "ko": "피부 분석 결과"
        },
        "estimated_skin_age": {
            "en": "Estimated Skin Age",
            "ko": "예상 피부 나이"
        },
        "features_analysis": {
            "en": "Skin Features Analysis",
            "ko": "피부 특성 분석"
        },
        "personalized_feedback": {
            "en": "Your Personalized Feedback",
            "ko": "맞춤형 피드백"
        },
        "general_tips": {
            "en": "General Skincare Tips",
            "ko": "일반 피부 관리 팁"
        },
        "sun_protection": {
            "en": "Sun Protection",
            "ko": "자외선 차단"
        },
        "sun_tip": {
            "en": "Always use SPF 30+ sunscreen daily, even on cloudy days, to prevent premature aging and dark spots.",
            "ko": "흐린 날에도 매일 SPF 30+ 자외선 차단제를 사용하여 조기 노화와 다크스팟을 예방하세요."
        },
        "hydration": {
            "en": "Hydration",
            "ko": "수분 공급"
        },
        "hydration_tip": {
            "en": "Keep your skin hydrated with moisturizers containing hyaluronic acid and drink plenty of water daily.",
            "ko": "히알루론산이 함유된 보습제로 피부에 수분을 공급하고 매일 충분한 물을 마시세요."
        },
        "sleep": {
            "en": "Sleep Well",
            "ko": "충분한 수면"
        },
        "sleep_tip": {
            "en": "Quality sleep helps skin cell regeneration. Aim for 7-8 hours of sleep to reduce dark circles and improve skin texture.",
            "ko": "양질의 수면은 피부 세포 재생에 도움이 됩니다. 다크서클을 줄이고 피부 결을 개선하기 위해 7-8시간의 수면을 취하세요."
        },
        "save_report": {
            "en": "Save Report",
            "ko": "보고서 저장"
        },
        "share_results": {
            "en": "Share Results",
            "ko": "결과 공유하기"
        },
        "results_saved": {
            "en": "Your results are stored securely. You can access them again by uploading the same photo.",
            "ko": "결과가 안전하게 저장되었습니다. 같은 사진을 업로드하면 다시 확인할 수 있습니다."
        },
        "compare_results": {
            "en": "Compare Results",
            "ko": "결과 비교하기"
        },
        
        # Feature names translations
        "feature_fine_lines": {
            "en": "fine lines",
            "ko": "잔주름"
        },
        "feature_wrinkles": {
            "en": "wrinkles",
            "ko": "주름"
        },
        "feature_dark_spots": {
            "en": "dark spots",
            "ko": "다크스팟"
        },
        "feature_pores": {
            "en": "pores",
            "ko": "모공"
        },
        "feature_dryness": {
            "en": "dryness",
            "ko": "건조함"
        },
        "feature_oiliness": {
            "en": "oiliness",
            "ko": "유분"
        },
        "feature_redness": {
            "en": "redness",
            "ko": "붉은기"
        },
        "feature_uneven_tone": {
            "en": "uneven tone",
            "ko": "불균일한 피부톤"
        },
        "feature_elasticity": {
            "en": "elasticity",
            "ko": "탄력"
        },
        
        # Flash messages translations
        "no_file": {
            "en": "No file part",
            "ko": "파일이 없습니다"
        },
        "no_selected_file": {
            "en": "No selected file",
            "ko": "선택된 파일이 없습니다"
        },
        "invalid_file": {
            "en": "Invalid file type. Please upload a JPG or PNG image.",
            "ko": "유효하지 않은 파일 형식입니다. JPG 또는 PNG 이미지를 업로드해주세요."
        },
        "no_permission": {
            "en": "You do not have permission to view this analysis",
            "ko": "이 분석을 볼 수 있는 권한이 없습니다"
        },
        
        # Login/Register translations
        "login": {
            "en": "Login",
            "ko": "로그인"
        },
        "register": {
            "en": "Register",
            "ko": "회원가입"
        },
        "email": {
            "en": "Email",
            "ko": "이메일"
        },
        "password": {
            "en": "Password",
            "ko": "비밀번호"
        },
        "confirm_password": {
            "en": "Confirm Password",
            "ko": "비밀번호 확인"
        },
        "logout": {
            "en": "Logout",
            "ko": "로그아웃"
        },
        
        # Product recommendation section
        "product_recommendations": {
            "en": "Product Recommendations",
            "ko": "제품 추천"
        },
        "based_on_analysis": {
            "en": "Based on your skin analysis, these products may help improve your skin condition",
            "ko": "피부 분석을 기반으로, 이러한 제품들이 피부 상태 개선에 도움이 될 수 있습니다"
        },
    }
    
    # Feature names mapping for translation
    _feature_names = {
        "fine_lines": "feature_fine_lines",
        "wrinkles": "feature_wrinkles",
        "dark_spots": "feature_dark_spots",
        "pores": "feature_pores",
        "dryness": "feature_dryness",
        "oiliness": "feature_oiliness",
        "redness": "feature_redness",
        "uneven_tone": "feature_uneven_tone",
        "elasticity": "feature_elasticity",
    }
    
    @classmethod
    def get(cls, key, lang="en"):
        """Get a translation for a key in the specified language"""
        if key in cls._translations:
            return cls._translations[key].get(lang, cls._translations[key]["en"])
        return key
    
    @classmethod
    def get_feature_name(cls, feature_name, lang="en"):
        """Get a translation for a feature name in the specified language"""
        key = cls._feature_names.get(feature_name, feature_name)
        return cls.get(key, lang)