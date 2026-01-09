from fastapi import FastAPI, Request, Response, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from bson import ObjectId
from twilio.twiml.voice_response import VoiceResponse

from services import (
    create_challan,
    serialize_mongo,
    classify_listen_status,
)
from database import challans, call_logs, provider_config
from models import ChallanCreate
from scheduler import start_scheduler

# ================= SECURITY =================
def verify_admin(x_admin_key: str = Header(...)):
    if x_admin_key != "MH-GOV-SECURE-KEY":
        raise HTTPException(status_code=401, detail="Unauthorized")

# ================= APP =================
app = FastAPI(title="Challan Reminder System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    start_scheduler()

# ======================================================
# CREATE CHALLAN (SECURED)
# ======================================================
@app.post("/challan")
def add_challan(
    data: ChallanCreate,
    auth=Depends(verify_admin)
):
    payload = data.dict()

    payload["late_fee_amount"] = payload.pop("late_fee")
    payload["last_date"] = datetime.combine(
        payload["last_date"],
        datetime.min.time()
    )

    return create_challan(**payload)

# ======================================================
# FETCH CHALLANS
# ======================================================
@app.get("/challans")
def get_challans():
    result = []

    for challan in challans.find().sort("created_at", -1):
        challan_id = challan["_id"]

        logs = list(
            call_logs.find({"challan_id": challan_id})
            .sort("call_time", -1)
        )

        attempts = len(logs)

        if attempts == 0:
            challan.update({
                "status": "pending",
                "call_attempts": 0,
                "last_duration": None,
                "listen_status": "waiting",
            })
        else:
            last = logs[0]
            duration = int(last.get("call_duration", 0))

            challan.update({
                "status": "received",
                "call_attempts": attempts,
                "last_duration": duration,
                "listen_status": classify_listen_status(duration),
            })

        result.append(challan)

    return serialize_mongo(result)

# ======================================================
# TWILIO VOICE
# ======================================================
@app.post("/twilio/voice")
async def twilio_voice(request: Request):
    challan_id = request.query_params.get("challan_id")
    r = VoiceResponse()

    if not challan_id:
        r.say("Invalid challan.")
        return Response(str(r), media_type="application/xml")

    challan = challans.find_one({"_id": ObjectId(challan_id)})
    if not challan:
        r.say("Invalid challan.")
        return Response(str(r), media_type="application/xml")

    due = challan["last_date"].strftime("%d %B %Y")
    r.say(
        f"Hello {challan['name']}. "
        f"Your challan for {challan['challan_type']} "
        f"is {challan['amount']} rupees. "
        f"Please pay it by {due}. Thank you.",
        language="en-IN",
    )

    return Response(str(r), media_type="application/xml")

# ======================================================
# TWILIO STATUS CALLBACK
# ======================================================
@app.post("/twilio/status")
async def twilio_status(request: Request):
    challan_id = request.query_params.get("challan_id")
    data = await request.form()

    if challan_id:
        call_logs.insert_one({
            "challan_id": ObjectId(challan_id),
            "call_time": datetime.utcnow(),
            "call_duration": int(data.get("CallDuration", 0)),
            "listen_status": classify_listen_status(
                int(data.get("CallDuration", 0))
            ),
        })

    return {"status": "logged"}

# ======================================================
# CALL PROVIDER CONFIG (SINGLE SOURCE OF TRUTH)
# ======================================================
@app.post("/admin/provider-config")
def save_provider_config(
    data: dict,
    auth=Depends(verify_admin)
):
    if "provider" not in data or "credentials" not in data:
        raise HTTPException(400, "provider & credentials required")

    provider_config.update_one(
        {"provider": data["provider"]},
        {
            "$set": {
                "provider": data["provider"],
                "credentials": data["credentials"],
                "active": True,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    provider_config.update_many(
        {"provider": {"$ne": data["provider"]}},
        {"$set": {"active": False}}
    )

    return {"message": f"{data['provider']} activated"}

# ======================================================
# EXOTEL VOICE
# ======================================================
@app.post("/exotel/voice")
async def exotel_voice(request: Request):
    challan_id = request.query_params.get("challan_id")

    if not challan_id:
        return Response("<Response><Say>Invalid challan</Say></Response>",
                        media_type="application/xml")

    challan = challans.find_one({"_id": ObjectId(challan_id)})
    if not challan:
        return Response("<Response><Say>Invalid challan</Say></Response>",
                        media_type="application/xml")

    message = (
        f"Hello {challan['name']}. "
        f"You have a traffic challan of {challan['amount']} rupees "
        f"for {challan['challan_type']}. "
        f"Please pay before "
        f"{challan['last_date'].strftime('%d %B %Y')}. Thank you."
    )

    return Response(
        f"<Response><Say>{message}</Say></Response>",
        media_type="application/xml"
    )

# ======================================================
# EXOTEL STATUS CALLBACK
# ======================================================
@app.post("/exotel/status")
async def exotel_status(request: Request):
    challan_id = request.query_params.get("challan_id")
    data = await request.form()

    if challan_id:
        call_logs.insert_one({
            "challan_id": ObjectId(challan_id),
            "call_time": datetime.utcnow(),
            "call_duration": int(data.get("DialDuration", 0)),
            "listen_status": classify_listen_status(
                int(data.get("DialDuration", 0))
            ),
        })

    return {"status": "logged"}
