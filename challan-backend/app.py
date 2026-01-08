from fastapi import FastAPI, Request, Response, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from bson import ObjectId
from twilio.twiml.voice_response import VoiceResponse
import csv, io

from services import (
    create_challan,
    serialize_mongo,
    classify_listen_status,
)
from database import challans, call_logs, twilio_config
from models import ChallanCreate
from scheduler import start_scheduler

app = FastAPI(title="Challan Reminder System")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= STARTUP =================
@app.on_event("startup")
def startup():
    start_scheduler()

# ======================================================
# CREATE SINGLE CHALLAN
# ======================================================
@app.post("/challan")
def add_challan(data: ChallanCreate):
    payload = data.dict()

    # frontend late_fee → backend late_fee_amount
    payload["late_fee_amount"] = payload.pop("late_fee")

    # date → datetime (MongoDB compatible)
    payload["last_date"] = datetime.combine(
        payload["last_date"],
        datetime.min.time()
    )

    return create_challan(**payload)

# ======================================================
# FETCH CHALLANS (STATUS = RECEIVED)
# ======================================================
@app.get("/challans")
def get_challans():
    result = []

    cursor = challans.find().sort("created_at", -1)

    for challan in cursor:
        challan_id = challan["_id"]

        logs = list(
            call_logs.find({"challan_id": challan_id})
            .sort("call_time", -1)
        )

        attempts = len(logs)

        if attempts == 0:
            challan["status"] = "pending"
            challan["call_attempts"] = 0
            challan["last_duration"] = None
            challan["listen_status"] = "waiting"
        else:
            last_call = logs[0]
            duration = int(last_call.get("call_duration", 0))

            challan["status"] = "received"
            challan["call_attempts"] = attempts
            challan["last_duration"] = duration
            challan["listen_status"] = classify_listen_status(duration)

        # ✅ EXACT user-entered type (no fake default)
        challan["challan_type"] = challan.get("challan_type")

        result.append(challan)

    # ✅ serialize ONLY ONCE (after loop)
    return serialize_mongo(result)

# ======================================================
# TWILIO VOICE (FULL MESSAGE – NO CUT)
# ======================================================
@app.post("/twilio/voice")
async def twilio_voice(request: Request):
    challan_id = request.query_params.get("challan_id")

    r = VoiceResponse()

    if not challan_id:
        r.say("Invalid challan.", voice="alice")
        return Response(str(r), media_type="application/xml")

    challan = challans.find_one({"_id": ObjectId(challan_id)})
    if not challan:
        r.say("Invalid challan.", voice="alice")
        return Response(str(r), media_type="application/xml")

    name = challan["name"]
    challan_type = challan["challan_type"]
    amount = challan["amount"]
    due = challan["last_date"].strftime("%d %B %Y")
    language = challan["language"]
    late_fee_type = challan["late_fee_type"]
    late_fee_amount = challan["late_fee_amount"]

    late_fee_text = (
        f"{late_fee_amount} rupees per day"
        if late_fee_type.lower() == "per day"
        else f"{late_fee_amount} rupees"
    )

    # 🗣 FULL MESSAGE
    if language == "hindi":
        r.say(
            f"नमस्ते {name}. "
            f"आपके नाम पर {challan_type} का {amount} रुपये का चालान है। "
            f"कृपया {due} तक भुगतान करें। "
            f"अन्यथा {late_fee_text} का विलंब शुल्क लगेगा।",
            voice="Polly.Aditi",
            language="hi-IN",
        )
        r.pause(length=1)
        r.say("धन्यवाद।", voice="Polly.Aditi", language="hi-IN")

    elif language == "marathi":
        r.say(
            f"नमस्कार {name}. "
            f"तुमच्या नावावर {challan_type} साठी {amount} रुपयांचे चलन आहे. "
            f"कृपया {due} पर्यंत भरणा करा. "
            f"नाहीतर {late_fee_text} उशीर शुल्क लागेल.",
            voice="Polly.Aditi",
            language="mr-IN",
        )
        r.pause(length=1)
        r.say("धन्यवाद.", voice="Polly.Aditi", language="mr-IN")

    else:
        r.say(
            f"Hello {name}. "
            f"Your challan for {challan_type} is {amount} rupees. "
            f"Please pay it by {due}. "
            f"Late fee of {late_fee_text} will apply.",
            voice="alice",
            language="en-IN",
        )
        r.pause(length=1)
        r.say("Thank you.", voice="alice", language="en-IN")

    return Response(str(r), media_type="application/xml")

