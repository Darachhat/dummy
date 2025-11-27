import logging
import asyncio
from fastapi import HTTPException
from sqlalchemy.orm import Session
from services.osp_client import osp_lookup, osp_commit, osp_confirm, osp_reverse
from models.payment import Payment

from loguru import logger

async def osp_full_payment_flow(payment: Payment, db: Session):
    """CDC Flow: Lookup → Commit → Confirm → Reverse (if confirm fails)"""

    ref_no = payment.reference_number
    tx_id = f"TID{payment.id:06d}"
    logger.info(f"[OSP][FLOW] Start Ref={ref_no}, TX={tx_id}")

    # 1. Lookup
    try:
        lookup_res = await osp_lookup(ref_no)
        payment.session_id = lookup_res.get("session_id")
        db.commit()
        logger.info(f"[OSP][LOOKUP][OK] {lookup_res}")
    except Exception as e:
        logger.error(f"[OSP][LOOKUP][FAIL] {str(e)}")
        raise HTTPException(status_code=400, detail="CDC lookup failed")

    # 2. Commit
    try:
        commit_res = await osp_commit(ref_no, payment.session_id, tx_id)
        payment.acknowledgement_id = commit_res.get("acknowledgement_id")
        payment.cdc_transaction_datetime = commit_res.get("cdc_transaction_datetime")
        payment.status = "committed"
        db.commit()
        logger.info(f"[OSP][COMMIT][OK] {commit_res}")
    except Exception as e:
        logger.error(f"[OSP][COMMIT][FAIL] {str(e)}")
        payment.status = "commit_failed"
        db.commit()
        raise HTTPException(status_code=400, detail="CDC commit-payment failed")

    # 3. Confirm (retry x3)
    confirm_success = False
    for attempt in range(3):
        try:
            confirm_res = await osp_confirm(ref_no, tx_id, payment.acknowledgement_id)
            payment.status = "confirmed"
            db.commit()
            logger.info(f"[OSP][CONFIRM][OK][Try {attempt+1}] {confirm_res}")
            confirm_success = True
            break
        except Exception as e:
            logger.warning(f"[OSP][CONFIRM][FAIL][Try {attempt+1}] {str(e)}")
            if attempt < 2:
                await asyncio.sleep(2)

    # 4. Reverse if confirm failed
    if not confirm_success:
        logger.warning("[OSP][CONFIRM][FAIL] → Starting Reverse flow")
        reverse_success = False

        for attempt in range(3):
            try:
                reversal_transaction_id = f"REV-{tx_id}"
                reverse_res = await osp_reverse(ref_no, tx_id, reversal_transaction_id)
                payment.reversal_transaction_id = reversal_transaction_id
                payment.reversal_acknowledgement_id = reverse_res.get("reversal_acknowledgement_id")
                payment.status = "reversed"
                db.commit()
                logger.info(f"[OSP][REVERSE][OK][Try {attempt+1}] {reverse_res}")
                reverse_success = True
                break
            except Exception as e:
                logger.warning(f"[OSP][REVERSE][FAIL][Try {attempt+1}] {str(e)}")
                if attempt < 2:
                    await asyncio.sleep(2)

        if not reverse_success:
            logger.error("[OSP][REVERSE][FAIL] → Manual reconciliation required")
            payment.status = "reversal_failed"
            db.commit()
            raise HTTPException(
                status_code=500,
                detail="CDC confirm failed and reversal unsuccessful. Manual reconciliation required.",
            )

        raise HTTPException(status_code=500, detail="CDC confirm failed. Payment reversed successfully.")

    logger.info(f"[OSP][FLOW][SUCCESS] Payment Ref={ref_no} Confirmed")
    return {
        "status": "confirmed",
        "reference_number": ref_no,
        "acknowledgement_id": payment.acknowledgement_id,
        "cdc_transaction_datetime": payment.cdc_transaction_datetime,
    }
