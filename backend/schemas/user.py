from pydantic import BaseModel
from typing import List
from .account import AccountOut
from decimal import Decimal


class MeOut(BaseModel):
    user: dict
    total_balance: Decimal
    accounts: List[AccountOut]