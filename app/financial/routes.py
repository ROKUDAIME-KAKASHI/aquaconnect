import csv, io
from datetime import date
from flask import render_template, redirect, url_for, request, flash, make_response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.financial import financial_bp
from app.models import User, Farm, Transaction
from app.services import calculate_financial_summary
from app import db


def get_current_user():
    try:
        verify_jwt_in_request(locations=['cookies'])
        return User.query.get(int(get_jwt_identity()))
    except Exception:
        return None


@financial_bp.route('/')
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farms = Farm.query.filter_by(owner_id=user.id).all()
    farm_id = request.args.get('farm_id', type=int)
    selected_farm = None
    transactions = []
    summary = None
    if farms:
        selected_farm = Farm.query.get(farm_id) if farm_id else farms[0]
        if selected_farm and selected_farm.owner_id == user.id:
            txs = (Transaction.query
                   .filter_by(farm_id=selected_farm.id)
                   .order_by(Transaction.date.desc()).all())
            transactions = [t.to_dict() for t in txs]
            summary = calculate_financial_summary(transactions)
    return render_template('financial/index.html',
                           user=user, farms=farms, selected_farm=selected_farm,
                           transactions=transactions, summary=summary)


@financial_bp.route('/add', methods=['POST'])
def add_transaction():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farm_id = request.form.get('farm_id', type=int)
    farm = Farm.query.get(farm_id)
    if not farm or farm.owner_id != user.id:
        flash('Farm not found.', 'error')
        return redirect(url_for('financial.index'))

    tx = Transaction(
        farm_id=farm_id,
        type=request.form.get('type', 'expense'),
        amount=float(request.form.get('amount', 0)),
        category=request.form.get('category', '').strip(),
        description=request.form.get('description', '').strip(),
        date=date.fromisoformat(request.form.get('date') or date.today().isoformat()),
    )
    db.session.add(tx)
    db.session.commit()
    flash('Transaction recorded.', 'success')
    return redirect(url_for('financial.index', farm_id=farm_id))


# ── Edit / Delete Transaction ─────────────────────────────────────────────────

@financial_bp.route('/transaction/<int:tx_id>/edit', methods=['POST'])
def edit_transaction(tx_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    tx = Transaction.query.get_or_404(tx_id)
    farm = Farm.query.get(tx.farm_id)
    if not farm or farm.owner_id != user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('financial.index'))
    tx.type = request.form.get('type', tx.type)
    tx.amount = float(request.form.get('amount', tx.amount))
    tx.category = request.form.get('category', '').strip()
    tx.description = request.form.get('description', '').strip()
    tx.date = date.fromisoformat(request.form.get('date') or tx.date.isoformat())
    db.session.commit()
    flash('Transaction updated.', 'success')
    return redirect(url_for('financial.index', farm_id=tx.farm_id))


@financial_bp.route('/transaction/<int:tx_id>/delete', methods=['POST'])
def delete_transaction(tx_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    tx = Transaction.query.get_or_404(tx_id)
    farm = Farm.query.get(tx.farm_id)
    if not farm or farm.owner_id != user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('financial.index'))
    farm_id = tx.farm_id
    db.session.delete(tx)
    db.session.commit()
    flash('Transaction deleted.', 'success')
    return redirect(url_for('financial.index', farm_id=farm_id))


# ── Financial Report ──────────────────────────────────────────────────────────

@financial_bp.route('/report')
def report():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farms = Farm.query.filter_by(owner_id=user.id).all()
    farm_id = request.args.get('farm_id', type=int)
    selected_year = request.args.get('year', type=int, default=date.today().year)
    selected_farm = farms[0] if farms else None
    if farm_id:
        f = Farm.query.get(farm_id)
        if f and f.owner_id == user.id:
            selected_farm = f

    all_txs = []
    if selected_farm:
        all_txs = Transaction.query.filter_by(farm_id=selected_farm.id).all()

    from sqlalchemy import extract
    year_txs = [t for t in all_txs if t.date.year == selected_year]
    total_income  = sum(t.amount for t in year_txs if t.type == 'income')
    total_expense = sum(t.amount for t in year_txs if t.type == 'expense')
    net_profit = total_income - total_expense
    profit_margin = round((net_profit / total_income * 100) if total_income else 0, 1)

    MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    monthly = []
    for i, m in enumerate(MONTHS, 1):
        mo_txs = [t for t in year_txs if t.date.month == i]
        inc = sum(t.amount for t in mo_txs if t.type == 'income')
        exp = sum(t.amount for t in mo_txs if t.type == 'expense')
        monthly.append({'month': m, 'income': inc, 'expense': exp, 'net': inc - exp})

    expense_txs = [t for t in year_txs if t.type == 'expense']
    cat_totals = {}
    for t in expense_txs:
        k = t.category or 'Uncategorized'
        cat_totals[k] = cat_totals.get(k, 0) + t.amount
    total_exp = sum(cat_totals.values()) or 1
    category_breakdown = sorted([
        {'category': k, 'amount': v, 'pct': round(v / total_exp * 100, 1)}
        for k, v in cat_totals.items()
    ], key=lambda x: -x['amount'])

    years_available = sorted({t.date.year for t in all_txs}, reverse=True) or [date.today().year]

    from app.services import calculate_financial_summary
    summary_obj = type('S', (), {
        'total_income': total_income, 'total_expense': total_expense,
        'net_profit': net_profit, 'profit_margin': profit_margin
    })()

    return render_template('financial/report.html',
                           user=user, farms=farms, selected_farm=selected_farm,
                           summary=summary_obj, monthly=monthly,
                           category_breakdown=category_breakdown,
                           years=years_available, selected_year=selected_year)


# ── Export CSV ────────────────────────────────────────────────────────────────

@financial_bp.route('/export')
def export_csv():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farm_id = request.args.get('farm_id', type=int)
    farms = Farm.query.filter_by(owner_id=user.id).all()
    farm_ids = [f.id for f in farms]
    q = Transaction.query.filter(Transaction.farm_id.in_(farm_ids))
    if farm_id and farm_id in farm_ids:
        q = q.filter_by(farm_id=farm_id)
    txs = q.order_by(Transaction.date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Amount', 'Category', 'Description', 'Farm ID'])
    for t in txs:
        writer.writerow([t.date, t.type, t.amount, t.category or '', t.description or '', t.farm_id])
    output.seek(0)
    resp = make_response(output.getvalue())
    resp.headers['Content-Disposition'] = 'attachment; filename=financial_export.csv'
    resp.headers['Content-Type'] = 'text/csv'
    return resp

