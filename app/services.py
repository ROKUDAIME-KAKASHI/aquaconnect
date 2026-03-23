import json


def analyze_water_quality(ph: float, temperature: float, dissolved_oxygen: float,
                           ammonia: float = 0.0, salinity: float = 0.0) -> dict:
    """
    Rule-based AI water quality analysis engine.
    Returns health_status (good | warning | critical), alerts, recommendations,
    and a numeric risk_score (0-100).
    Expandable: replace thresholds with an ML model (e.g., scikit-learn).
    """
    alerts = []
    recommendations = []
    risk_points = 0

    # ── pH Analysis ─────────────────────────────────────────────────────────
    if ph < 5.0 or ph > 9.5:
        alerts.append('⚠️ pH critically out of range')
        recommendations.append('Immediately apply lime (low pH) or dilute with fresh water (high pH).')
        risk_points += 40
    elif ph < 6.5 or ph > 8.5:
        alerts.append('🔶 pH slightly out of optimal range (6.5–8.5)')
        recommendations.append('Monitor pH closely and adjust gradually using buffering agents.')
        risk_points += 20

    # ── Temperature Analysis ─────────────────────────────────────────────────
    if temperature < 15 or temperature > 35:
        alerts.append('⚠️ Temperature critically out of safe range')
        recommendations.append('Consider shading ponds, aerators, or water exchange to regulate temperature.')
        risk_points += 35
    elif temperature < 20 or temperature > 30:
        alerts.append('🔶 Temperature outside optimal range (20–30°C)')
        recommendations.append('Monitor temperature daily and adjust feeding rates accordingly.')
        risk_points += 15

    # ── Dissolved Oxygen Analysis ────────────────────────────────────────────
    if dissolved_oxygen < 3.0:
        alerts.append('🚨 Dissolved oxygen critically low – immediate action required')
        recommendations.append('Run aerators immediately and reduce feed input. Check for algae blooms.')
        risk_points += 45
    elif dissolved_oxygen < 5.0:
        alerts.append('🔶 Dissolved oxygen below optimal (5+ mg/L)')
        recommendations.append('Increase aeration duration and avoid overcrowding.')
        risk_points += 20

    # ── Ammonia Analysis ─────────────────────────────────────────────────────
    if ammonia > 1.0:
        alerts.append('🚨 Ammonia level dangerously high – toxic to fish')
        recommendations.append('Perform 30% water exchange immediately. Reduce feed and add beneficial bacteria.')
        risk_points += 40
    elif ammonia > 0.5:
        alerts.append('🔶 Ammonia elevated')
        recommendations.append('Reduce feeding by 20% and increase biological filtration.')
        risk_points += 20

    # ── Health Status ────────────────────────────────────────────────────────
    risk_score = min(risk_points, 100)
    if risk_score == 0:
        health_status = 'good'
    elif risk_score <= 30:
        health_status = 'warning'
    else:
        health_status = 'critical'

    if not recommendations:
        recommendations.append('All water parameters are within optimal ranges. Keep up the good work!')

    return {
        'health_status': health_status,
        'risk_score': risk_score,
        'alerts': alerts,
        'recommendations': recommendations,
        'parameter_summary': {
            'ph': {'value': ph, 'optimal': '6.5–8.5', 'status': _param_status(ph, 6.5, 8.5, 5.0, 9.5)},
            'temperature': {'value': temperature, 'optimal': '20–30°C', 'status': _param_status(temperature, 20, 30, 15, 35)},
            'dissolved_oxygen': {'value': dissolved_oxygen, 'optimal': '5+ mg/L', 'status': _do_status(dissolved_oxygen)},
            'ammonia': {'value': ammonia, 'optimal': '<0.5 mg/L', 'status': _ammonia_status(ammonia)},
        }
    }


def _param_status(val, opt_low, opt_high, crit_low, crit_high):
    if val < crit_low or val > crit_high:
        return 'critical'
    if val < opt_low or val > opt_high:
        return 'warning'
    return 'good'


def _do_status(val):
    if val < 3.0:
        return 'critical'
    if val < 5.0:
        return 'warning'
    return 'good'


def _ammonia_status(val):
    if val > 1.0:
        return 'critical'
    if val > 0.5:
        return 'warning'
    return 'good'


