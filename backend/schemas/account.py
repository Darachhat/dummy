from pydantic import BaseModel


class AccountOut(BaseModel):
    id: int
    name: str
    number: str
    balance_cents: int
    currency: str


    class Config:
        from_attributes = True