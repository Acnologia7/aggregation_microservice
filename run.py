import atexit, zoneinfo

from datetime import datetime

from app.views import create_flask_app_with_bp
from app.tasks import periodic_update_token, periodic_update_offers_task
from app.models import db

flask_app, sched = create_flask_app_with_bp()

with flask_app.app_context():
    db.create_all()
    print("Database created successfully.")

sched.add_job(id='task3', func=periodic_update_token, next_run_time=datetime.now(zoneinfo.ZoneInfo('Europe/Prague')))
sched.add_job(id='task2', func=periodic_update_token, trigger='interval', minutes=5)
sched.add_job(id='task1', func=periodic_update_offers_task, trigger='interval', seconds=330)
sched.start()

atexit.register(lambda: sched.shutdown())

if __name__=='__main__':
    flask_app.run(debug=False)
