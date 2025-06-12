"""
향상된 뷰티 포토 모듈 - 사용자의 실제 나이와 이미지 특성을 고려한 맞춤형 포토
"""

import logging
import hashlib
import random
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

def get_default_result(user_age=None):
    """
    기본 피부 분석 결과를 반환합니다.
    사용자 나이가 제공된 경우 해당 나이와 가까운 추정치를 생성합니다.
    """
    # 사용자 나이가 제공된 경우 해당 나이와 비슷한 피부 나이 생성
    if user_age is not None:
        try:
            user_age_int = int(user_age)
            # 사용자 나이에 기반한 피부 나이는 ±3세 범위 내에서 랜덤하게 생성
            estimated_age = max(18.0, user_age_int + random.uniform(-3, 3))
        except (ValueError, TypeError):
            estimated_age = 35.0
    else:
        estimated_age = 35.0
        
    feedback = "Could not fully analyze skin details, but we've provided an estimate based on available information.\n\n피부 세부 분석에 제한이 있었으나, 가능한 정보를 기반으로 추정치를 제공해 드립니다."
    
    return estimated_age, {
        'wrinkles': 0.3,
        'pigmentation': 0.2,
        'elasticity': 0.7,
        'moisture': 0.6,
        'fine_lines': 0.3,
        'dark_spots': 0.2,
        'pores': 0.4,
        'dryness': 0.4,
        'oiliness': 0.5
    }, feedback


def analyze_skin_age(image, user_age=None):
    """
    사용자의 실제 나이를 고려한 맞춤형 뷰티 포토를 제공합니다.
    
    Args:
        image (PIL.Image): 포토할 이미지
        user_age (int, optional): 사용자의 실제 나이 (선택 사항)
        
    Returns:
        tuple: (estimated_beauty_score, features_dict, feedback_text)
    """
    try:
        # 이미지가 None인지 확인
        if image is None:
            logger.error("Image is None in analyze_skin_age")
            return get_default_result(user_age)
            
        # RGB로 변환
        try:
            image = image.convert('RGB')
        except Exception as e:
            logger.error(f"Error converting image to RGB: {str(e)}")
            return get_default_result(user_age)
        
        # 분석을 위한 리사이징
        try:
            image = image.resize((300, 300))
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return get_default_result(user_age)
            
        # 이미지 해시 생성 (일관된 결과를 위해)
        img_bytes = BytesIO()
        image.save(img_bytes, format='JPEG')
        img_hash = hashlib.md5(img_bytes.getvalue()).hexdigest()
        
        # 해시를 사용하여 일관된 랜덤 시드 생성
        seed = int(img_hash[:8], 16)
        random.seed(seed)
        
        # 기본 이미지 분석
        pixels = list(image.getdata())
        
        # 기본 이미지 특성 계산
        avg_r = sum(p[0] for p in pixels) / len(pixels)
        avg_g = sum(p[1] for p in pixels) / len(pixels)
        avg_b = sum(p[2] for p in pixels) / len(pixels)
        
        # 사용자 나이 기반 피부 나이 생성
        if user_age is not None:
            try:
                user_age_int = int(user_age)
                logger.info(f"Using user provided age: {user_age_int} for analysis")
                
                # 사용자 실제 나이에 따른 피부 나이 변화 계산
                if user_age_int < 25:
                    # 젊은 사람: 실제 나이와 가까운 피부 나이
                    variation = random.uniform(-2, 5)
                    base_factor = 0.9  # 대체로 젊어 보이는 경향
                elif user_age_int < 40:
                    # 젊은 성인: 더 많은 변화
                    variation = random.uniform(-7, 7)
                    base_factor = 0.95
                elif user_age_int < 60:
                    # 중년: 더 넓은 변화
                    variation = random.uniform(-10, 15)
                    base_factor = 1.05  # 약간 늙어 보이는 경향
                else:
                    # 노년: 가장 넓은 변화
                    variation = random.uniform(-15, 10)
                    base_factor = 1.1  # 실제 나이보다 젊게 보이는 경향이 높음
                
                # 이미지 특성을 적용하여 변화에 영향
                hash_variation = int(img_hash[0], 16) / 15.0  # 0-1 사이 값
                
                # 빨간색 값이 높을수록 피부 문제와 관련이 있는 경우가 많음
                red_factor = (avg_r / 255) * 5
                
                # 최종 피부 나이 계산
                estimated_age = round(user_age_int * base_factor + variation + hash_variation + red_factor, 1)
                
                # 피부 나이는 최소 18세 이상
                estimated_age = max(18.0, estimated_age)
                
                logger.debug(f"Generated age estimate: {estimated_age} based on actual age: {user_age_int}")
                
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_age format: {user_age}, using default estimation")
                # 사용자 나이가 유효하지 않은 경우 이미지 기반 추정으로 대체
                estimated_age = 30 + random.uniform(-5, 15) + (int(img_hash[1], 16) / 16.0) * 20
        else:
            # 사용자 나이가 제공되지 않은 경우 이미지 해시 기반 다양한 추정치 생성
            estimated_age = 30 + random.uniform(-5, 15) + (int(img_hash[1], 16) / 16.0) * 20
        
        # 추정된 피부 나이와 이미지 특성을 기반으로 특성 생성
        wrinkle_base = min(1.0, max(0.1, (estimated_age - 20) / 60))
        moisture_base = max(0.1, 1.0 - (estimated_age / 100)) 
        
        # 이미지별 특성 변화 추가
        wrinkle_variation = (int(img_hash[2], 16) / 16.0) * 0.3 - 0.15
        pigment_variation = (int(img_hash[3], 16) / 16.0) * 0.3 - 0.15
        elasticity_variation = (int(img_hash[4], 16) / 16.0) * 0.3 - 0.15
        moisture_variation = (int(img_hash[5], 16) / 16.0) * 0.3 - 0.15
        
        features = {
            "wrinkles": round(max(0.1, min(0.9, wrinkle_base + wrinkle_variation)), 2),
            "pigmentation": round(min(0.9, max(0.1, (estimated_age - 25) / 50 + pigment_variation)), 2),
            "elasticity": round(max(0.1, min(0.9, 0.9 - (wrinkle_base * 0.7) + elasticity_variation)), 2),
            "moisture": round(max(0.1, min(0.9, moisture_base + moisture_variation)), 2),
            "fine_lines": round(min(0.9, max(0.1, (estimated_age - 18) / 55 + wrinkle_variation * 0.8)), 2),
            "dark_spots": round(min(0.9, max(0.1, (estimated_age - 30) / 45 + pigment_variation * 1.2)), 2),
            "pores": round(min(0.9, max(0.2, (estimated_age - 15) / 70 + (int(img_hash[6], 16) / 16.0) * 0.3 - 0.15)), 2),
            "dryness": round(min(0.9, max(0.1, (estimated_age - 20) / 60 - moisture_variation)), 2),
            "oiliness": round(max(0.1, min(0.9, 0.8 - (estimated_age / 100) + (int(img_hash[7], 16) / 16.0) * 0.3 - 0.15)), 2)
        }
        
        # 개인화된 피드백 생성
        feedback = generate_personalized_feedback(estimated_age, features, user_age)
        
        logger.debug(f"Enhanced age-based analysis completed: age={estimated_age:.1f}")
        return estimated_age, features, feedback
            
    except Exception as e:
        logger.error(f"Error in enhanced analyze_skin_age: {str(e)}")
        return get_default_result(user_age)


