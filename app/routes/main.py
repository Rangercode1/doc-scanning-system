import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Document, Scan, CreditRequest
from app.utils.document_matching import calculate_similarity, get_document_hash
from datetime import datetime, timedelta
from sqlalchemy import func
from io import BytesIO

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        recent_scans = current_user.scans.order_by(Scan.created_at.desc()).limit(5).all()
        return render_template('main/index.html', recent_scans=recent_scans)
    return render_template('main/index.html')

@main_bp.route('/profile')
@login_required
def profile():
    # Reset daily credits if needed
    current_user.reset_daily_credits()
    scans = current_user.scans.order_by(Scan.created_at.desc()).limit(10).all()
    documents = current_user.documents.order_by(Document.created_at.desc()).limit(10).all()
    return render_template('main/profile.html', scans=scans, documents=documents)

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # Check if user has credits
        if current_user.credits <= 0:
            flash('You have no credits remaining. Please request more credits.', 'danger')
            return redirect(url_for('main.profile'))

        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Try different encodings to read the file
            encodings = ['utf-8', 'latin1', 'cp1252', 'ascii']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            # If no encoding worked, try binary mode
            if content is None:
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='ignore')
                except Exception as e:
                    os.remove(file_path)
                    flash('Error reading file: ' + str(e), 'danger')
                    return redirect(request.url)

            # Calculate document hash
            content_hash = get_document_hash(content)

            # Create document
            document = Document(
                filename=filename,
                content=content,
                content_hash=content_hash,
                user_id=current_user.id
            )
            db.session.add(document)
            
            # Find similar documents
            similar_docs = calculate_similarity(document)
            
            # Create scan records for matches
            scan = None
            for doc, score in similar_docs:
                scan = Scan(
                    source_document_id=document.id,
                    user_id=current_user.id,
                    similarity_score=score,
                    matched_document_id=doc.id
                )
                db.session.add(scan)
            
            # Deduct credit
            current_user.deduct_credit()
            
            db.session.commit()
            
            # Clean up uploaded file
            os.remove(file_path)
            
            flash('Document uploaded and scanned successfully!', 'success')
            if scan:
                return redirect(url_for('main.scan_results', scan_id=scan.id))
            return redirect(url_for('main.documents'))
            
        flash('Invalid file type', 'danger')
        return redirect(request.url)
    
    recent_docs = current_user.documents.order_by(Document.created_at.desc()).limit(5).all()
    return render_template('main/upload.html', recent_docs=recent_docs)

@main_bp.route('/scan_results/<int:scan_id>')
@login_required
def scan_results(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    if scan.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.profile'))
    
    return render_template('main/scan_results.html', scan=scan)

@main_bp.route('/documents')
@login_required
def documents():
    page = request.args.get('page', 1, type=int)
    documents = current_user.documents.order_by(Document.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('main/documents.html', documents=documents)

@main_bp.route('/documents/<int:document_id>/view')
@login_required
def view_document(document_id):
    document = Document.query.get_or_404(document_id)
    if document.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.documents'))
    return render_template('main/view_document.html', document=document)

@main_bp.route('/documents/<int:document_id>/download')
@login_required
def download_document(document_id):
    document = Document.query.get_or_404(document_id)
    if document.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.documents'))
    
    # Create a BytesIO object with the document content
    document_io = BytesIO(document.content.encode('utf-8'))
    
    # Send the file with the original filename
    return send_file(
        document_io,
        mimetype='text/plain',
        as_attachment=True,
        download_name=document.filename
    )

@main_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get date range for analytics
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Calculate total documents
        total_documents = current_user.documents.count()
        
        # Calculate matches found
        matches_found = current_user.scans.filter(Scan.matched_document_id.isnot(None)).count()
        
        # Calculate scans today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        scans_today = current_user.scans.filter(Scan.created_at >= today_start).count()
        
        # Get recent activity
        recent_activity = []
        recent_scans = current_user.scans.order_by(Scan.created_at.desc()).limit(5).all()
        
        for scan in recent_scans:
            score = int(scan.similarity_score * 100) if scan.similarity_score else 0
            activity = {
                'icon': 'fa-search' if scan.matched_document_id else 'fa-times',
                'title': f"Scan {'matched' if scan.matched_document_id else 'not matched'}",
                'timestamp': scan.created_at.strftime('%Y-%m-%d %H:%M'),
                'description': f"Similarity: {score}%" if scan.matched_document_id else "No match found",
                'action_url': url_for('main.scan_results', scan_id=scan.id),
                'action_text': 'View Results'
            }
            recent_activity.append(activity)
        
        # Prepare stats dictionary
        stats = {
            'total_documents': total_documents,
            'matches_found': matches_found,
            'scans_today': scans_today
        }
        
        return render_template('main/dashboard.html',
                             stats=stats,
                             recent_activity=recent_activity)
                             
    except Exception as e:
        flash('An error occurred while loading the dashboard. Please try again.', 'danger')
        print(f"Dashboard Error: {str(e)}")  # For logging
        return redirect(url_for('main.index'))

@main_bp.route('/request-credits', methods=['POST'])
@login_required
def request_credits():
    amount = request.form.get('amount', type=int)
    reason = request.form.get('reason')
    
    if not amount or amount <= 0 or amount > 100:
        flash('Please enter a valid credit amount (1-100).', 'danger')
        return redirect(url_for('main.dashboard'))
    
    credit_request = CreditRequest(
        user_id=current_user.id,
        amount=amount,
        reason=reason
    )
    db.session.add(credit_request)
    db.session.commit()
    
    flash('Your credit request has been submitted and is pending approval.', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/credits')
@login_required
def credits():
    # Get credit requests history
    credit_requests = CreditRequest.query.filter_by(user_id=current_user.id)\
        .order_by(CreditRequest.created_at.desc()).all()
    
    # Calculate daily credit usage
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    scans_today = current_user.scans.filter(Scan.created_at >= today_start).count()
    
    # Get pending credit requests
    pending_requests = CreditRequest.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).all()
    
    return render_template('main/credits.html',
                         credit_requests=credit_requests,
                         scans_today=scans_today,
                         pending_requests=pending_requests) 