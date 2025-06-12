import random
import imagehash
from PIL import Image
from config import Config

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def generate_image_hash(image):
    """Generate a perceptual hash for an image."""
    return imagehash.average_hash(image)

# 피부 특성 분석 기준표 및 피드백 매핑
SKIN_FEATURE_RANGES = {
    "wrinkles": {
        "low": (0.0, 0.3),
        "medium": (0.3, 0.6),
        "high": (0.6, 1.0),
    },
    "pigmentation": {
        "low": (0.0, 0.2),
        "medium": (0.2, 0.5),
        "high": (0.5, 1.0),
    },
    "elasticity": {
        "low": (0.0, 0.4),
        "medium": (0.4, 0.7),
        "high": (0.7, 1.0),
    },
    "moisture": {
        "low": (0.0, 0.3),
        "medium": (0.3, 0.6),
        "high": (0.6, 1.0),
    },
    "fine_lines": {
        "low": (0.0, 0.3),
        "medium": (0.3, 0.6),
        "high": (0.6, 1.0),
    },
    "dark_spots": {
        "low": (0.0, 0.3),
        "medium": (0.3, 0.6),
        "high": (0.6, 1.0),
    },
    "pores": {
        "low": (0.0, 0.3),
        "medium": (0.3, 0.6),
        "high": (0.6, 1.0),
    },
    "dryness": {
        "low": (0.0, 0.3),
        "medium": (0.3, 0.6),
        "high": (0.6, 1.0),
    },
    "oiliness": {
        "low": (0.0, 0.3),
        "medium": (0.3, 0.6),
        "high": (0.6, 1.0),
    },
}

# 사용자에게 제공할 피드백 메시지 (한국어)
SKIN_FEEDBACK_MESSAGES_KO = {
    "wrinkles": {
        "low": "주름이 거의 보이지 않아 동안 인상을 줍니다.",
        "medium": "주름이 조금씩 보이기 시작했습니다. 눈가나 미간 관리가 필요합니다.",
        "high": "주름이 뚜렷해지고 있습니다. 보습과 탄력 관리가 중요합니다.",
    },
    "pigmentation": {
        "low": "피부 톤이 고르고 잡티가 거의 없습니다.",
        "medium": "피부에 약간의 색소침착이 보입니다. 자외선 차단에 신경 써주세요.",
        "high": "잡티와 색소침착이 많이 나타나고 있습니다. 미백과 진정 케어가 필요합니다.",
    },
    "elasticity": {
        "low": "피부 탄력이 많이 떨어진 상태입니다. 콜라겐과 마사지 케어를 추천드립니다.",
        "medium": "탄력이 약간 부족한 상태입니다. 꾸준한 관리로 개선될 수 있습니다.",
        "high": "피부가 탱탱하고 탄력이 좋은 상태입니다.",
    },
    "moisture": {
        "low": "피부가 건조한 상태입니다. 수분 공급이 시급합니다.",
        "medium": "수분이 어느 정도 유지되고 있으나 더 신경 써야 합니다.",
        "high": "피부가 충분히 촉촉하고 건강한 상태입니다.",
    },
    "fine_lines": {
        "low": "미세 주름이 거의 없는 상태입니다.",
        "medium": "미세 주름이 생기기 시작했습니다. 꾸준한 관리가 필요합니다.",
        "high": "미세 주름이 많이 보입니다. 레티놀 제품과 집중 관리가 필요합니다.",
    },
    "dark_spots": {
        "low": "기미와 잡티가 거의 보이지 않습니다.",
        "medium": "약간의 기미와 잡티가 있습니다. 비타민C 제품 사용을 권장합니다.",
        "high": "기미와 잡티가 많이 있습니다. 미백 관리와 자외선 차단이 매우 중요합니다.",
    },
    "pores": {
        "low": "모공이 작고 잘 관리되고 있습니다.",
        "medium": "모공이 약간 넓어져 있습니다. 수분 공급과 함께 모공 관리가 필요합니다.",
        "high": "모공이 많이 확장되어 있습니다. 꾸준한 클렌징과 모공 케어가 필요합니다.",
    },
    "dryness": {
        "low": "건조함이 거의 느껴지지 않는 좋은 상태입니다.",
        "medium": "약간의 건조함이 있습니다. 수분 공급을 늘려주세요.",
        "high": "심한 건조함이 있습니다. 집중적인 보습 관리가 필요합니다.",
    },
    "oiliness": {
        "low": "지성이 거의 없는 균형잡힌 피부입니다.",
        "medium": "T존 부위에 약간의 유분기가 있습니다. 균형있는 관리가 필요합니다.",
        "high": "피부가 많이 번들거립니다. 유분 조절과 함께 충분한 수분 공급이 필요합니다.",
    },
}

