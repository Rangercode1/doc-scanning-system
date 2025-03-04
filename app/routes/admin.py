from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Document, Scan, CreditRequest, User
from datetime import datetime, timedelta
from sqlalchemy import func
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    # Get basic statistics
    total_users = User.query.count()
    total_documents = Document.query.count()
    total_scans = Scan.query.count()
    pending_requests = CreditRequest.query.filter_by(status='pending').count()
    
    # Get recent activity
    recent_scans = Scan.query.order_by(Scan.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html',
                         total_users=total_users,
                         total_documents=total_documents,
                         total_scans=total_scans,
                         pending_requests=pending_requests,
                         recent_scans=recent_scans,
                         recent_users=recent_users)

@admin_bp.route('/credit-requests')
@login_required
@admin_required
def credit_requests():
    page = request.args.get('page', 1, type=int)
    requests = CreditRequest.query.order_by(
        CreditRequest.status == 'pending',
        CreditRequest.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/credit_requests.html', requests=requests)

@admin_bp.route('/credit-requests/<int:request_id>/<action>')
@login_required
@admin_required
def process_credit_request(request_id, action):
    credit_request = CreditRequest.query.get_or_404(request_id)
    
    if credit_request.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('admin.credit_requests'))
    
    if action == 'approve':
        user = User.query.get(credit_request.user_id)
        user.add_credits(credit_request.amount)
        credit_request.status = 'approved'
        flash(f'Approved {credit_request.amount} credits for {user.username}', 'success')
    elif action == 'reject':
        credit_request.status = 'rejected'
        flash('Credit request rejected', 'info')
    else:
        flash('Invalid action', 'danger')
        return redirect(url_for('admin.credit_requests'))
    
    credit_request.processed_at = datetime.utcnow()
    credit_request.processed_by = current_user.id
    db.session.commit()
    
    return redirect(url_for('admin.credit_requests'))

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    # Get date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Daily scans over time
    daily_scans = db.session.query(
        func.date(Scan.created_at).label('date'),
        func.count(Scan.id).label('count')
    ).filter(
        Scan.created_at >= start_date
    ).group_by(
        func.date(Scan.created_at)
    ).all()
    
    # Top users by scan count
    top_users = db.session.query(
        User.username,
        func.count(Scan.id).label('scan_count')
    ).join(Scan).group_by(User.id).order_by(
        func.count(Scan.id).desc()
    ).limit(10).all()
    
    # Credit usage statistics
    credit_stats = db.session.query(
        func.sum(CreditRequest.amount).label('total_requested'),
        func.count(CreditRequest.id).label('total_requests'),
        func.avg(CreditRequest.amount).label('avg_request_amount')
    ).filter(
        CreditRequest.status == 'approved'
    ).first()
    
    return render_template('admin/analytics.html',
                         daily_scans=daily_scans,
                         top_users=top_users,
                         credit_stats=credit_stats)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users) 