def is_valid_phone(phone: str) -> bool:
    phone = phone.strip()
    return phone.isdigit() and len(phone) == 10