# ======================================================
# TWILIO STATUS CALLBACK
# ======================================================
@app.post("/twilio/status")
async def twilio_status(request: Request):
    challan_id = request.query_params.get("challan_id")
    data = await request.form()

    duration = int(data.get("CallDuration", 0))

    if challan_id:
        call_logs.insert_one({
            "challan_id": ObjectId(challan_id),
            "call_time": datetime.utcnow(),
            "call_duration": duration,
            "listen_status": classify_listen_status(duration),
        })

    return {"status": "logged"}

# ======================================================
# ADMIN: SAVE TWILIO CONFIG
# ======================================================
@app.post("/admin/twilio-config")
def save_twilio_config(data: dict):
    required = ["account_sid", "auth_token", "phone_number"]
    for r in required:
        if r not in data:
            raise HTTPException(400, f"Missing field: {r}")

    twilio_config.delete_many({})
    twilio_config.insert_one({
        "account_sid": data["account_sid"],
        "auth_token": data["auth_token"],
        "phone_number": data["phone_number"],
        "updated_at": datetime.utcnow()
    })

    return {"message": "Twilio configuration saved successfully"}

from database import provider_config

@app.post("/admin/twilio-config")
def save_twilio_config(data: dict):
    provider_config.update_one(
        {"provider": "twilio"},
        {
            "$set": {
                "provider": "twilio",
                "credentials": data,
                "active": True,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    provider_config.update_many(
        {"provider": {"$ne": "twilio"}},
        {"$set": {"active": False}}
    )
    return {"message": "Twilio activated"}

@app.post("/admin/exotel-config")
def save_exotel_config(data: dict):
    provider_config.update_one(
        {"provider": "exotel"},
        {
            "$set": {
                "provider": "exotel",
                "credentials": data,
                "active": True,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    provider_config.update_many(
        {"provider": {"$ne": "exotel"}},
        {"$set": {"active": False}}
    )
    return {"message": "Exotel activated"}

@app.post("/admin/plivo-config")
def save_plivo_config(data: dict):
    provider_config.update_one(
        {"provider": "plivo"},
        {
            "$set": {
                "provider": "plivo",
                "credentials": data,
                "active": True,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    provider_config.update_many(
        {"provider": {"$ne": "plivo"}},
        {"$set": {"active": False}}
    )
    return {"message": "Plivo activated"}
# ======================================================
# ADMIN: SAVE CALL PROVIDER CONFIG (TWILIO / EXOTEL / PLIVO)
# ======================================================
@app.post("/admin/provider-config")
def save_provider_config(data: dict):
    required = ["provider"]
    for r in required:
        if r not in data:
            raise HTTPException(400, f"Missing field: {r}")

    # clear old config
    provider_config.delete_many({})

    provider_config.insert_one({
        **data,
        "updated_at": datetime.utcnow()
    })

    return {
        "message": "Provider configuration saved",
        "active_provider": data["provider"]
    }
# ======================================================
# EXOTEL VOICE XML
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
        f"Please pay before {challan['last_date'].strftime('%d %B %Y')}. "
        f"Thank you."
    )

    xml = f"""
    <Response>
        <Say voice="female">{message}</Say>
    </Response>
    """

    return Response(xml, media_type="application/xml")
# ======================================================
# EXOTEL STATUS CALLBACK
# ======================================================
@app.post("/exotel/status")
async def exotel_status(request: Request):
    challan_id = request.query_params.get("challan_id")
    data = await request.form()

    duration = int(data.get("DialDuration", 0))

    if challan_id:
        call_logs.insert_one({
            "challan_id": ObjectId(challan_id),
            "call_time": datetime.utcnow(),
            "call_duration": duration,
            "listen_status": classify_listen_status(duration),
        })

    return {"status": "logged"}

