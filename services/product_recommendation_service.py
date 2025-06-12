"""
Product Recommendation Service
쿠팡파트너스와 아마존 어소시에이트 API 연동 준비된 제품 추천 시스템
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

@dataclass
class ProductRecommendation:
    """제품 추천 데이터 클래스"""
    title: str
    price: str
    image_url: str
    product_url: str
    rating: float
    review_count: int
    brand: str
    category: str
    source: str  # 'coupang' or 'amazon'
    description: str = ""
    
class SkinAnalysisMapper:
    """피부 분석 결과를 제품 추천 키워드로 매핑"""
    
    # 피부 문제별 추천 성분 및 제품 타입
    SKIN_ISSUE_MAPPING = {
        'wrinkles': {
            'keywords': ['retinol', 'anti-aging', 'collagen', 'peptide', '주름', '안티에이징'],
            'ingredients': ['retinol', 'peptide', 'collagen', 'hyaluronic acid'],
            'avoid_sensitive': ['retinol'],  # 민감 피부 시 피할 성분
            'alternative_sensitive': ['bakuchiol', 'vitamin c']  # 민감 피부 대안
        },
        'fine_lines': {
            'keywords': ['fine lines', 'anti-aging cream', 'vitamin c', '잔주름', '비타민c'],
            'ingredients': ['vitamin c', 'niacinamide', 'peptide'],
            'avoid_sensitive': [],
            'alternative_sensitive': []
        },
        'pigmentation': {
            'keywords': ['whitening', 'brightening', 'vitamin c', 'niacinamide', '미백', '기미'],
            'ingredients': ['vitamin c', 'niacinamide', 'arbutin', 'kojic acid'],
            'avoid_sensitive': ['kojic acid'],
            'alternative_sensitive': ['vitamin c', 'niacinamide']
        },
        'dark_spots': {
            'keywords': ['dark spot', 'spot treatment', 'brightening serum', '다크스팟', '기미'],
            'ingredients': ['vitamin c', 'hydroquinone', 'arbutin'],
            'avoid_sensitive': ['hydroquinone'],
            'alternative_sensitive': ['vitamin c', 'licorice extract']
        },
        'dryness': {
            'keywords': ['moisturizer', 'hydrating cream', 'hyaluronic acid', '보습', '수분크림'],
            'ingredients': ['hyaluronic acid', 'ceramide', 'glycerin', 'squalane'],
            'avoid_sensitive': [],
            'alternative_sensitive': []
        },
        'moisture': {
            'keywords': ['hydrating', 'moisture barrier', 'ceramide', '수분', '보습'],
            'ingredients': ['hyaluronic acid', 'ceramide', 'glycerin'],
            'avoid_sensitive': [],
            'alternative_sensitive': []
        },
        'elasticity': {
            'keywords': ['firming', 'elasticity', 'collagen', 'peptide', '탄력', '콜라겐'],
            'ingredients': ['peptide', 'collagen', 'elastin'],
            'avoid_sensitive': [],
            'alternative_sensitive': []
        },
        'pores': {
            'keywords': ['pore minimizer', 'niacinamide', 'bha', '모공', '니아신아마이드'],
            'ingredients': ['niacinamide', 'salicylic acid', 'zinc'],
            'avoid_sensitive': ['salicylic acid'],
            'alternative_sensitive': ['niacinamide', 'zinc']
        },
        'oiliness': {
            'keywords': ['oil control', 'sebum control', 'niacinamide', '유분', '기름'],
            'ingredients': ['niacinamide', 'salicylic acid', 'zinc oxide'],
            'avoid_sensitive': ['salicylic acid'],
            'alternative_sensitive': ['niacinamide', 'zinc oxide']
        }
    }
    
    @classmethod
    def generate_keywords(cls, features: Dict[str, float], user_age: int = None, 
                         is_sensitive: bool = False) -> List[str]:
        """피부 분석 결과를 기반으로 검색 키워드 생성"""
        keywords = []
        priority_issues = []
        
        # 높은 수치의 문제들을 우선순위로 정렬
        sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
        
        for issue, score in sorted_features:
            if score > 0.6:  # 임계값 이상인 문제들만 처리
                priority_issues.append((issue, score))
                
                if issue in cls.SKIN_ISSUE_MAPPING:
                    mapping = cls.SKIN_ISSUE_MAPPING[issue]
                    
                    if is_sensitive and mapping['avoid_sensitive']:
                        # 민감 피부용 대안 키워드 사용
                        keywords.extend(mapping['alternative_sensitive'])
                    else:
                        keywords.extend(mapping['keywords'])
        
        # 나이별 추가 키워드
        if user_age:
            if user_age >= 40:
                keywords.extend(['anti-aging', 'mature skin', '안티에이징'])
            elif user_age >= 30:
                keywords.extend(['prevention', 'early anti-aging', '예방'])
            else:
                keywords.extend(['basic care', '기초케어'])
        
        # 중복 제거 후 상위 10개 키워드만 반환
        return list(dict.fromkeys(keywords))[:10]

class ProductRecommendationEngine:
    """제품 추천 엔진 - API 연동 준비된 구조"""
    
    def __init__(self):
        # API 설정 (환경변수에서 가져오기)
        self.coupang_access_key = os.environ.get('COUPANG_ACCESS_KEY')
        self.coupang_secret_key = os.environ.get('COUPANG_SECRET_KEY') 
        self.amazon_access_key = os.environ.get('AMAZON_ACCESS_KEY')
        self.amazon_secret_key = os.environ.get('AMAZON_SECRET_KEY')
        self.amazon_associate_tag = os.environ.get('AMAZON_ASSOCIATE_TAG')
        
        # 캐시 설정
        self.cache = {}
        self.cache_duration = timedelta(hours=6)  # 6시간 캐시
        
        # API 호출 제한 설정
        self.api_call_limit = 1000  # 일일 호출 제한
        self.daily_calls = 0
        self.last_reset = datetime.now().date()
        
    def is_api_available(self, source: str) -> bool:
        """API 사용 가능 여부 확인"""
        if source == 'coupang':
            return bool(self.coupang_access_key and self.coupang_secret_key)
        elif source == 'amazon':
            return bool(self.amazon_access_key and self.amazon_secret_key and self.amazon_associate_tag)
        return False
    
    def get_cache_key(self, keywords: List[str], source: str) -> str:
        """캐시 키 생성"""
        return f"{source}_{hash('_'.join(sorted(keywords)))}"
    
    def is_cache_valid(self, cache_entry: Dict) -> bool:
        """캐시 유효성 확인"""
        if not cache_entry:
            return False
        cache_time = datetime.fromisoformat(cache_entry['timestamp'])
        return datetime.now() - cache_time < self.cache_duration
    
    def reset_daily_limit_if_needed(self):
        """일일 제한 리셋"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_calls = 0
            self.last_reset = today
    
    def search_coupang_products(self, keywords: List[str]) -> List[ProductRecommendation]:
        """쿠팡 제품 검색 (API 연동 준비)"""
        logger.info(f"Searching Coupang products for keywords: {keywords}")
        
        if not self.is_api_available('coupang'):
            logger.warning("Coupang API credentials not available")
            return self._get_fallback_products('coupang', keywords)
        
        cache_key = self.get_cache_key(keywords, 'coupang')
        
        # 캐시 확인
        if cache_key in self.cache and self.is_cache_valid(self.cache[cache_key]):
            logger.info("Returning cached Coupang results")
            return [ProductRecommendation(**item) for item in self.cache[cache_key]['products']]
        
        # API 호출 제한 확인
        self.reset_daily_limit_if_needed()
        if self.daily_calls >= self.api_call_limit:
            logger.warning("Daily API call limit reached")
            return self._get_fallback_products('coupang', keywords)
        
        try:
            # TODO: 실제 쿠팡 API 호출 로직 구현
            # 현재는 기본 구조만 준비
            products = self._call_coupang_api(keywords)
            
            # 캐시 저장
            self.cache[cache_key] = {
                'products': [product.__dict__ for product in products],
                'timestamp': datetime.now().isoformat()
            }
            
            self.daily_calls += 1
            return products
            
        except Exception as e:
            logger.error(f"Coupang API error: {e}")
            return self._get_fallback_products('coupang', keywords)
    
    def search_amazon_products(self, keywords: List[str]) -> List[ProductRecommendation]:
        """아마존 제품 검색 (API 연동 준비)"""
        logger.info(f"Searching Amazon products for keywords: {keywords}")
        
        if not self.is_api_available('amazon'):
            logger.warning("Amazon API credentials not available")
            return self._get_fallback_products('amazon', keywords)
        
        cache_key = self.get_cache_key(keywords, 'amazon')
        
        # 캐시 확인
        if cache_key in self.cache and self.is_cache_valid(self.cache[cache_key]):
            logger.info("Returning cached Amazon results")
            return [ProductRecommendation(**item) for item in self.cache[cache_key]['products']]
        
        # API 호출 제한 확인
        self.reset_daily_limit_if_needed()
        if self.daily_calls >= self.api_call_limit:
            logger.warning("Daily API call limit reached")
            return self._get_fallback_products('amazon', keywords)
        
        try:
            # TODO: 실제 아마존 API 호출 로직 구현
            # 현재는 기본 구조만 준비
            products = self._call_amazon_api(keywords)
            
            # 캐시 저장
            self.cache[cache_key] = {
                'products': [product.__dict__ for product in products],
                'timestamp': datetime.now().isoformat()
            }
            
            self.daily_calls += 1
            return products
            
        except Exception as e:
            logger.error(f"Amazon API error: {e}")
            return self._get_fallback_products('amazon', keywords)
    
    def _call_coupang_api(self, keywords: List[str]) -> List[ProductRecommendation]:
        """쿠팡 API 호출 (구현 예정)"""
        # TODO: 실제 쿠팡파트너스 API 호출 로직
        # 지금은 빈 리스트 반환
        return []
    
    def _call_amazon_api(self, keywords: List[str]) -> List[ProductRecommendation]:
        """아마존 API 호출 (구현 예정)"""
        # TODO: 실제 아마존 PA API 호출 로직
        # 지금은 빈 리스트 반환
        return []
    
    def _get_fallback_products(self, source: str, keywords: List[str]) -> List[ProductRecommendation]:
        """API 실패 시 대체 제품 (기본 데이터베이스에서)"""
        logger.info(f"Using fallback products for {source}")
        
        # TODO: 실제 운영시에는 사전 선별된 제품 데이터베이스에서 가져오기
        # 현재는 빈 리스트 반환
        return []
    
    def filter_and_rank_products(self, products: List[ProductRecommendation], 
                                features: Dict[str, float]) -> List[ProductRecommendation]:
        """제품 필터링 및 랭킹"""
        if not products:
            return []
        
        # 평점 4.0 이상, 리뷰 10개 이상 필터링
        filtered_products = [
            p for p in products 
            if p.rating >= 4.0 and p.review_count >= 10
        ]
        
        # 가격대별 다양성 확보 (저가, 중가, 고가)
        # TODO: 가격 분석 및 다양성 로직 구현
        
        # 상위 6개 제품만 반환
        return filtered_products[:6]
    
    def get_recommendations(self, features: Dict[str, float], user_age: int = None,
                          is_sensitive: bool = False) -> Dict[str, List[ProductRecommendation]]:
        """통합 제품 추천"""
        logger.info("Starting product recommendation process")
        
        # 키워드 생성
        keywords = SkinAnalysisMapper.generate_keywords(features, user_age, is_sensitive)
        logger.info(f"Generated keywords: {keywords}")
        
        recommendations = {}
        
        # 쿠팡 제품 검색
        try:
            coupang_products = self.search_coupang_products(keywords)
            recommendations['coupang'] = self.filter_and_rank_products(coupang_products, features)
        except Exception as e:
            logger.error(f"Coupang search failed: {e}")
            recommendations['coupang'] = []
        
        # 아마존 제품 검색
        try:
            amazon_products = self.search_amazon_products(keywords)
            recommendations['amazon'] = self.filter_and_rank_products(amazon_products, features)
        except Exception as e:
            logger.error(f"Amazon search failed: {e}")
            recommendations['amazon'] = []
        
        logger.info(f"Recommendations generated: {len(recommendations['coupang'])} Coupang, {len(recommendations['amazon'])} Amazon")
        return recommendations

# 전역 인스턴스
recommendation_engine = ProductRecommendationEngine()

def get_product_recommendations(features: Dict[str, float], user_age: int = None,
                              is_sensitive: bool = False) -> Dict[str, List[Dict]]:
    """제품 추천 메인 함수"""
    try:
        recommendations = recommendation_engine.get_recommendations(features, user_age, is_sensitive)
        
        # ProductRecommendation 객체를 딕셔너리로 변환
        result = {}
        for source, products in recommendations.items():
            result[source] = [
                {
                    'title': p.title,
                    'price': p.price,
                    'image_url': p.image_url,
                    'product_url': p.product_url,
                    'rating': p.rating,
                    'review_count': p.review_count,
                    'brand': p.brand,
                    'category': p.category,
                    'source': p.source,
                    'description': p.description
                }
                for p in products
            ]
        
        return result
        
    except Exception as e:
        logger.error(f"Product recommendation failed: {e}")
        return {'coupang': [], 'amazon': []}