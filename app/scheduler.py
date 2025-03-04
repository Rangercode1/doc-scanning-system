from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app import db
from app.models.user import User
from flask import current_app

def reset_all_users_credits():
    """Reset credits for all users at noon"""
    with current_app.app_context():
        users = User.query.all()
        for user in users:
            if not user.is_admin:  # Don't reset admin credits
                user.credits = current_app.config['DAILY_FREE_CREDITS']
                user.last_credit_reset = datetime.utcnow()
        db.session.commit()
        print(f"Credits reset for all users at {datetime.utcnow()}")

def init_scheduler(app):
    """Initialize the scheduler with the credit reset job"""
    scheduler = BackgroundScheduler()
    
    # Schedule credit reset at 12 PM (noon) every day
    scheduler.add_job(
        reset_all_users_credits,
        trigger=CronTrigger(hour=12, minute=0),
        id='credit_reset_job',
        name='Reset user credits daily at noon',
        replace_existing=True
    )
    
    scheduler.start()
    return scheduler 