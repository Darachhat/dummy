from pydantic import BaseModel
from typing import List
from .account import AccountOut


class MeOut(BaseModel):
    user: dict
    total_balance_cents: int
    accounts: List[AccountOut]