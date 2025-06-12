"""
GPT-4 Vision을 활용한 피부 분석 모듈
OpenAI의 Vision API를 사용하여 이미지에서 피부 나이 및 특성을 추정합니다.
"""

import os
import base64
import logging
import re
import json
from io import BytesIO
import openai
from PIL import Image

logger = logging.getLogger(__name__)

# OpenAI API 키 설정
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


def analyze_skin_with_vision(image, user_age=None):
    """
    GPT-4 Vision API를 사용하여 피부 분석을 수행합니다.
    
    Args:
        image (PIL.Image): 분석할 이미지
        user_age (int, optional): 사용자의 실제 나이 (선택 사항)
        
    Returns:
        tuple: (estimated_skin_age, features_dict, feedback_text)
    """
    try:
        # 이미지가 None인지 확인
        if image is None:
            logger.error("Image is None in analyze_skin_with_vision")
            return get_default_result()
            
        logger.info("Starting GPT-4 Vision skin analysis")
        
        # 사용자가 실제 나이를 제공했는지 로그
        if user_age:
            logger.debug(f"User provided actual age: {user_age}")
        
        # OpenAI API 키가 있는지 확인
        if not OPENAI_API_KEY:
            logger.warning("No OpenAI API key available, using fallback analysis")
            return get_default_result()
            
        # 이미지를 base64로 변환
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        # GPT-4 Vision API용 프롬프트 구성
        prompt = f"""
Analyze this facial image for a skin analysis app. The user is {user_age or 'unknown'} years old.

1. SKIN AGE: Estimate the skin age in years (just the number).
2. SKIN FEATURES: Rate these features on a scale from 0.0 to 1.0 (higher means more prominent):
   - wrinkles
   - pigmentation
   - elasticity (higher is better)
   - moisture (higher is better)
   - fine_lines
   - dark_spots
   - pores
   - dryness
   - oiliness

3. PERSONALIZED FEEDBACK: Provide gentle feedback in English AND Korean.

Format your response in valid JSON exactly like this:
{{
  "estimated_age": [number],
  "features": {{
    "wrinkles": [0.0-1.0],
    "pigmentation": [0.0-1.0],
    "elasticity": [0.0-1.0],
    "moisture": [0.0-1.0],
    "fine_lines": [0.0-1.0],
    "dark_spots": [0.0-1.0],
    "pores": [0.0-1.0],
    "dryness": [0.0-1.0],
    "oiliness": [0.0-1.0]
  }},
  "feedback_en": "English feedback...",
  "feedback_ko": "Korean feedback..."
}}
"""
        
        logger.info("Calling GPT-4 Vision API for comprehensive skin analysis...")
        
        # OpenAI API 호출
        try:
            # 2024년 5월 기준 최신 모델인 gpt-4o로 업데이트
            gpt_response = openai.chat.completions.create(
                model="gpt-4o", # gpt-4-vision-preview는 더 이상 사용되지 않음 
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional dermatologist and skin analysis expert."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this skin image for a skincare application. Focus only on general skin texture, not on identifying the person. Evaluate skin conditions such as wrinkles, dryness, pigmentation, pores, and elasticity with scores from 0 to 100. Also provide skincare recommendations in both English and Korean. Output in JSON format with these keys: estimated_skin_condition (from 1-100), features, feedback_en, feedback_ko."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                max_tokens=800
            )

            logger.info("GPT-4 Vision API response received successfully!")
            response_text = gpt_response.choices[0].message.content
            logger.debug(f"Raw analysis result: {response_text[:100]}...")
            
            # JSON 응답 파싱
            try:
                result = json.loads(response_text)
                estimated_age = float(result.get("estimated_age", 40))
                features = result.get("features", {})
                
                # 일부 특성이 누락된 경우 기본값 추가
                default_features = {
                    "wrinkles": 0.5, "pigmentation": 0.5, "elasticity": 0.5,
                    "moisture": 0.5, "fine_lines": 0.5, "dark_spots": 0.5,
                    "pores": 0.5, "dryness": 0.5, "oiliness": 0.5
                }
                
                for key, value in default_features.items():
                    if key not in features:
                        features[key] = value
                
                # 피드백 결합
                feedback_en = result.get("feedback_en", "Analysis feedback not available.")
                feedback_ko = result.get("feedback_ko", "분석 피드백을 사용할 수 없습니다.")
                feedback_text = f"{feedback_en}\n\n{feedback_ko}"
                
                logger.info(f"Successfully parsed GPT-4 Vision analysis: age={estimated_age}")
                return estimated_age, features, feedback_text
                
            except json.JSONDecodeError as json_error:
                logger.error(f"Error parsing JSON from GPT-4 Vision: {str(json_error)}")
                
                # JSON 파싱이 실패한 경우 정규 표현식으로 추출 시도
                try:
                    # 추정 나이 추출
                    age_match = re.search(r"estimated_age\"?\s*:\s*(\d+\.?\d*)", response_text)
                    estimated_age = float(age_match.group(1)) if age_match else 40.0
                    
                    # 간단한 피드백 생성
                    feedback = "Based on the analysis, we've detected some characteristics of your skin. " + \
                              "Please consult with a dermatologist for personalized advice.\n\n" + \
                              "분석 결과에 따르면 귀하의 피부에서 몇 가지 특성이 감지되었습니다. " + \
                              "개인화된 조언을 위해 피부과 전문의와 상담하세요."
                    
                    # 기본 특성 값 생성
                    default_age_features = get_age_based_features(estimated_age)
                    
                    return estimated_age, default_age_features, feedback
                except Exception as extraction_error:
                    logger.error(f"Error extracting data with regex: {str(extraction_error)}")
                    return get_default_result()
                
        except Exception as api_error:
            logger.error(f"Error calling GPT-4 Vision API: {str(api_error)}")
            return get_default_result()
            
    except Exception as e:
        logger.error(f"Error in GPT-4 Vision skin analysis: {str(e)}")
        return get_default_result()


def get_default_result():
    """
    기본 피부 분석 결과를 반환합니다.
    """
    feedback = "Could not analyze skin. Please try again with a clearer face photo.\n\n피부 분석에 실패했습니다. 더 선명한 얼굴 사진으로 다시 시도해주세요."
    return 35.0, {
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


def get_age_based_features(age):
    """
    추정 나이에 기반한 피부 특성 값을 생성합니다.
    
    Args:
        age (float): 추정된 피부 나이
        
    Returns:
        dict: 피부 특성 값을 포함하는 딕셔너리
    """
    # 나이에 따라 특성 값 생성
    wrinkles = min(1.0, max(0.0, (age - 20) / 60))
    elasticity = max(0.1, 1.0 - (wrinkles * 0.8))  # 탄력은 나이에 따라 감소
    
    features = {
        "wrinkles": round(wrinkles, 2),
        "pigmentation": round(min(1.0, max(0.1, (age - 25) / 50)), 2),
        "elasticity": round(elasticity, 2),
        "moisture": round(max(0.1, 1.0 - (age / 100)), 2),
        "fine_lines": round(min(1.0, max(0.1, (age - 18) / 55)), 2),
        "dark_spots": round(min(1.0, max(0.1, (age - 30) / 45)), 2),
        "pores": round(min(1.0, max(0.2, (age - 15) / 70)), 2),
        "dryness": round(min(1.0, max(0.1, (age - 20) / 60)), 2),
        "oiliness": round(max(0.1, 0.8 - (age / 100)), 2)
    }
    
    return features