

def mock_lookup(reference_number: str):
   
    return {
        "reference_number": 2,
        "customer_name": "Cathainote Co., Ltd",
        "amount_cents": 10000,
        "currency": "USD",
        "session_id": f"SESS-{reference_number[-6:]}"
    }
