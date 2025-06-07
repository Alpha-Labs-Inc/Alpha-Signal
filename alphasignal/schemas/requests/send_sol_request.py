from pydantic import BaseModel


class SendSolRequest(BaseModel):
    destination: str
    amt: float
