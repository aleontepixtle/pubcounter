from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from flask_socketio import emit
from app import db, job_queue, socketio
from app.models import SavedCredentials, Job
from app.crypto import CredentialEncryption
from datetime import datetime
from rq.job import Job as RQJob
import json

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')


@jobs_bp.route('/submit', methods=['POST'])
@login_required
def submit_job():
    """Submit a new inventory automation job."""
    if not current_user.can_submit_job():
        return jsonify({'error': 'Account not approved'}), 403
    
    data = request.get_json()
    use_saved = data.get('use_saved', False)
    
    if use_saved:
        # Use saved credentials
        saved_creds = SavedCredentials.query.filter_by(user_id=current_user.id).first()
        if not saved_creds:
            return jsonify({'error': 'No saved credentials found'}), 400
        
        # Decrypt credentials
        creds = CredentialEncryption.decrypt_credentials(
            saved_creds.encrypted_username,
            saved_creds.encrypted_password,
            saved_creds.encrypted_totp_secret
        )
        language = saved_creds.language
    else:
        # Use manually provided credentials
        creds = {
            'username': data.get('jw_username'),
            'password': data.get('jw_password'),
            'totp_secret': data.get('jw_totp_secret')
        }
        language = data.get('language', 'en')
        
        if not all(creds.values()):
            return jsonify({'error': 'Missing credentials'}), 400
    
    # Rate limiting check
    if current_app.config['RATELIMIT_ENABLED']:
        recent_jobs = Job.query.filter_by(user_id=current_user.id)\
            .filter(Job.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0))\
            .count()
        
        if recent_jobs >= current_app.config['RATELIMIT_PER_USER_PER_HOUR']:
            return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
    
    # Enqueue the job
    try:
        from app.worker import run_automation_task
        
        rq_job = job_queue.enqueue(
            run_automation_task,
            creds['username'],
            creds['password'],
            creds['totp_secret'],
            language,
            current_user.id,
            job_timeout=3600  # 1 hour timeout
        )
        
        # Create job record in database
        job = Job(
            user_id=current_user.id,
            rq_job_id=rq_job.id,
            status='queued',
            language=language
        )
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'rq_job_id': rq_job.id
        }), 202
        
    except Exception as e:
        current_app.logger.error(f'Error submitting job: {str(e)}')
        return jsonify({'error': 'Failed to submit job'}), 500


@jobs_bp.route('/<int:job_id>/status', methods=['GET'])
@login_required
def job_status(job_id):
    """Get the status of a specific job."""
    job = Job.query.get_or_404(job_id)
    
    # Ensure user can only see their own jobs (unless admin)
    if job.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get RQ job status
    try:
        rq_job = RQJob.fetch(job.rq_job_id, connection=job_queue.connection)
        
        # Update status if changed
        if rq_job.is_failed and job.status != 'failed':
            job.status = 'failed'
            job.error_message = str(rq_job.exc_info) if rq_job.exc_info else 'Unknown error'
            job.completed_at = datetime.utcnow()
            db.session.commit()
        elif rq_job.is_finished and job.status != 'completed':
            job.status = 'completed'
            job.progress = 100
            job.completed_at = datetime.utcnow()
            job.result = json.dumps(rq_job.result) if rq_job.result else None
            db.session.commit()
        elif rq_job.is_started and job.status == 'queued':
            job.status = 'running'
            job.started_at = datetime.utcnow()
            db.session.commit()
            
    except Exception as e:
        current_app.logger.error(f'Error fetching RQ job status: {str(e)}')
    
    return jsonify(job.to_dict())


@jobs_bp.route('/<int:job_id>', methods=['GET'])
@login_required
def get_job(job_id):
    """Get detailed information about a job."""
    job = Job.query.get_or_404(job_id)
    
    # Ensure user can only see their own jobs (unless admin)
    if job.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(job.to_dict())


@jobs_bp.route('/my-jobs', methods=['GET'])
@login_required
def my_jobs():
    """Get all jobs for the current user."""
    jobs = Job.query.filter_by(user_id=current_user.id)\
        .order_by(Job.created_at.desc())\
        .limit(50)\
        .all()
    
    return jsonify([job.to_dict() for job in jobs])


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    if current_user.is_authenticated:
        emit('connected', {'message': 'Connected to job updates'})


@socketio.on('join_job')
def handle_join_job(data):
    """Join a specific job's room for updates."""
    if not current_user.is_authenticated:
        return
    
    job_id = data.get('job_id')
    if job_id:
        job = Job.query.get(job_id)
        if job and (job.user_id == current_user.id or current_user.is_admin):
            emit('joined', {'job_id': job_id})


def emit_job_progress(job_id, progress, current_step, last_publication=None):
    """Emit job progress update via WebSocket."""
    job = Job.query.get(job_id)
    if job:
        job.progress = progress
        job.current_step = current_step
        if last_publication:
            job.last_publication = last_publication
        db.session.commit()
        
        # Emit to all clients in this job's room
        socketio.emit('job_progress', {
            'job_id': job_id,
            'progress': progress,
            'current_step': current_step,
            'last_publication': last_publication
        }, room=f'job_{job_id}')