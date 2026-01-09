from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from database import challans, call_logs
from calls import trigger_call
from config import MAX_RETRIES
from services import trigger_call

scheduler = BackgroundScheduler()

def retry_failed_calls():
    hour = datetime.now().hour
    if hour < 12 or hour >= 18:
        return

    for challan in challans.find():
        logs = list(call_logs.find(
            {"challan_id": challan["_id"]},
            sort=[("call_time", -1)]
        ))

        attempts = len(logs)
        if attempts >= MAX_RETRIES:
            continue

        if logs and logs[0].get("listen_status") in ["declined", "partial"]:
            trigger_call(
                challan["phone"],
                str(challan["_id"])
            )

def start_scheduler():
    scheduler.add_job(retry_failed_calls, "interval", hours=2)
    scheduler.start()