def calculate_financial_summary(transactions: list) -> dict:
    """Aggregate transactions into income, expenses, profit, and margin."""
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    profit = total_income - total_expense
    margin = (profit / total_income * 100) if total_income > 0 else 0

    by_category = {}
    for t in transactions:
        cat = t.get('category', 'Other')
        by_category.setdefault(cat, {'income': 0, 'expense': 0})
        by_category[cat][t['type']] = by_category[cat].get(t['type'], 0) + t['amount']

    return {
        'total_income': round(total_income, 2),
        'total_expense': round(total_expense, 2),
        'profit': round(profit, 2),
        'profit_margin_pct': round(margin, 1),
        'profitability': 'profitable' if profit > 0 else ('break_even' if profit == 0 else 'loss'),
        'by_category': by_category,
    }


def get_weather_alert(location: str) -> dict:
    """
    Geocodes a location string and fetches a 3-day forecast from Open-Meteo.
    Returns aquaculture-specific weather alerts.
    """
    if not location:
        return None
        
    try:
        import urllib.request
        import urllib.parse
        import ssl
        import json
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # 1. Geocode
        safe_loc = urllib.parse.quote(location)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={safe_loc}&count=1"
        req = urllib.request.Request(geo_url, headers={'User-Agent': 'AquaConnect/1.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
            geo_data = json.loads(response.read().decode())
            
        if not geo_data.get('results'):
            return None
            
        lat = geo_data['results'][0]['latitude']
        lon = geo_data['results'][0]['longitude']
        loc_name = geo_data['results'][0]['name']
        
        # 2. Weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,precipitation_sum&timezone=auto&forecast_days=3"
        req2 = urllib.request.Request(weather_url, headers={'User-Agent': 'AquaConnect/1.0'})
        with urllib.request.urlopen(req2, timeout=5, context=ctx) as response2:
            weather_data = json.loads(response2.read().decode())
            
        daily = weather_data.get('daily', {})
        max_temps = daily.get('temperature_2m_max', [])
        precips = daily.get('precipitation_sum', [])
        dates = daily.get('time', [])
        
        # 3. Analyze
        alert_level = 'info'
        alert_text = "Upcoming weather looks stable for aquaculture."
        alert_icon = "🌤️"
        
        if max_temps and max(max_temps) >= 35.0:
            alert_level = 'danger'
            alert_text = "High Heat Advisory: Temperatures over 35°C expected. Dissolved oxygen drops quickly in heat. Maximize aeration."
            alert_icon = "🥵"
        elif precips and sum(precips) >= 15.0:
            alert_level = 'warning'
            alert_text = f"Heavy Rain Expected ({sum(precips):.1f}mm). Prepare lime mapping as pH may drop suddenly."
            alert_icon = "🌧️"
        elif max_temps and min(max_temps) <= 18.0:
            alert_level = 'warning'
            alert_text = "Cold Temps expected. Fish metabolism will decrease, reduce feeding to avoid water fouling."
            alert_icon = "❄️"
            
        return {
            'location_name': loc_name,
            'alert_level': alert_level,
            'alert_text': alert_text,
            'alert_icon': alert_icon,
            'forecast': [
                {'date': dates[i], 'temp': max_temps[i], 'precip': precips[i]}
                for i in range(len(dates))
            ] if dates else []
        }
        
    except Exception as e:
        print(f"Weather API Error: {e}")
        return None

def generate_ai_expert_reply(title: str, content: str) -> str:
    """Uses Google Gemini API to generate an expert aquaculture response."""
    import os
    import google.generativeai as genai
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return "The AI Expert is currently offline (API key not configured). Please contact human support."
        
    try:
        genai.configure(api_key=api_key)
        prompt = f"Forum Post Title: {title}\n\nContent: {content}\n\nPlease help this farmer."
        
        # Depending on the user's specific Google AI Studio tier, certain model names might be restricted.
        # We loop through the standard naming conventions to find the one associated with their API key.
        available_models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
        
        for m in available_models:
            try:
                model = genai.GenerativeModel(m,
                    system_instruction="You are AquaConnect AI, an expert, specialized aquaculture scientist and veterinarian. A farmer is asking for help on a forum. Give a highly practical, scientifically accurate, and encouraging response in clean markdown. Keep it concise (under 250 words)."
                )
                response = model.generate_content(prompt)
                return response.text
            except Exception as inner_e:
                print(f"[AI Fallback] Model {m} failed: {inner_e}")
                continue
                
        # If all loops fail, the outer exception block catches it
        raise Exception("All targeted Gemini models returned access or quota errors.")
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I apologize, but I am currently unable to process your request. A human expert will review this soon."