# 사용자에게 제공할 피드백 메시지 (영어)
SKIN_FEEDBACK_MESSAGES_EN = {
    "wrinkles": {
        "low": "Your skin shows minimal wrinkles, giving you a youthful appearance.",
        "medium": "Some wrinkles are starting to appear. Focus on eye and brow area care.",
        "high": "Wrinkles are becoming more prominent. Moisture and elasticity management are important.",
    },
    "pigmentation": {
        "low": "Your skin tone is even with very few blemishes.",
        "medium": "There's some pigmentation visible. Pay attention to sun protection.",
        "high": "Significant pigmentation and dark spots are present. Brightening and soothing care is needed.",
    },
    "elasticity": {
        "low": "Your skin elasticity is reduced. Collagen products and massage care are recommended.",
        "medium": "Elasticity is slightly lacking. Consistent care can improve this.",
        "high": "Your skin is firm with good elasticity.",
    },
    "moisture": {
        "low": "Your skin is dry. Immediate hydration is needed.",
        "medium": "Moisture is somewhat maintained but needs more attention.",
        "high": "Your skin is sufficiently hydrated and healthy.",
    },
    "fine_lines": {
        "low": "Almost no fine lines are visible.",
        "medium": "Fine lines are beginning to form. Regular care is needed.",
        "high": "Fine lines are quite visible. Retinol products and intensive care are recommended.",
    },
    "dark_spots": {
        "low": "Almost no dark spots or blemishes are visible.",
        "medium": "Some dark spots are present. Consider using vitamin C products.",
        "high": "Significant dark spots are present. Brightening treatments and sun protection are crucial.",
    },
    "pores": {
        "low": "Your pores are small and well-maintained.",
        "medium": "Pores are slightly enlarged. Hydration along with pore care is needed.",
        "high": "Pores are significantly enlarged. Consistent cleansing and pore care are necessary.",
    },
    "dryness": {
        "low": "There's minimal dryness, which is a good sign.",
        "medium": "Slight dryness is present. Increase hydration.",
        "high": "Severe dryness is present. Intensive moisturizing care is needed.",
    },
    "oiliness": {
        "low": "Your skin has balanced oil production.",
        "medium": "There's some oiliness in the T-zone. Balanced care is needed.",
        "high": "Your skin is quite oily. Oil control along with sufficient hydration is needed.",
    },
}

def generate_feedback(skin_age, features, lang="en"):
    """Generate personalized feedback based on skin age and features in the specified language."""
    # 기본 인사말
    intro = ""
    if lang == "ko":
        intro = f"당신의 피부 나이는 약 {int(skin_age)}세로 추정됩니다.\n\n"
    else:  # Default to English
        intro = f"Your skin's estimated age is {int(skin_age)} years.\n\n"
    
    feedback = intro
    
    # 언어에 따라 적절한 피드백 메시지 선택
    feedback_messages = SKIN_FEEDBACK_MESSAGES_EN
    if lang == "ko":
        feedback_messages = SKIN_FEEDBACK_MESSAGES_KO
        
    # 피드백 생성
    for feature, value in features.items():
        if feature in SKIN_FEATURE_RANGES:
            for level, (low, high) in SKIN_FEATURE_RANGES[feature].items():
                if low <= value < high and feature in feedback_messages:
                    feedback += f"• {feedback_messages[feature][level]}\n"
                    break
    
    # 추천사항 생성 (언어별로 추천사항 추가)
    recommends = []
    
    # 각 피부 특성에 맞는 추천 항목 생성
    for feature, value in features.items():
        if feature in SKIN_FEATURE_RANGES:
            for level, (low, high) in SKIN_FEATURE_RANGES[feature].items():
                if low <= value < high:
                    # 한국어 추천사항
                    if lang == "ko":
                        if level == "high" and feature in ["wrinkles", "fine_lines"]:
                            recommends.append("• 레티놀과 펩타이드가 함유된 제품으로 주름 개선을 시도해보세요.")
                        elif level == "high" and feature in ["dark_spots", "pigmentation"]:
                            recommends.append("• 비타민C 세럼과 자외선 차단제를 매일 사용하세요.")
                        elif level == "high" and feature == "dryness":
                            recommends.append("• 히알루론산이 함유된 수분 세럼을 사용하세요.")
                        elif level == "high" and feature == "oiliness":
                            recommends.append("• 나이아신아마이드가 함유된 부드러운 클렌저로 유분 조절을 해보세요.")
                        elif level == "low" and feature == "elasticity":
                            recommends.append("• 콜라겐 생성을 돕는 제품과 함께 꾸준한 마사지를 권장합니다.")
                        elif level == "high" and feature == "pores":
                            recommends.append("• BHA(살리실산)를 활용하여 모공 관리를 해보세요.")
                    # 영어 추천사항 
                    else:
                        if level == "high" and feature in ["wrinkles", "fine_lines"]:
                            recommends.append("• Consider products with retinol and peptides to reduce lines and wrinkles.")
                        elif level == "high" and feature in ["dark_spots", "pigmentation"]:
                            recommends.append("• Use vitamin C serums and sunscreen daily to fade dark spots.")
                        elif level == "high" and feature == "dryness":
                            recommends.append("• Add a hydrating serum with hyaluronic acid to your routine.")
                        elif level == "high" and feature == "oiliness":
                            recommends.append("• Try a gentle cleanser with niacinamide to balance oil production.")
                        elif level == "low" and feature == "elasticity":
                            recommends.append("• Use collagen-boosting products and perform facial massage regularly.")
                        elif level == "high" and feature == "pores":
                            recommends.append("• Incorporate BHA (like salicylic acid) to minimize pore appearance.")
    
    # 추천 사항이 있을 경우에만 추가
    if recommends:
        if lang == "ko":
            feedback += "\n추천 관리법:\n"
        else:
            feedback += "\nRecommendations:\n"
        
        # 중복 제거
        unique_recommends = list(set(recommends))
        feedback += "\n".join(unique_recommends)
    
    return feedback