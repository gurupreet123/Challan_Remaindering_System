from datetime import datetime
from bson import ObjectId
from twilio.rest import Client
from utils import is_valid_phone
from calls import trigger_call
from database import challans, call_logs, twilio_config
from database import provider_config

MAX_RETRIES = 3

# 🔴 UPDATE WHENEVER NGROK RESTARTS
NGROK_BASE_URL = "https://nonorthographic-overgrievously-rubi.ngrok-free.dev"

# ================= HELPERS =================
def is_valid_phone(phone: str) -> bool:
    phone = phone.strip()
    if phone.startswith("+91"):
        phone = phone[3:]
    return phone.isdigit() and len(phone) == 10

def classify_listen_status(duration: int):
    if duration < 5:
        return "declined"
    elif duration <= 15:
        return "partial"
    return "complete"

def serialize_mongo(cursor):
    data = []
    for d in cursor:
        d["_id"] = str(d["_id"])
        if "created_at" in d:
            d["created_at"] = d["created_at"].isoformat()
        if "updated_at" in d and d["updated_at"]:
            d["updated_at"] = d["updated_at"].isoformat()
        data.append(d)
    return data

# ======================================================
# PROVIDER-AWARE CALL ROUTER
# ======================================================
def trigger_call(phone: str, challan_id: str):
    config = provider_config.find_one()
    if not config:
        raise Exception("No call provider configured")

    provider = config.get("provider")

    if provider == "exotel":
        return trigger_exotel_call(phone, challan_id, config)

    if provider == "twilio":
        return trigger_twilio_call(phone, challan_id, config)

    if provider == "plivo":
        return trigger_plivo_call(phone, challan_id, config)

    raise Exception("Invalid provider selected")
    
# ================= PROVIDER IMPLEMENTATIONS =================
import requests

def trigger_exotel_call(phone, challan_id, config):
    """
    REAL Exotel outbound call
    """

    sid = config["sid"]
    api_key = config["api_key"]
    caller_id = config["caller_id"]

    url = f"https://api.exotel.com/v1/Accounts/{sid}/Calls/connect.json"

    payload = {
        "From": caller_id,
        "To": phone,
        "CallerId": caller_id,
        "Url": f"{NGROK_BASE_URL}/exotel/voice?challan_id={challan_id}",
        "StatusCallback": f"{NGROK_BASE_URL}/exotel/status?challan_id={challan_id}"
    }

    response = requests.post(
        url,
        data=payload,
        auth=(sid, api_key),
        timeout=10
    )

    print("📞 Exotel Response:", response.text)
    return response.status_code == 200


def trigger_twilio_call(phone, challan_id, config):
    print("📞 Twilio Call")
    print("To:", phone)
    print("From:", config.get("from"))
    return True


def trigger_plivo_call(phone, challan_id, config):
    print("📞 Plivo Call")
    print("To:", phone)
    print("Caller:", config.get("caller_id"))
    return True


# ================= TWILIO CLIENT =================
def get_twilio_client():
    config = twilio_config.find_one()
    if not config:
        raise Exception("Twilio config not set by admin")

    return (
        Client(config["account_sid"], config["auth_token"]),
        config["phone_number"]
    )

# ================= CREATE CHALLAN =================
from datetime import datetime

def create_challan(
    name,
    phone,
    language,
    challan_type,
    amount,
    last_date=None,
    late_fee_type=None,
    late_fee_amount=None
):
    # -----------------------------
    # VALIDATION
    # -----------------------------
    if not is_valid_phone(phone):
        return {"error": True, "message": "Invalid phone number"}

    if not challan_type:
        return {"error": True, "message": "Challan type is required"}

    # -----------------------------
    # CREATE CHALLAN DOCUMENT
    # -----------------------------
    challan = {
        "name": name.strip(),
        "phone": phone.strip(),
        "language": language,
        "challan_type": challan_type,          # ✅ EXACT USER INPUT
        "amount": int(amount),

        "last_date": last_date,
        "late_fee_type": late_fee_type,
        "late_fee_amount": late_fee_amount,

        # -----------------------------
        # CALL TRACKING FIELDS
        # -----------------------------
        "status": "pending",                   # pending / received
        "call_attempts": 0,
        "listen_status": None,                 # complete / partial / declined
        "last_duration": None,

        # -----------------------------
        # SYSTEM METADATA
        # -----------------------------
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # -----------------------------
    # INSERT INTO DB
    # -----------------------------
    result = challans.insert_one(challan)
    challan_id = str(result.inserted_id)

    # -----------------------------
    # TRIGGER CALL (ASYNC / SAFE)
    # -----------------------------
    try:
        trigger_call(phone, challan_id)
    except Exception as e:
        print("Call trigger failed:", e)

    # -----------------------------
    # RESPONSE
    # -----------------------------
    challan["_id"] = challan_id
    return challan

