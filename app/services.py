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
