from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, SavedCredentials, Job
from app.forms import CredentialsForm, ManualSubmitForm
from app.crypto import CredentialEncryption

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page - redirect to dashboard if logged in, otherwise to login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing recent jobs and quick actions."""
    if not current_user.can_submit_job():
        flash('Your account is not yet approved. Please wait for administrator approval.', 'warning')
    
    # Get user's recent jobs
    recent_jobs = Job.query.filter_by(user_id=current_user.id)\
        .order_by(Job.created_at.desc())\
        .limit(10)\
        .all()
    
    # Check if user has saved credentials
    has_saved_creds = SavedCredentials.query.filter_by(user_id=current_user.id).first() is not None
    
    return render_template('dashboard.html', 
                         recent_jobs=recent_jobs,
                         has_saved_creds=has_saved_creds)


@main_bp.route('/submit')
@login_required
def submit():
    """Job submission page."""
    if not current_user.can_submit_job():
        flash('Your account is not approved yet. Please contact an administrator.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Check if user has saved credentials
    saved_creds = SavedCredentials.query.filter_by(user_id=current_user.id).first()
    
    manual_form = ManualSubmitForm()
    
    return render_template('submit.html', 
                         has_saved_creds=saved_creds is not None,
                         manual_form=manual_form)


@main_bp.route('/credentials', methods=['GET', 'POST'])
@login_required
def credentials():
    """Manage saved credentials."""
    saved_creds = SavedCredentials.query.filter_by(user_id=current_user.id).first()
    
    form = CredentialsForm()
    
    if form.validate_on_submit():
        # Encrypt the credentials
        encrypted = CredentialEncryption.encrypt_credentials(
            form.jw_username.data,
            form.jw_password.data,
            form.jw_totp_secret.data
        )
        
        if saved_creds:
            # Update existing credentials
            saved_creds.encrypted_username = encrypted['username']
            saved_creds.encrypted_password = encrypted['password']
            saved_creds.encrypted_totp_secret = encrypted['totp_secret']
            saved_creds.language = form.language.data
            flash('Credentials updated successfully!', 'success')
        else:
            # Create new credentials
            saved_creds = SavedCredentials(
                user_id=current_user.id,
                encrypted_username=encrypted['username'],
                encrypted_password=encrypted['password'],
                encrypted_totp_secret=encrypted['totp_secret'],
                language=form.language.data
            )
            db.session.add(saved_creds)
            flash('Credentials saved successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('main.credentials'))
    
    # Pre-fill form with existing language if credentials exist
    if saved_creds and request.method == 'GET':
        form.language.data = saved_creds.language
    
    return render_template('credentials.html', 
                         form=form, 
                         has_saved_creds=saved_creds is not None)


@main_bp.route('/credentials/delete', methods=['POST'])
@login_required
def delete_credentials():
    """Delete saved credentials."""
    saved_creds = SavedCredentials.query.filter_by(user_id=current_user.id).first()
    
    if saved_creds:
        db.session.delete(saved_creds)
        db.session.commit()
        flash('Credentials deleted successfully.', 'success')
    else:
        flash('No saved credentials found.', 'info')
    
    return redirect(url_for('main.credentials'))


@main_bp.route('/admin/users')
@login_required
def admin_users():
    """Admin page to manage user approvals."""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    pending_users = User.query.filter_by(is_approved=False, is_active=True).all()
    approved_users = User.query.filter_by(is_approved=True, is_active=True).all()
    
    return render_template('admin_users.html', 
                         pending_users=pending_users,
                         approved_users=approved_users)


@main_bp.route('/admin/users/<int:user_id>/approve', methods=['POST'])
@login_required
def approve_user(user_id):
    """Approve a pending user."""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    flash(f'User {user.username} has been approved.', 'success')
    return redirect(url_for('main.admin_users'))


@main_bp.route('/admin/users/<int:user_id>/deactivate', methods=['POST'])
@login_required
def deactivate_user(user_id):
    """Deactivate a user."""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.is_admin and User.query.filter_by(is_admin=True).count() == 1:
        flash('Cannot deactivate the last admin user.', 'danger')
        return redirect(url_for('main.admin_users'))
    
    user.is_active = False
    db.session.commit()
    
    flash(f'User {user.username} has been deactivated.', 'success')
    return redirect(url_for('main.admin_users'))