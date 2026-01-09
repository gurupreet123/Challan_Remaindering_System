from pydantic import BaseModel
from datetime import datetime

class ChallanCreate(BaseModel):
    name: str
    phone: str
    language: str
    challan_type: str
    amount: int
    last_date: datetime
    late_fee_type: str   
    late_fee_amount: int
