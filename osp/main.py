from fastapi import FastAPI, Header, Query, HTTPException
from datetime import datetime
import random, time
import os

# Load ENV 
OSP_VERSION = os.getenv("OSP_VERSION", "v1.0.0")
VALID_AUTH = os.getenv("OSP_AUTH_TOKEN", "Bearer token")
VALID_PARTNER = os.getenv("OSP_PARTNER", "DUMMYBANK")

app = FastAPI(title="One-Stop-Service Mock API", version=OSP_VERSION)

# Simulating data
FAKE_BILLS = {
    "00A0000000000": {"customer_name": "Cathainote Co., Ltd", "amount": 230, "currency": "USD","session_id":"SESS618112","acknowledgement_id":"AID195431","reversal_transaction_id":"RTID716618","reversal_acknowledgement_id":"RAID352360"},
    "00B0000000001": {"customer_name": "Darachhat Co., Ltd", "amount": 170, "currency": "USD","session_id":"SESS618113","acknowledgement_id":"AID195432","reversal_transaction_id":"RTID716619","reversal_acknowledgement_id":"RAID352361"},
}

# Utility functions
def simulate_latency(min_s=0.5, max_s=2.0): time.sleep(random.uniform(min_s, max_s))
def maybe_fail(chance=0.1): 
    if random.random() < chance:
        raise HTTPException(status_code=random.choice([400, 500]), detail="OSP temporary failure")

def validate_request(auth: str | None, partner: str | None):
    if not auth or not partner:
        raise HTTPException(status_code=401, detail="Missing authorization or partner")
    if auth != VALID_AUTH or partner != VALID_PARTNER:
        raise HTTPException(status_code=403, detail="Invalid authorization or partner")

# ---------------------- LOOKUP ----------------------
@app.get("/api/v1.0.0/query-payment")
def query_payment(
    authorization: str = Header(None),
    partner: str = Query(...),
    reference_number: str = Query(...),
):
    validate_request(authorization, partner)
    simulate_latency()
    maybe_fail(0.1)

    bill = FAKE_BILLS.get(reference_number)
    if not bill:
        raise HTTPException(status_code=404, detail="Reference not found")

    return {
        "response_code": 200,
        "response_msg": "Bill found",
        "reference_number": reference_number,
        "customer_name": bill["customer_name"],
        "amount": bill["amount"],
        "currency": bill["currency"],
        "attr_1_name": None,
        "attr_1_value": None,
        "attr_2_name": None,
        "attr_2_value": None,
        "session_id": bill["session_id"],
        "cdc_transaction_datetime": None,
        "acknowledgement_id": bill["acknowledgement_id"],
        "reversal_transaction_id": bill["reversal_transaction_id"],
        "reversal_acknowledgement_id": bill["reversal_acknowledgement_id"],
    }
    return {
        "response_code": 400,
        "response_msg": "Confirmation failed at OSP",
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "acknowledgement_id": acknowledgement_id,
        "reversal_transaction_id": f"RTID{random.randint(100000,999999)}",
        "reversal_acknowledgement_id": f"RAID{random.randint(100000,999999)}",
    }

# ---------------------- COMMIT ----------------------
@app.get("/api/v1.0.0/commit-payment")
def commit_payment(
    authorization: str = Header(None),
    partner: str = Query(...),
    reference_number: str = Query(...),
    session_id: str = Query(...),
    transaction_id: str = Query(...),
):
    validate_request(authorization, partner)
    simulate_latency()
    maybe_fail(0.1)

    bill = FAKE_BILLS.get(reference_number)
    if not bill:
        return {
            "response_code": 404,
            "response_msg": "Reference not found at OSP",
            "reference_number": reference_number,
            "transaction_id": transaction_id,
        }

    if random.random() > 0.15:
        return {
            "response_code": 200,
            "response_msg": "Commit successful",
            "reference_number": reference_number,
            "customer_name": bill["customer_name"],
            "amount": bill["amount"],
            "currency": bill["currency"],
            "session_id": session_id,
            "cdc_transaction_datetime": datetime.utcnow().isoformat(),
            "acknowledgement_id": f"AID{random.randint(100000,999999)}",
            "reversal_transaction_id": f"RTID{random.randint(100000,999999)}",
            "reversal_acknowledgement_id": f"RAID{random.randint(100000,999999)}",
        }

    return {
        "response_code": 400,
        "response_msg": "Commit failed at OSP",
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "acknowledgement_id": f"AID{random.randint(100000,999999)}",
        "reversal_transaction_id": f"RTID{random.randint(100000,999999)}",
        "reversal_acknowledgement_id": f"RAID{random.randint(100000,999999)}",
    }

# ---------------------- CONFIRM ----------------------
@app.get("/api/v1.0.0/confirm-payment")
def confirm_payment(
    authorization: str = Header(None),
    partner: str = Query(...),
    reference_number: str = Query(...),
    transaction_id: str = Query(...),
    acknowledgement_id: str = Query(...),
):
    validate_request(authorization, partner)
    simulate_latency()
    maybe_fail(0.1)

    bill = FAKE_BILLS.get(reference_number)
    if bill and random.random() > 0.2:
        return {
            "response_code": 200,
            "response_msg": "Confirmed successfully",
            "reference_number": reference_number,
            "customer_name": bill["customer_name"],
            "amount": bill["amount"],
            "currency": bill["currency"],
            "session_id": f"SESS{random.randint(100000,999999)}",
            "cdc_transaction_datetime": datetime.utcnow().isoformat(),
            "acknowledgement_id": acknowledgement_id,
            "reversal_transaction_id": f"RTID{random.randint(100000,999999)}",
            "reversal_acknowledgement_id": f"RAID{random.randint(100000,999999)}",
        }

    return {
        "response_code": 400,
        "response_msg": "Confirmation failed at OSP",
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "acknowledgement_id": acknowledgement_id,
    }

# ---------------------- REVERSE ----------------------
@app.get("/api/v1.0.0/reverse-payment")
def reverse_payment(
    authorization: str = Header(None),
    partner: str = Query(...),
    reference_number: str = Query(...),
    transaction_id: str = Query(...),
    reversal_transaction_id: str = Query(...),
):
    validate_request(authorization, partner)
    simulate_latency()
    maybe_fail(0.1)

    bill = FAKE_BILLS.get(reference_number)
    if not bill:
        return {
            "response_code": 404,
            "response_msg": "Reference not found at OSP",
            "reference_number": reference_number,
            "transaction_id": transaction_id,
            "reversal_transaction_id": reversal_transaction_id,
            "reversal_acknowledgement_id": None,
        }

    if random.random() > 0.2:
        return {
            "response_code": 200,
            "response_msg": "Reversal successful",
            "reference_number": reference_number,
            "customer_name": bill["customer_name"],
            "amount": bill["amount"],
            "currency": bill["currency"],
            "session_id": f"SESS{random.randint(100000,999999)}",
            "cdc_transaction_datetime": datetime.utcnow().isoformat(),
            "acknowledgement_id": f"AID{random.randint(100000,999999)}",
            "reversal_transaction_id": reversal_transaction_id,
            "reversal_acknowledgement_id": f"RAID{random.randint(100000,999999)}",
        }

    return {
        "response_code": 400,
        "response_msg": "Reversal failed at OSP",
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "acknowledgement_id": f"AID{random.randint(100000,999999)}",
        "reversal_transaction_id": reversal_transaction_id,
        "reversal_acknowledgement_id": f"RAID{random.randint(100000,999999)}",
    }

# ---------------------- RUN ----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9000)
