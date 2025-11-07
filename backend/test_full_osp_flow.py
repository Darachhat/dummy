import httpx
import json

BASE_URL = "http://10.255.1.206:3001/api/v1.0.0"
PARTNER = "DUMMYBANK"
AUTH = "Basic RFVNTVlCQU5LOlBFNmM3ZVBaNndGSA=="  # <-- replace with settings.OSP_AUTH value

REFERENCE = "25Q5840989540"  # <-- put an unpaid reference number here
TRANSACTION_ID = "000099"     # <-- make sure this is unique

headers = {
    "Authorization": AUTH,
    "Content-Type": "application/x-www-form-urlencoded"
}


async def test_full_flow():
    async with httpx.AsyncClient(timeout=30) as client:
        # 1️⃣ Lookup
        print("---- STEP 1: Lookup ----")
        params = {"reference_number": REFERENCE, "partner": PARTNER}
        lookup = await client.get(f"{BASE_URL}/query-payment", params=params, headers=headers)
        print(lookup.status_code, lookup.text)

        if lookup.status_code != 200:
            print("❌ Lookup failed, stopping test.")
            return

        lookup_data = lookup.json()
        session_id = lookup_data.get("session_id")
        print(f"✅ Session ID: {session_id}")

        # 2️⃣ Commit
        print("\n---- STEP 2: Commit ----")
        data = {
            "reference_number": REFERENCE,
            "session_id": session_id,
            "transaction_id": TRANSACTION_ID,
            "partner": PARTNER,
        }
        commit = await client.post(f"{BASE_URL}/commit-payment", data=data, headers=headers)
        print(commit.status_code, commit.text)

        if commit.status_code != 200:
            print("❌ Commit failed — check 'Invalid data validation' again.")
            return

        commit_data = commit.json()
        ack_id = commit_data.get("acknowledgement_id")
        print(f"✅ Acknowledgement ID: {ack_id}")

        # 3️⃣ Confirm
        print("\n---- STEP 3: Confirm ----")
        data = {
            "reference_number": REFERENCE,
            "transaction_id": TRANSACTION_ID,
            "acknowledgement_id": ack_id,
            "partner": PARTNER,
        }
        confirm = await client.post(f"{BASE_URL}/confirm-payment", data=data, headers=headers)
        print(confirm.status_code, confirm.text)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_full_flow())
