"""
Product recommendation system based on skin analysis results.
"""

def get_product_recommendations(features, skin_age, actual_age=None):
    """
    Generate product recommendations based on skin analysis features.
    
    Args:
        features (dict): Skin analysis features (wrinkles, pigmentation, etc.)
        skin_age (float): Estimated skin age
        actual_age (int, optional): User's actual age
        
    Returns:
        list: List of recommended products
    """
    recommendations = []
    
    # Get feature values
    wrinkles = features.get('wrinkles', 0)
    pigmentation = features.get('pigmentation', 0)
    elasticity = features.get('elasticity', 0)
    moisture = features.get('moisture', 0)
    fine_lines = features.get('fine_lines', 0)
    dark_spots = features.get('dark_spots', 0)
    pores = features.get('pores', 0)
    dryness = features.get('dryness', 0)
    oiliness = features.get('oiliness', 0)
    
    # Anti-aging products for wrinkles and fine lines
    if wrinkles > 0.3 or fine_lines > 0.3:
        recommendations.append({
            'category': 'Anti-Aging',
            'name': 'Retinol Serum',
            'description': 'Helps reduce fine lines and wrinkles while promoting skin renewal.',
            'price_range': '$25-45'
        })
        
    if wrinkles > 0.5:
        recommendations.append({
            'category': 'Anti-Aging',
            'name': 'Hyaluronic Acid Moisturizer',
            'description': 'Deep hydration to plump skin and reduce visible aging signs.',
            'price_range': '$30-60'
        })
    
    # Pigmentation and dark spot treatments
    if pigmentation > 0.3 or dark_spots > 0.3:
        recommendations.append({
            'category': 'Brightening',
            'name': 'Vitamin C Serum',
            'description': 'Brightens skin tone and reduces dark spots for even complexion.',
            'price_range': '$20-40'
        })
        
    if pigmentation > 0.5:
        recommendations.append({
            'category': 'Treatment',
            'name': 'Niacinamide Serum',
            'description': 'Minimizes pores and evens skin tone while controlling oil.',
            'price_range': '$15-35'
        })
    
    # Moisture and hydration
    if dryness > 0.4 or moisture < 0.4:
        recommendations.append({
            'category': 'Hydration',
            'name': 'Ceramide Moisturizer',
            'description': 'Restores skin barrier and provides long-lasting hydration.',
            'price_range': '$25-50'
        })
        
    if dryness > 0.6:
        recommendations.append({
            'category': 'Intensive Care',
            'name': 'Overnight Repair Mask',
            'description': 'Intensive overnight treatment for dry and damaged skin.',
            'price_range': '$35-65'
        })
    
    # Oil control for oily skin
    if oiliness > 0.6:
        recommendations.append({
            'category': 'Oil Control',
            'name': 'Salicylic Acid Cleanser',
            'description': 'Gently exfoliates and controls excess oil production.',
            'price_range': '$18-30'
        })
        
    if pores > 0.5:
        recommendations.append({
            'category': 'Pore Care',
            'name': 'Clay Mask',
            'description': 'Deep cleanses pores and removes impurities for smoother skin.',
            'price_range': '$20-35'
        })
    
    # Elasticity and firmness
    if elasticity < 0.4:
        recommendations.append({
            'category': 'Firming',
            'name': 'Collagen Boosting Serum',
            'description': 'Improves skin elasticity and firmness for youthful appearance.',
            'price_range': '$40-70'
        })
    
    # Sun protection (always important)
    recommendations.append({
        'category': 'Protection',
        'name': 'Broad Spectrum SPF 50+ Sunscreen',
        'description': 'Essential daily protection against UV damage and premature aging.',
        'price_range': '$15-30'
    })
    
    # Basic skincare routine
    if len(recommendations) < 3:
        recommendations.extend([
            {
                'category': 'Cleansing',
                'name': 'Gentle Daily Cleanser',
                'description': 'Mild formula that cleanses without stripping natural oils.',
                'price_range': '$12-25'
            },
            {
                'category': 'Moisturizing',
                'name': 'Daily Face Moisturizer',
                'description': 'Lightweight formula for daily hydration and protection.',
                'price_range': '$20-40'
            }
        ])
    
    # Limit to 3 recommendations maximum
    return recommendations[:3]