import os
import subprocess
import tempfile
import time
import requests
from pathlib import Path
from flask import current_app
import subprocess


def run_automation_task(jw_username, jw_password, jw_totp_secret, language, user_id):
    """
    Execute the Docker automation with provided credentials.
    
    This function:
    1. Creates a temporary .env file with the credentials
    2. Spins up the Docker container with the mounted .env
    3. Monitors the container and reports progress
    4. Cleans up the temporary .env file
    5. Sends Discord notification via n8n webhook
    
    Args:
        jw_username: JW.org username
        jw_password: JW.org password
        jw_totp_secret: TOTP secret for 2FA
        language: Language code for the automation
        user_id: Database user ID for tracking
    
    Returns:
        dict: Results of the automation
    """
    
    # Get configuration from Flask app context
    from app import create_app
    app = create_app()
    
    with app.app_context():
        automation_path = app.config['AUTOMATION_SCRIPT_PATH']
        automation_host_path = app.config['AUTOMATION_SCRIPT_HOST_PATH']
        n8n_webhook = app.config.get('N8N_WEBHOOK_URL', '')

        # Resolve the absolute path (for checking if it exists in the container)
        base_path = Path(__file__).parent.parent
        script_path = (base_path / automation_path).resolve()

        if not script_path.exists():
            raise FileNotFoundError(f'Automation script not found at {script_path}')

        # Use host path for Docker-in-Docker commands (via /var/run/docker.sock)
        host_script_path = Path(automation_host_path).resolve()
        
        # Update job status
        from app import db
        from app.models import Job
        job = Job.query.filter_by(user_id=user_id).order_by(Job.created_at.desc()).first()
        
        temp_env_file = None
        container_name = f'selenium-automation-user-{user_id}-{int(time.time())}'
        
        try:
            # Create temporary .env file
            temp_env_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.env',
                delete=False,
                dir='/tmp'
            )
            
            # Write credentials to temp file
            env_content = f"""JW_USERNAME={jw_username}
JW_PASSWORD={jw_password}
JW_TOTP_SECRET={jw_totp_secret}
LANGUAGE={language}
"""
            temp_env_file.write(env_content)
            temp_env_file.close()
            
            # Make sure the file is only readable by owner
            os.chmod(temp_env_file.name, 0o600)
            
            # Update job to running
            if job:
                job.status = 'running'
                job.progress = 10
                job.current_step = 'Starting Docker container...'
                db.session.commit()
            
            # Build the docker-compose command with the temporary env file
            # We'll use docker run instead of docker-compose for more control
            # IMPORTANT: Use host_script_path for volume mounts since we're using Docker-in-Docker
            docker_cmd = [
                'docker', 'run',
                '--name', container_name,
                '--env-file', temp_env_file.name,
                '--rm',  # Auto-remove container after completion
                '--shm-size', '2gb',
                '-v', f'{host_script_path}/data:/app/data',
                # We need to build the image first or use existing one
                'selenium-inventory-submit:latest',
                # Run script in non-interactive mode with language from env
                'python', 'src/main.py', '--non-interactive', '--language', language
            ]
            
            # First, check if image exists, if not build it
            check_image = subprocess.run(
                ['docker', 'images', '-q', 'selenium-inventory-submit:latest'],
                capture_output=True,
                text=True
            )
            
            if not check_image.stdout.strip():
                # Build the image using host path
                if job:
                    job.current_step = 'Building Docker image (first time only)...'
                    job.progress = 20
                    db.session.commit()

                build_cmd = ['docker', 'build', '-t', 'selenium-inventory-submit:latest', str(host_script_path)]
                subprocess.run(build_cmd, check=True)
            
            # Update progress
            if job:
                job.current_step = 'Running automation script...'
                job.progress = 30
                db.session.commit()

            # Log the Docker command for debugging
            app.logger.info(f'Executing Docker command: {" ".join(docker_cmd)}')

            # Run the container
            process = subprocess.Popen(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            app.logger.info(f'Docker container started with PID: {process.pid}')
            
            # Monitor the process and capture output
            stdout_lines = []
            stderr_lines = []
            
            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stdout_lines.append(output.strip())
                    
                    # Update progress based on output
                    if job and 'login' in output.lower():
                        job.current_step = 'Logging in...'
                        job.progress = 40
                        db.session.commit()
                    elif job and '2fa' in output.lower():
                        job.current_step = 'Completing 2FA...'
                        job.progress = 50
                        db.session.commit()
                    elif job and 'publication' in output.lower():
                        job.current_step = 'Processing publications...'
                        job.progress = 60
                        # Try to extract publication name from output
                        job.last_publication = output.strip()[:255]
                        db.session.commit()
            
            # Get any remaining stderr
            stderr = process.stderr.read()
            if stderr:
                stderr_lines.append(stderr)
            
            # Wait for process to complete
            return_code = process.poll()

            # Log the result
            app.logger.info(f'Docker container exited with code: {return_code}')
            app.logger.info(f'STDOUT lines: {len(stdout_lines)}')
            app.logger.info(f'STDERR lines: {len(stderr_lines)}')
            if stderr_lines:
                app.logger.error(f'STDERR: {stderr_lines}')

            # Update final status
            if job:
                if return_code == 0:
                    job.status = 'completed'
                    job.progress = 100
                    job.current_step = 'Completed successfully!'
                    job.result = '\n'.join(stdout_lines)
                else:
                    job.status = 'failed'
                    job.error_message = '\n'.join(stderr_lines) if stderr_lines else 'Unknown error'

                db.session.commit()
            
            # Send Discord notification via n8n webhook
            if n8n_webhook:
                try:
                    notification_data = {
                        'user_id': user_id,
                        'status': job.status if job else 'unknown',
                        'language': language,
                        'completed_at': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    requests.post(n8n_webhook, json=notification_data, timeout=10)
                except Exception as e:
                    app.logger.error(f'Failed to send Discord notification: {str(e)}')
            
            return {
                'success': return_code == 0,
                'output': '\n'.join(stdout_lines),
                'errors': '\n'.join(stderr_lines) if stderr_lines else None
            }
            
        except Exception as e:
            # Update job status on error
            if job:
                job.status = 'failed'
                job.error_message = str(e)
                db.session.commit()
            raise
            
        finally:
            # CRITICAL: Clean up the temporary env file
            if temp_env_file and os.path.exists(temp_env_file.name):
                try:
                    os.unlink(temp_env_file.name)
                except Exception as e:
                    app.logger.error(f'Failed to delete temp env file: {str(e)}')
            
            # Clean up any remaining containers
            try:
                subprocess.run(
                    ['docker', 'rm', '-f', container_name],
                    capture_output=True,
                    timeout=30
                )
            except Exception as e:
                app.logger.error(f'Failed to clean up container: {str(e)}')


if __name__ == '__main__':
    """Allow running worker standalone."""
    print('Starting RQ worker...')
    print('Make sure Redis is running!')
    print('Press Ctrl+C to stop')
    
    from redis import Redis
    from rq import Worker, Queue
    import sys
    
    redis_conn = Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
    queue = Queue(connection=redis_conn)
    
    worker = Worker([queue], connection=redis_conn)
    worker.work()