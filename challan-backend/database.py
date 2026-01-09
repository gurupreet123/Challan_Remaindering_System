from pymongo import MongoClient

# ================= MONGO CONNECTION =================
MONGO_URI = "mongodb+srv://gurupreetdhande20_db_user:wCYCbbr095tJTTzV@cluster0.ui3npux.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)

db = client["challan_system"]

# ================= COLLECTIONS =================
challans = db["challans"]
call_logs = db["call_logs"]
twilio_config = db["twilio_config"]
provider_config = db["provider_config"]

print("🔥 MongoDB connected to:", client.address)
print("🔥 Database name:", db.name)
