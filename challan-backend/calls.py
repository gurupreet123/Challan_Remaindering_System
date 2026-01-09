import requests
from database import provider_config

def trigger_call(phone: str, challan_id: str):
    config = provider_config.find_one({"active": True})

    if not config:
        print("❌ No active provider configured")
        return

    provider = config["provider"]
    creds = config["credentials"]

    if provider == "twilio":
        trigger_twilio(phone, challan_id, creds)
    elif provider == "exotel":
        trigger_exotel(phone, challan_id, creds)
    elif provider == "plivo":
        trigger_plivo(phone, challan_id, creds)

# ---------------- TWILIO ----------------
from twilio.rest import Client

def trigger_twilio(phone, challan_id, c):
    client = Client(c["account_sid"], c["auth_token"])

    call = client.calls.create(
        to=f"+91{phone}",
        from_=c["phone_number"],
        url=f"https://nonorthographic-overgrievously-rubi.ngrok-free.dev/twilio/voice?challan_id={challan_id}",
        status_callback=f"https://nonorthographic-overgrievously-rubi.ngrok-free.dev/twilio/status?challan_id={challan_id}",
        status_callback_event=["completed"]
    )

    print("📞 TWILIO CALL SID:", call.sid)

# ---------------- EXOTEL ----------------
import requests

def trigger_exotel(phone, challan_id, c):
    """
    REAL Exotel call trigger
    """
    ACCOUNT_SID = c["account_sid"]
    API_KEY = c["api_key"]
    API_TOKEN = c["api_token"]
    EXOPHONE = c["exophone"]

    url = f"https://api.exotel.com/v1/Accounts/{ACCOUNT_SID}/Calls/connect.json"

    payload = {
        "From": phone,  # 10-digit number
        "To": phone,
        "CallerId": EXOPHONE,
        "Url": f" https://nonorthographic-overgrievously-rubi.ngrok-free.dev/twilio/voice?challan_id={challan_id}",
        "StatusCallback": f" https://nonorthographic-overgrievously-rubi.ngrok-free.dev/twilio/status?challan_id={challan_id}"
    }

    response = requests.post(
        url,
        data=payload,
        auth=(API_KEY, API_TOKEN)
    )

    print("📞 EXOTEL RESPONSE:", response.status_code, response.text)

# ---------------- PLIVO ----------------
def trigger_plivo(phone, challan_id, c):
    print(f"📞 PLIVO call to {phone} | challan={challan_id}")
