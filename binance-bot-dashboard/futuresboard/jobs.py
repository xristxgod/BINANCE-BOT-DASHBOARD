from flask_apscheduler import APScheduler
from addition.sripts import debiting_funds, add_ref_info, is_min_balance

def register_scheduler(app):
    ''' Adding a subtask to run at a specific time '''
    scheduler = APScheduler()
    scheduler.init_app(app)
    # This script will start its work at 3:30 Moscow time
    scheduler.add_job(id='Add ref info', func=add_ref_info.main, trigger='cron', hour=23, minute=00)
    scheduler.add_job(id="Is min balance", func=is_min_balance.main, trigger="interval", seconds=1000)
    scheduler.add_job(id='Debiting funds', func=debiting_funds.main, trigger='cron', hour=23, minute=30)
    scheduler.start()