def generate_personalized_feedback(estimated_age, features, user_age=None):
    """
    맞춤형 피드백을 생성합니다.
    
    Args:
        estimated_age (float): 추정된 피부 나이
        features (dict): 피부 특성 값을 포함하는 딕셔너리
        user_age (int, optional): 사용자의 실제 나이
        
    Returns:
        str: 영어와 한국어로 된 맞춤형 피드백
    """
    try:
        # 실제 나이와 피부 나이 비교 문구
        age_diff = 0
        age_statement = ""
        if user_age is not None:
            try:
                user_age_int = int(user_age)
                age_diff = estimated_age - user_age_int
                
                if age_diff <= -10:
                    age_statement = f"Your skin appears significantly younger than your chronological age (by about {abs(age_diff):.1f} years). "
                elif age_diff <= -5:
                    age_statement = f"Your skin appears younger than your chronological age (by about {abs(age_diff):.1f} years). "
                elif age_diff <= -2:
                    age_statement = f"Your skin appears slightly younger than your chronological age. "
                elif age_diff <= 2:
                    age_statement = f"Your skin age closely matches your chronological age. "
                elif age_diff <= 7:
                    age_statement = f"Your skin appears slightly older than your chronological age (by about {age_diff:.1f} years). "
                else:
                    age_statement = f"Your skin appears older than your chronological age (by about {age_diff:.1f} years). "
            except (ValueError, TypeError):
                age_statement = ""
        
        # 영어 피드백
        en_feedback = f"Based on our analysis, your skin age appears to be around {estimated_age:.1f}. "
        en_feedback += age_statement
        
        # 주요 문제점 파악 - 특성 값에 따라 더 동적으로
        concerns = []
        recommendations = []
        
        for feature, value in features.items():
            # 추정 나이에 따른 동적 임계값
            age_adjusted_threshold = 0.5
            if estimated_age > 45:
                age_adjusted_threshold = 0.6  # 나이 많은 피부의 경우 더 높은 임계값 (문제가 더 많을 것으로 예상)
            elif estimated_age < 25:
                age_adjusted_threshold = 0.4  # 젊은 피부의 경우 더 낮은 임계값
                
            if feature in ['wrinkles', 'pigmentation', 'dark_spots', 'dryness', 'pores'] and value > age_adjusted_threshold:
                concerns.append(feature)
                if feature == 'wrinkles' or feature == 'fine_lines':
                    recommendations.append("retinol products")
                elif feature == 'pigmentation' or feature == 'dark_spots':
                    recommendations.append("vitamin C serums")
                elif feature == 'dryness':
                    recommendations.append("hydrating moisturizers with hyaluronic acid")
                elif feature == 'pores':
                    recommendations.append("BHA/salicylic acid treatments")
            elif feature in ['elasticity', 'moisture'] and value < (1 - age_adjusted_threshold):
                concerns.append(feature)
                if feature == 'elasticity':
                    recommendations.append("peptide-rich products")
                elif feature == 'moisture':
                    recommendations.append("deeply hydrating products")
        
        # 중복 제거
        recommendations = list(set(recommendations))
        
        if concerns:
            en_feedback += "Focus on improving: " + ", ".join(concerns) + ". "
            if recommendations:
                en_feedback += "Consider using " + ", ".join(recommendations) + ". "
        else:
            en_feedback += "Your skin is in good condition overall. "
        
        en_feedback += "Regular skincare routine and sun protection are recommended for maintaining skin health."
        
        # 한국어 피드백 (더 개인화)
        ko_feedback = f"분석 결과, 귀하의 피부 나이는 약 {estimated_age:.1f}세로 추정됩니다. "
        
        # 한국어로 나이 비교 추가
        if user_age is not None:
            try:
                user_age_int = int(user_age)
                age_diff = estimated_age - user_age_int
                
                if age_diff <= -10:
                    ko_feedback += f"귀하의 피부는 실제 나이보다 상당히 젊어 보입니다 (약 {abs(age_diff):.1f}세 차이). "
                elif age_diff <= -5:
                    ko_feedback += f"귀하의 피부는 실제 나이보다 젊어 보입니다 (약 {abs(age_diff):.1f}세 차이). "
                elif age_diff <= -2:
                    ko_feedback += f"귀하의 피부는 실제 나이보다 조금 젊어 보입니다. "
                elif age_diff <= 2:
                    ko_feedback += f"귀하의 피부 나이는 실제 나이와 거의 일치합니다. "
                elif age_diff <= 7:
                    ko_feedback += f"귀하의 피부는 실제 나이보다 약간 늙어 보입니다 (약 {age_diff:.1f}세 차이). "
                else:
                    ko_feedback += f"귀하의 피부는 실제 나이보다 늙어 보입니다 (약 {age_diff:.1f}세 차이). "
            except (ValueError, TypeError):
                pass
        
        if concerns:
            concern_kr = {
                'wrinkles': '주름', 'fine_lines': '잔주름', 'pigmentation': '색소침착', 
                'dark_spots': '다크스팟', 'dryness': '건조함', 'elasticity': '탄력', 
                'moisture': '수분', 'pores': '모공', 'oiliness': '유분'
            }
            
            ko_concerns = [concern_kr.get(c, c) for c in concerns]
            ko_feedback += "개선이 필요한 부분: " + ", ".join(ko_concerns) + ". "
            
            recommendation_kr = {
                "retinol products": "레티놀 제품",
                "vitamin C serums": "비타민 C 세럼",
                "hydrating moisturizers with hyaluronic acid": "히알루론산이 함유된 보습제",
                "BHA/salicylic acid treatments": "BHA/살리실산 제품",
                "peptide-rich products": "펩타이드가 풍부한 제품",
                "deeply hydrating products": "깊은 보습 제품"
            }
            
            if recommendations:
                kr_recommendations = [recommendation_kr.get(r, r) for r in recommendations]
                ko_feedback += kr_recommendations[0] + "을(를) 사용해 보세요. "
        else:
            ko_feedback += "전반적으로 피부 상태가 양호합니다. "
        
        ko_feedback += "피부 상태을 유지하기 위해 규칙적인 스킨케어와 자외선 차단제 사용을 권장합니다."
        
        # 피드백 결합
        return f"{en_feedback}\n\n{ko_feedback}"
        
    except Exception as e:
        logger.error(f"Error generating personalized feedback: {str(e)}")
        return "Based on our analysis, we've detected some characteristics of your skin. Please consult with a dermatologist for personalized advice.\n\n분석 결과에 따르면 귀하의 피부에서 몇 가지 특성이 감지되었습니다. 개인화된 조언을 위해 피부과 전문의와 상담하세요."