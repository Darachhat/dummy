import random

def mock_lookup(reference_number: str):
    customers = [
        "Cathainote Co., Ltd",
        "Sunrise Energy",
        "GreenFarm",
        "Apsara Telecom",
    ]
    amount = random.randint(5_000, 30_000)
    return {
        "reference_number": reference_number,
        "customer_name": random.choice(customers),
        "amount_cents": amount,
        "currency": "USD",
        "session_id": f"SESS-{reference_number[-6:]}"
    }

def cdc_lookup(reference_number: str, partner: str):
    return {
        "response_code": 200,
        "response_msg": "Success",
        "reference_number": reference_number,
        "customer_name": "Cathainote Co., Ltd",
        "amount": 23000000,
        "currency": "KHR",
        "session_id": f"SESS-{reference_number[-6:]}"
    }
